import React, { useMemo } from "react";
import {
  isRouteErrorResponse,
  Links,
  Meta,
  Outlet,
  Scripts,
  ScrollRestoration,
} from "react-router";
import { ConfigProvider, theme as antdTheme } from "antd";
import type { Route } from "./+types/root";
import { useAppStore } from "./store/useAppStore";
import "./app.css";

export const links: Route.LinksFunction = () => [
  { rel: "preconnect", href: "https://fonts.googleapis.com" },
  {
    rel: "preconnect",
    href: "https://fonts.gstatic.com",
    crossOrigin: "anonymous",
  },
  {
    rel: "stylesheet",
    href: "https://fonts.googleapis.com/css2?family=Inter:ital,opsz,wght@0,14..32,100..900;1,14..32,100..900&display=swap",
  },
  { rel: "manifest", href: "/site.webmanifest" },
  { rel: "shortcut icon", href: "/favicon.ico" },
  { rel: "canonical", href: "https://vijeeth.zapto.org/domain" }
];

export const meta: Route.MetaFunction = () => [
  { title: "Workforce OS - Enterprise Employee, Vendor & Policy Management System" },
  {
    name: "description",
    content: "Workforce OS is an all-in-one enterprise platform for employee directory management, vendor contractor tracking, role-scoped policies, and Gemini AI RAG assistant.",
  },
  { name: "keywords", content: "workforce management, employee directory, vendor portal, contractor tracking, company policy RAG, enterprise HR OS, Gemini AI assistant" },
  { name: "robots", content: "index, follow, max-snippet:-1, max-image-preview:large" },
  { name: "theme-color", content: "#1677ff" },
  { property: "og:title", content: "Workforce OS - Enterprise Employee, Vendor & Policy Management System" },
  { property: "og:description", content: "All-in-one enterprise platform for employee directory management, vendor contractor tracking, role-scoped policies, and Gemini AI RAG assistant." },
  { property: "og:type", content: "website" },
  { property: "og:url", content: "https://vijeeth.zapto.org/domain" },
  { property: "og:image", content: "https://vijeeth.zapto.org/domain/favicon.ico" },
  { property: "og:site_name", content: "Workforce OS Enterprise Platform" },
  { name: "twitter:card", content: "summary_large_image" },
  { name: "twitter:title", content: "Workforce OS - Enterprise Employee, Vendor & Policy Management System" },
  { name: "twitter:description", content: "All-in-one enterprise platform for employee directory management, vendor contractor tracking, role-scoped policies, and Gemini AI RAG assistant." },
];

export function Layout({ children }: { children: React.ReactNode }) {
  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "Workforce OS",
    "applicationCategory": "BusinessApplication",
    "operatingSystem": "Web",
    "url": "https://vijeeth.zapto.org/domain",
    "description": "Enterprise Employee, Vendor & Policy Management Platform with AI RAG Vector Assistant.",
    "offers": {
      "@type": "Offer",
      "price": "0",
      "priceCurrency": "USD"
    }
  };

  return (
    <html lang="en">
      <head>
        <meta charSet="utf-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <Meta />
        <Links />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
        />
      </head>
      <body>
        {children}
        <ScrollRestoration />
        <Scripts />
      </body>
    </html>
  );
}

const themeTokens = {
  colorPrimary: "#1677ff",
  borderRadius: 8,
  fontFamily: "Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif",
};

export default function App() {
  const themeMode = useAppStore((state) => state.themeMode);

  const themeConfig = useMemo(
    () => ({
      algorithm: themeMode === "dark" ? antdTheme.darkAlgorithm : antdTheme.defaultAlgorithm,
      token: themeTokens,
    }),
    [themeMode]
  );

  return (
    <ConfigProvider theme={themeConfig}>
      <Outlet />
    </ConfigProvider>
  );
}

export function ErrorBoundary({ error }: Route.ErrorBoundaryProps) {
  let message = "Oops!";
  let details = "An unexpected error occurred.";
  let stack: string | undefined;

  if (isRouteErrorResponse(error)) {
    message = error.status === 404 ? "404" : "Error";
    details =
      error.status === 404
        ? "The requested page could not be found."
        : error.statusText || details;
  } else if (import.meta.env.DEV && error && error instanceof Error) {
    details = error.message;
    stack = error.stack;
  }

  return (
    <main className="pt-16 p-4 container mx-auto">
      <h1>{message}</h1>
      <p>{details}</p>
      {stack && (
        <pre className="w-full p-4 overflow-x-auto">
          <code>{stack}</code>
        </pre>
      )}
    </main>
  );
}
