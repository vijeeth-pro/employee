import os
import io
import math
import logging
import requests
from typing import List, Dict, Any, Tuple
import pypdf

from app.core.config import settings

logger = logging.getLogger("rag_service")

# Local fallback in-memory vector store if Pinecone is unconfigured/offline
_LOCAL_VECTOR_STORE: List[Dict[str, Any]] = []

def extract_text_from_file(file_bytes: bytes, filename: str) -> str:
    """Extract raw text from PDF, TXT, or MD file bytes."""
    filename_lower = filename.lower()
    if filename_lower.endswith(".pdf"):
        try:
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            text_pages = [page.extract_text() or "" for page in reader.pages]
            return "\n\n".join(text_pages)
        except Exception as e:
            logger.error(f"Failed to extract text from PDF {filename}: {e}")
            raise ValueError(f"Failed to parse PDF document: {str(e)}")
    else:
        # Default text/markdown processing
        try:
            return file_bytes.decode("utf-8", errors="replace")
        except Exception as e:
            raise ValueError(f"Failed to read text document: {str(e)}")

def chunk_text(text: str, chunk_size: int = 700, chunk_overlap: int = 120, category: str = "General Policy") -> List[str]:
    """
    Optimized Recursive Semantic Chunker:
    Splits text on natural structural boundaries (paragraphs, section headers, sentence periods)
    rather than arbitrary character cuts, keeping complete policy rules intact.
    """
    if not text or not text.strip():
        return []

    # First split into paragraphs / sections
    raw_paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    if not raw_paragraphs:
        raw_paragraphs = [text.strip()]

    chunks = []
    current_chunk = ""

    for paragraph in raw_paragraphs:
        # If adding paragraph fits within chunk_size, append it
        if len(current_chunk) + len(paragraph) + 2 <= chunk_size:
            current_chunk = f"{current_chunk}\n\n{paragraph}".strip()
        else:
            if current_chunk:
                chunks.append(current_chunk)
            
            # If paragraph itself is larger than chunk_size, split by sentences
            if len(paragraph) > chunk_size:
                sentences = paragraph.replace(". ", ".\n").split("\n")
                sub_chunk = ""
                for sent in sentences:
                    if len(sub_chunk) + len(sent) + 1 <= chunk_size:
                        sub_chunk = f"{sub_chunk} {sent}".strip()
                    else:
                        if sub_chunk:
                            chunks.append(sub_chunk)
                        sub_chunk = sent
                if sub_chunk:
                    current_chunk = sub_chunk
            else:
                current_chunk = paragraph

    if current_chunk:
        chunks.append(current_chunk)

    # Prefix each chunk with category context for richer embedding representation
    contextual_chunks = [
        f"[{category}] {c}" if not c.startswith("[") else c
        for c in chunks
    ]

    return contextual_chunks

def _fallback_dummy_embedding(text: str, dim: int = 768) -> List[float]:
    """Generates a deterministic normalized pseudo-embedding for local fallback."""
    vec = [0.0] * dim
    for i, char in enumerate(text[:300]):
        idx = (ord(char) * 17 + i * 31) % dim
        vec[idx] += 1.0
    
    norm = math.sqrt(sum(v * v for v in vec)) or 1.0
    return [v / norm for v in vec]

def generate_embedding(text: str, task_type: str = "RETRIEVAL_DOCUMENT") -> List[float]:
    """
    Generates a 768-dim float vector embedding via Google Gemini Embedding API.
    Uses 'taskType' (RETRIEVAL_DOCUMENT vs RETRIEVAL_QUERY) for optimal semantic retrieval accuracy.
    """
    gemini_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        return _fallback_dummy_embedding(text)

    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={gemini_key}"
        payload = {
            "model": "models/gemini-embedding-001",
            "content": {"parts": [{"text": text}]},
            "taskType": task_type,
            "outputDimensionality": 768
        }
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            data = res.json()
            return data["embedding"]["values"]
        else:
            logger.warning(f"Gemini embedding API returned status {res.status_code}: {res.text}")
    except Exception as e:
        logger.error(f"Gemini embedding exception: {e}")

    return _fallback_dummy_embedding(text)

_PINECONE_INDEX_CACHE = None

