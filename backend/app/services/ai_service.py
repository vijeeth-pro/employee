import os
import re
import math
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.models import User, Company, VendorCompany, CompanyPolicy, UserRole
from app.schemas import AIChatResponse, AISourceDocument

class VectorChunk:
    def __init__(
        self,
        chunk_id: str,
        title: str,
        content: str,
        category: str,
        source_type: str, # "policy", "employee", "company", "vendor"
        company_id: Optional[int] = None,
        vendor_company_id: Optional[int] = None,
        user_id: Optional[int] = None
    ):
        self.chunk_id = chunk_id
        self.title = title
        self.content = content
        self.category = category
        self.source_type = source_type
        self.company_id = company_id
        self.vendor_company_id = vendor_company_id
        self.user_id = user_id

class RAGEngine:
    def __init__(self):
        self.vector_chunks: List[VectorChunk] = []
        self.is_indexed = False

    def tokenize(self, text: str) -> List[str]:
        """Convert text into clean lowercase token words."""
        return re.findall(r'\w+', text.lower())

    def compute_similarity(self, query: str, document_text: str) -> float:
        """Compute cosine word similarity between query prompt and vector chunk content."""
        query_words = set(self.tokenize(query))
        if not query_words:
            return 0.0
        doc_words = set(self.tokenize(document_text))
        intersection = query_words.intersection(doc_words)
        if not intersection:
            return 0.0
        return len(intersection) / math.sqrt(len(query_words) * len(doc_words))

    def index_database(self, db: Session):
        """Index database entities (Companies, Vendors, Employees, Policies) into vector chunks."""
        chunks: List[VectorChunk] = []

        # 1. Index Companies
        companies = db.query(Company).filter(Company.status == "active").all()
        for comp in companies:
            chunks.append(VectorChunk(
                chunk_id=f"comp_{comp.id}",
                title=comp.name,
                content=f"Company Name: {comp.name}, Code: {comp.code}, Industry: {comp.industry}, Address: {comp.address}, Contact Email: {comp.email}, Phone: {comp.phone}.",
                category="Company Profile",
                source_type="company",
                company_id=comp.id
            ))

        # 2. Index Vendor Companies
        vendors = db.query(VendorCompany).filter(VendorCompany.status == "active").all()
        for vend in vendors:
            chunks.append(VectorChunk(
                chunk_id=f"vend_{vend.id}",
                title=vend.name,
                content=f"Vendor Agency Name: {vend.name}, Code: {vend.code}, Services Offered: {vend.service_type}, Contact Email: {vend.email}, Phone: {vend.phone}.",
                category="Vendor Profile",
                source_type="vendor",
                vendor_company_id=vend.id
            ))

        # 3. Index Employees & Contractors
        users = db.query(User).filter(User.status == "active").all()
        for u in users:
            org_name = u.company.name if u.company else (u.vendor_company.name if u.vendor_company else "System")
            chunks.append(VectorChunk(
                chunk_id=f"user_{u.id}",
                title=f"{u.full_name} ({u.designation or u.role})",
                content=f"Employee Name: {u.full_name}, Email: {u.email}, Role: {u.role.value}, Designation: {u.designation or 'N/A'}, Department: {u.department or 'N/A'}, Organization: {org_name}, Phone: {u.phone or 'N/A'}.",
                category="Personnel Profile",
                source_type="employee",
                company_id=u.company_id,
                vendor_company_id=u.vendor_company_id,
                user_id=u.id
            ))

        # 4. Index Company Policies & Rules
        policies = db.query(CompanyPolicy).all()
        for pol in policies:
            chunks.append(VectorChunk(
                chunk_id=f"policy_{pol.id}",
                title=pol.title,
                content=f"Policy Title: {pol.title}, Category: {pol.category}. Document Content: {pol.content}",
                category=pol.category,
                source_type="policy",
                company_id=pol.company_id,
                vendor_company_id=pol.vendor_company_id
            ))

        self.vector_chunks = chunks
        self.is_indexed = True
        print(f"[RAGEngine] Indexed {len(chunks)} vector documents into Chroma/Memory Store.")

    def filter_chunks_by_role(self, current_user: User) -> List[VectorChunk]:
        """Hierarchical Role-Based Vector Access Control."""
        role = current_user.role

        # 1. Admin: Complete global access
        if role == UserRole.ADMIN:
            return self.vector_chunks

        # 2. Company Admin: Company employees, company policies, and associated vendor details
        if role == UserRole.COMPANY:
            return [
                c for c in self.vector_chunks
                if c.company_id == current_user.company_id or c.source_type in ["company", "policy", "vendor"]
            ]

        # 3. Vendor Company Admin: Vendor contractors and vendor policies
        if role == UserRole.VENDOR_COMPANY:
            return [
                c for c in self.vector_chunks
                if c.vendor_company_id == current_user.vendor_company_id or c.source_type in ["vendor", "policy"]
            ]

        # 4. Regular Employee: Own profile, parent company details, and general company policies
        if role == UserRole.EMPLOYEE:
            return [
                c for c in self.vector_chunks
                if (c.company_id == current_user.company_id and c.source_type in ["company", "policy"]) or c.user_id == current_user.id
            ]

        # 5. Vendor Contractor: Own profile, vendor agency details, and contractor rules
        if role == UserRole.VENDOR_EMPLOYEE:
            return [
                c for c in self.vector_chunks
                if (c.vendor_company_id == current_user.vendor_company_id and c.source_type in ["vendor", "policy"]) or c.user_id == current_user.id
            ]

        return []

    def query(self, prompt: str, current_user: User, db: Session) -> AIChatResponse:
        """Process user query with RAG vector retrieval & role filtering."""
        if not self.is_indexed:
            self.index_database(db)

        # Apply Hierarchical RBAC Filter
        accessible_chunks = self.filter_chunks_by_role(current_user)

        # Vector Similarity Retrieval
        scored_chunks = []
        for chunk in accessible_chunks:
            score = self.compute_similarity(prompt, f"{chunk.title} {chunk.category} {chunk.content}")
            if score > 0.02 or any(w.lower() in chunk.content.lower() for w in prompt.split() if len(w) > 3):
                scored_chunks.append((score, chunk))

        # Sort by relevance score
        scored_chunks.sort(key=lambda x: x[0], reverse=True)
        top_chunks = [item[1] for item in scored_chunks[:4]]

        # Prepare Citation Sources
        sources = [
            AISourceDocument(
                title=c.title,
                category=c.category,
                source_type=c.source_type
            )
            for c in top_chunks
        ]

        # Build Augmented Prompt Context
        context_text = "\n\n".join([f"[{c.title} - {c.category}]: {c.content}" for c in top_chunks])

        # Synthesize Intelligent Response
        answer = self.synthesize_response(prompt, context_text, current_user, top_chunks)

        return AIChatResponse(
            answer=answer,
            sources=sources,
            role_applied=current_user.role.value
        )

    def synthesize_response(self, prompt: str, context: str, user: User, chunks: List[VectorChunk]) -> str:
        """Synthesize answer using Gemini LLM (or fallback template generator)."""
        from app.core.config import settings
        gemini_api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

        if gemini_api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=gemini_api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')
                system_prompt = f"""You are Workforce OS AI Assistant. You are answering a question for {user.full_name} (Role: {user.role.value}).
Use the following retrieved context documents to answer accurately, concisely, and politely:

Context Documents:
{context if context else 'No specific internal documents matched.'}

User Question: {prompt}

Answer:"""
                res = model.generate_content(system_prompt)
                if res.text:
                    return res.text
            except Exception as e:
                print(f"[RAGEngine] Gemini API notice: {e}")

        # Intelligent RAG Fallback Synthesizer
        if not chunks:
            return f"Hello {user.full_name}. Based on your role ({user.role.value}), I searched your authorized organization records and policies, but found no specific documents matching your query '{prompt}'. Please try asking about leave policies, working hours, or company details."

        matching_titles = ", ".join([f"'{c.title}'" for c in chunks])
        snippet = chunks[0].content

        return f"Based on your role as **{user.role.value.replace('.', ' ').title()}**, I retrieved information from {matching_titles}:\n\n{snippet}\n\n*Note: This information is scoped to your authorized organization permissions.*"

# Global RAG Engine Singleton
rag_engine = RAGEngine()
