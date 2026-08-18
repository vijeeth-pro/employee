import React, { useEffect } from "react";

interface SEOHeadProps {
  title?: string;
  description?: string;
  keywords?: string;
  canonicalPath?: string;
  ogType?: string;
  ogImage?: string;
  schema?: Record<string, any>;
}

const DEFAULT_TITLE = "Workforce OS - Enterprise Employee, Vendor & Policy Management System";
const DEFAULT_DESCRIPTION = "Workforce OS is an all-in-one enterprise platform for employee directory management, vendor contractor tracking, role-scoped policies, and Gemini AI RAG assistant.";
const DEFAULT_KEYWORDS = "workforce management, employee directory, vendor portal, contractor tracking, company policy RAG, enterprise HR OS, Gemini AI assistant";
const DOMAIN = "https://vijeeth.zapto.org";

export const SEOHead: React.FC<SEOHeadProps> = ({
  title,
  description = DEFAULT_DESCRIPTION,
  keywords = DEFAULT_KEYWORDS,
  canonicalPath = "",
  ogType = "website",
  ogImage = `${DOMAIN}/favicon.ico`,
  schema
}) => {
  const fullTitle = title ? `${title} | Workforce OS` : DEFAULT_TITLE;
  const canonicalUrl = `${DOMAIN}${canonicalPath}`;

  useEffect(() => {
    // 1. Update Document Title
    document.title = fullTitle;

    // Helper to set or create meta tags
    const setMetaTag = (nameAttr: string, valAttr: string, content: string) => {
      let element = document.querySelector(`meta[${nameAttr}="${valAttr}"]`) as HTMLMetaElement;
      if (!element) {
        element = document.createElement("meta");
        element.setAttribute(nameAttr, valAttr);
        document.head.appendChild(element);
      }
      element.setAttribute("content", content);
    };

    // 2. Standard Meta Tags
    setMetaTag("name", "description", description);
    setMetaTag("name", "keywords", keywords);
    setMetaTag("name", "robots", "index, follow, max-snippet:-1, max-image-preview:large");
    setMetaTag("name", "theme-color", "#1677ff");

    // 3. OpenGraph Tags
    setMetaTag("property", "og:title", fullTitle);
    setMetaTag("property", "og:description", description);
    setMetaTag("property", "og:type", ogType);
    setMetaTag("property", "og:url", canonicalUrl);
    setMetaTag("property", "og:image", ogImage);
    setMetaTag("property", "og:site_name", "Workforce OS Enterprise Platform");

    // 4. Twitter Card Tags
    setMetaTag("name", "twitter:card", "summary_large_image");
    setMetaTag("name", "twitter:title", fullTitle);
    setMetaTag("name", "twitter:description", description);
    setMetaTag("name", "twitter:image", ogImage);

    // 5. Canonical Link Tag
    let canonicalLink = document.querySelector('link[rel="canonical"]') as HTMLLinkElement;
    if (!canonicalLink) {
      canonicalLink = document.createElement("link");
      canonicalLink.setAttribute("rel", "canonical");
      document.head.appendChild(canonicalLink);
    }
    canonicalLink.setAttribute("href", canonicalUrl);

    // 6. JSON-LD Structured Data
    if (schema) {
      let scriptTag = document.querySelector('script[type="application/ld+json"]') as HTMLScriptElement;
      if (!scriptTag) {
        scriptTag = document.createElement("script");
        scriptTag.setAttribute("type", "application/ld+json");
        document.head.appendChild(scriptTag);
      }
      scriptTag.textContent = JSON.stringify(schema);
    }
  }, [fullTitle, description, keywords, canonicalUrl, ogType, ogImage, schema]);

  return null;
};