def _get_pinecone_index():
    """Returns cached Pinecone Index object if configured and reachable, else None."""
    global _PINECONE_INDEX_CACHE
    if _PINECONE_INDEX_CACHE is not None:
        return _PINECONE_INDEX_CACHE

    pinecone_key = settings.PINECONE_API_KEY or os.getenv("PINECONE_API_KEY")
    if not pinecone_key:
        return None

    try:
        from pinecone import Pinecone, ServerlessSpec
        pc = Pinecone(api_key=pinecone_key)
        index_name = settings.PINECONE_INDEX_NAME or "workforce-policy-index"
        
        # Create index if it does not exist
        existing_indices = [idx.name for idx in pc.list_indexes()]
        if index_name not in existing_indices:
            pc.create_index(
                name=index_name,
                dimension=768,
                metric="cosine",
                spec=ServerlessSpec(cloud="aws", region="us-east-1")
            )
        
        _PINECONE_INDEX_CACHE = pc.Index(index_name)
        return _PINECONE_INDEX_CACHE
    except Exception as e:
        logger.warning(f"Pinecone connection exception: {e}")
        return None

def upsert_chunks_to_vector_db(
    doc_id: int,
    title: str,
    chunks: List[str],
    company_id: int = None,
    vendor_company_id: int = None,
    category: str = "General Policy"
):
    """Generates embeddings and upserts chunks to Pinecone (or local fallback store)."""
    index = _get_pinecone_index()

    vectors_to_upsert = []
    for idx, chunk_str in enumerate(chunks):
        embedding = generate_embedding(chunk_str, task_type="RETRIEVAL_DOCUMENT")
        vector_id = f"doc_{doc_id}_chunk_{idx}"
        metadata = {
            "doc_id": doc_id,
            "title": title,
            "category": category,
            "chunk_index": idx,
            "chunk_text": chunk_str,
            "company_id": company_id if company_id is not None else 0,
            "vendor_company_id": vendor_company_id if vendor_company_id is not None else 0
        }

        if index:
            vectors_to_upsert.append((vector_id, embedding, metadata))
        else:
            # Local fallback store
            _LOCAL_VECTOR_STORE.append({
                "id": vector_id,
                "values": embedding,
                "metadata": metadata
            })

    if index and vectors_to_upsert:
        # Upsert in batches of 50
        batch_size = 50
        for i in range(0, len(vectors_to_upsert), batch_size):
            index.upsert(vectors=vectors_to_upsert[i:i + batch_size])

def query_relevant_chunks(
    query_text: str,
    company_id: int = None,
    vendor_company_id: int = None,
    top_k: int = 4
) -> List[Dict[str, Any]]:
    """
    Performs similarity search in Pinecone filtered by company_id / vendor_company_id.
    """
    query_vec = generate_embedding(query_text, task_type="RETRIEVAL_QUERY")
    index = _get_pinecone_index()

    matched_results = []

    if index:
        filter_dict = {}
        if company_id is not None:
            filter_dict["company_id"] = {"$in": [company_id, 0]}
        elif vendor_company_id is not None:
            filter_dict["vendor_company_id"] = {"$in": [vendor_company_id, 0]}

        try:
            res = index.query(
                vector=query_vec,
                top_k=top_k,
                include_metadata=True,
                filter=filter_dict if filter_dict else None
            )

            for match in res.get("matches", []):
                meta = match.get("metadata", {})
                matched_results.append({
                    "title": meta.get("title", "Policy Document"),
                    "category": meta.get("category", "General"),
                    "chunk_text": meta.get("chunk_text", ""),
                    "score": round(float(match.get("score", 0.0)), 3)
                })
            return matched_results
        except Exception as e:
            logger.warning(f"Pinecone query exception: {e}")

    # Fallback search on local vector store using Cosine Similarity
    def cosine_similarity(v1, v2):
        dot = sum(a * b for a, b in zip(v1, v2))
        m1 = math.sqrt(sum(a * a for a in v1)) or 1.0
        m2 = math.sqrt(sum(b * b for b in v2)) or 1.0
        return dot / (m1 * m2)

    scored_local = []
    for item in _LOCAL_VECTOR_STORE:
        meta = item["metadata"]
        # Filter check
        if company_id is not None and meta.get("company_id") not in (company_id, 0):
            continue
        if vendor_company_id is not None and meta.get("vendor_company_id") not in (vendor_company_id, 0):
            continue

        score = cosine_similarity(query_vec, item["values"])
        scored_local.append((score, meta))

    scored_local.sort(key=lambda x: x[0], reverse=True)
    for score, meta in scored_local[:top_k]:
        matched_results.append({
            "title": meta.get("title", "Policy Document"),
            "category": meta.get("category", "General"),
            "chunk_text": meta.get("chunk_text", ""),
            "score": round(float(score), 3)
        })

    return matched_results

def generate_rag_answer(
    query_text: str,
    context_chunks: List[Dict[str, Any]],
    user_info: Dict[str, Any]
) -> str:
    """
    Generates role-aware, policy-backed answer using Gemini LLM.
    """
    gemini_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")

    # Format retrieved context
    context_str = "\n\n".join([
        f"--- DOCUMENT: {c['title']} ({c['category']}) ---\n{c['chunk_text']}"
        for c in context_chunks
    ]) if context_chunks else "No specific policy document chunks retrieved."

    user_context_str = (
        f"User Name: {user_info.get('full_name', 'User')}\n"
        f"Role: {user_info.get('role', 'N/A')}\n"
        f"Organization: {user_info.get('company_name') or user_info.get('vendor_company_name') or 'Global Administrator'}\n"
        f"Designation: {user_info.get('designation', 'Staff Member')}\n"
        f"Department: {user_info.get('department', 'General')}\n"
        f"--- LIVE EMPLOYEE DATABASE LEAVE LEDGER METRICS ---\n"
        f"Annual Leave Quota: {user_info.get('annual_leave_quota', 20)} days/year\n"
        f"Annual Leave Taken: {user_info.get('annual_leave_taken', 0)} days\n"
        f"Remaining Annual Leave Balance: {user_info.get('remaining_annual_leave', 20)} days\n"
        f"Sick Leave Quota: {user_info.get('sick_leave_quota', 10)} days/year\n"
        f"Sick Leave Taken: {user_info.get('sick_leave_taken', 0)} days\n"
        f"Remaining Sick Leave Balance: {user_info.get('remaining_sick_leave', 10)} days\n"
        f"Last Recorded Leave Date: {user_info.get('last_leave_date', 'None')}\n"
        f"Last Recorded Leave Type: {user_info.get('last_leave_type', 'None')}"
    )

    prompt = f"""You are the official AI Assistant for Workforce OS, an enterprise employee and vendor management platform.
Your task is to answer user queries accurately, professionally, and empathetically by COMBINING the user's live database profile/leave records WITH official company policy document excerpts.

LOGGED-IN USER PROFILE & LIVE DATABASE RECORDS:
{user_context_str}

RETRIEVED COMPANY POLICY EXCERPTS:
{context_str}

USER QUESTION:
{query_text}

MANDATORY RESPONSE GUIDELINES:
1. Address the user by their name ({user_info.get('full_name')}) and tailor your answer specifically to their role ({user_info.get('role')}).
2. COMBINE LIVE DATABASE RECORDS WITH POLICY RULES:
   - When asked about leave balances or leave status, calculate and state their EXACT remaining leave balances from their database record (e.g. {user_info.get('remaining_annual_leave')} annual leave days remaining out of {user_info.get('annual_leave_quota')} quota).
   - Explicitly mention their last recorded leave if relevant (e.g., "Your last recorded leave was {user_info.get('last_leave_type')} on {user_info.get('last_leave_date')}").
3. PROACTIVE POLICY REMINDERS & EDGE CASES:
   - Always remind them of key policy requirements (e.g. Leave exceeding 3 consecutive days requires manager approval 2 weeks in advance; max 5 days rollover to next calendar year).
   - If they have recent leaves or low balance, gently remind them of approval workflows or documentation requirements.
4. FORMATTING: Format the output cleanly with bold headers and bullet points.
"""

    if gemini_key:
        try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            res = requests.post(url, json=payload, timeout=20)
            if res.status_code == 200:
                data = res.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]
            else:
                # Try fallback model gemini-1.5-flash
                url2 = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={gemini_key}"
                res2 = requests.post(url2, json=payload, timeout=20)
                if res2.status_code == 200:
                    data2 = res2.json()
                    return data2["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            logger.error(f"Gemini LLM generation exception: {e}")

    # High quality structured default fallback answer if Gemini key is pending
    return (
        f"Hello {user_info.get('full_name', 'there')},\n\n"
        f"Based on your profile as a **{user_info.get('role')}** in **{user_info.get('company_name') or user_info.get('vendor_company_name') or 'Workforce OS'}**, "
        f"here is the information regarding your query:\n\n"
        f"• **Privilege Leave (PL / Annual):** 21 Days total per annum (accrued at 1.75 days per month). Max 10 days carry-forward allowed.\n"
        f"• **Sick & Casual Leave (SL/CL):** 12 Days allocated per annum (1 day per month). Medical certificate required for >2 consecutive days.\n"
        f"• **Maternity / Paternity:** 26 Weeks fully paid for Maternity; 15 Days fully paid for Paternity.\n"
        f"• **Notice Requirement:** Planned vacation requires approval at least 10 business days in advance.\n\n"
        f"*Note: Configure `GEMINI_API_KEY` in backend `.env` for real-time AI neural generation.*"
    )
