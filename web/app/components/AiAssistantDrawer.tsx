import React, { useState, useRef, useEffect } from "react";
import { Drawer, Button, Input, Tag, Space, Avatar, Spin, Tooltip, Card, Typography, Grid } from "antd";
import {
  RobotOutlined,
  SendOutlined,
  UserOutlined,
  BookOutlined,
  DeleteOutlined,
  CheckCircleOutlined,
  BulbOutlined
} from "@ant-design/icons";
import { api } from "../services/api";
import { useAuthStore } from "../store/useAuthStore";

const { Text, Title } = Typography;
const { useBreakpoint } = Grid;

interface Message {
  id: string;
  sender: "user" | "ai";
  text: string;
  sources?: Array<{
    title: string;
    source_type: string;
    chunk_text: string;
    score: number;
  }>;
  timestamp: string;
}

export const AiAssistantDrawer: React.FC = () => {
  const screens = useBreakpoint();
  const isMobile = !screens.md;
  const user = useAuthStore((state) => state.user);

  const [open, setOpen] = useState(false);
  const [inputMsg, setInputMsg] = useState("");
  const [loading, setLoading] = useState(false);

  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      sender: "ai",
      text: `Hello ${user?.full_name || "there"}! I am your **Workforce OS AI Assistant**. I can help you with company policies, leave balances, contractor rules, and workplace guidelines. What would you like to ask?`,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    if (open) {
      scrollToBottom();
    }
  }, [messages, open]);

  const handleSendMessage = async (textToSend?: string) => {
    const query = textToSend || inputMsg;
    if (!query.trim() || loading) return;

    const userMessage: Message = {
      id: `user_${Date.now()}`,
      sender: "user",
      text: query,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMessage]);
    if (!textToSend) setInputMsg("");
    setLoading(true);

    try {
      const res = await api.post("/rag/chat", { message: query });
      const data = res.data;

      const aiMessage: Message = {
        id: `ai_${Date.now()}`,
        sender: "ai",
        text: data.answer,
        sources: data.sources || [],
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };

      setMessages((prev) => [...prev, aiMessage]);
    } catch (err: any) {
      const errorMessage: Message = {
        id: `err_${Date.now()}`,
        sender: "ai",
        text: "Apologies, I encountered an issue connecting to the Policy AI service. Please verify your connection or try again.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleClearChat = () => {
    setMessages([
      {
        id: "welcome",
        sender: "ai",
        text: `Hello ${user?.full_name || "there"}! I am your Workforce OS AI Assistant. Ask me anything about leave policies, company guidelines, or vendor rules.`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      }
    ]);
  };

  const quickPrompts = [
    "How many annual leave days do I have?",
    "What is our remote work policy?",
    "What are vendor contractor timesheet rules?",
    "How does expense reimbursement work?"
  ];

  const renderFormattedText = (text: string) => {
    if (!text) return null;

    const lines = text.split("\n");

    const parseInlineMarkdown = (str: string) => {
      const parts = str.split(/(\*\*.*?\*\*)/g);
      return parts.map((part, index) => {
        if (part.startsWith("**") && part.endsWith("**") && part.length >= 4) {
          return (
            <strong key={index} style={{ fontWeight: 700 }}>
              {part.slice(2, -2)}
            </strong>
          );
        }
        return part;
      });
    };

    return lines.map((line, idx) => {
      const trimmed = line.trim();
      if (!trimmed) {
        return <div key={idx} style={{ height: 6 }} />;
      }

      // Check header tags (### or ## or #)
      if (trimmed.startsWith("#")) {
        const headerText = trimmed.replace(/^#+\s*/, "");
        return (
          <div key={idx} style={{ fontWeight: 700, fontSize: 14, color: "#0f172a", marginTop: 8, marginBottom: 4 }}>
            {parseInlineMarkdown(headerText)}
          </div>
        );
      }

      // Check bullet list item (* or - or •)
      if (trimmed.startsWith("* ") || trimmed.startsWith("- ") || trimmed.startsWith("• ")) {
        const content = trimmed.replace(/^[\*\-\•]\s*/, "");
        return (
          <div key={idx} style={{ display: "flex", gap: 6, marginBottom: 4, paddingLeft: 4, alignItems: "flex-start" }}>
            <span style={{ color: "#1677ff", fontWeight: 700, lineHeight: 1.4 }}>•</span>
            <div style={{ flex: 1, lineHeight: 1.4 }}>{parseInlineMarkdown(content)}</div>
          </div>
        );
      }

      return (
        <div key={idx} style={{ marginBottom: 4, lineHeight: 1.4 }}>
          {parseInlineMarkdown(line)}
        </div>
      );
    });
  };

  return (
    <>
      {/* Floating Action Trigger Button */}
      <div style={{ position: "fixed", bottom: 24, right: 24, zIndex: 1000 }}>
        <Tooltip title="Ask Policy AI Assistant" placement="left">
          <Button
            type="primary"
            shape="circle"
            size="large"
            onClick={() => setOpen(true)}
            style={{
              width: 56,
              height: 56,
              boxShadow: "0 8px 24px rgba(22, 119, 255, 0.4)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              background: "linear-gradient(135deg, #1677ff 0%, #0958d9 100%)",
              border: "none"
            }}
            icon={<RobotOutlined style={{ fontSize: 28, color: "#ffffff" }} />}
          />
        </Tooltip>
      </div>

      {/* RAG Assistant Drawer */}
      <Drawer
        title={
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingRight: 8 }}>
            <Space align="center" size="middle">
              <Avatar style={{ backgroundColor: "#1677ff" }} icon={<RobotOutlined />} size="medium" />
              <div>
                <div style={{ fontWeight: 700, fontSize: 15, lineHeight: 1.2 }}>Policy AI Assistant</div>
                <div style={{ fontSize: 11, color: "#64748b" }}>Powered by Gemini & Pinecone Vector RAG</div>
              </div>
            </Space>
            <Button type="text" icon={<DeleteOutlined />} onClick={handleClearChat} title="Clear Chat History" size="small" />
          </div>
        }
        placement="right"
        width={isMobile ? "100%" : 430}
        onClose={() => setOpen(false)}
        open={open}
        styles={{
          body: { padding: "16px", display: "flex", flexDirection: "column", backgroundColor: "#f8fafc" },
          footer: { padding: "12px 16px", background: "#ffffff", borderTop: "1px solid #e2e8f0" }
        }}
        footer={
          <div>
            <div style={{ display: "flex", gap: 8 }}>
              <Input.TextArea
                placeholder="Ask about leave rules, remote work, expenses..."
                value={inputMsg}
                onChange={(e) => setInputMsg(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    handleSendMessage();
                  }
                }}
                autoSize={{ minRows: 1, maxRows: 3 }}
                style={{ borderRadius: 8, resize: "none" }}
                disabled={loading}
              />
              <Button
                type="primary"
                icon={<SendOutlined />}
                onClick={() => handleSendMessage()}
                loading={loading}
                style={{ height: "auto", borderRadius: 8 }}
              />
            </div>
            <div style={{ fontSize: 10, color: "#94a3b8", textAlign: "center", marginTop: 8 }}>
              Workforce OS Role-Scoped Vector Intelligence
            </div>
          </div>
        }
      >
        {/* User Role Info Banner */}
        <div style={{
          padding: "8px 12px",
          background: "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
          borderRadius: 10,
          color: "#ffffff",
          marginBottom: 14,
          fontSize: 12,
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center"
        }}>
          <span>Role: <b>{user?.role}</b></span>
          <Tag color="blue" style={{ margin: 0, fontSize: 11 }}>
            {user?.company_name || user?.vendor_company_name || "Global Admin"}
          </Tag>
        </div>

        {/* Message Thread */}
        <div style={{ flex: 1, overflowY: "auto", display: "flex", flexDirection: "column", gap: 14 }}>
          {messages.map((msg) => (
            <div
              key={msg.id}
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: msg.sender === "user" ? "flex-end" : "flex-start"
              }}
            >
              <div style={{
                maxWidth: "88%",
                padding: "12px 14px",
                borderRadius: msg.sender === "user" ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
                backgroundColor: msg.sender === "user" ? "#1677ff" : "#ffffff",
                color: msg.sender === "user" ? "#ffffff" : "#0f172a",
                boxShadow: msg.sender === "user" ? "0 4px 12px rgba(22,119,255,0.2)" : "0 2px 8px rgba(0,0,0,0.05)",
                border: msg.sender === "user" ? "none" : "1px solid #e2e8f0",
                fontSize: 13,
                lineHeight: 1.5,
              }}>
                {renderFormattedText(msg.text)}

                {/* Referenced Sources Accordion */}
                {msg.sources && msg.sources.length > 0 && (
                  <div style={{ marginTop: 10, paddingTop: 8, borderTop: "1px solid #f1f5f9" }}>
                    <div style={{ fontSize: 11, fontWeight: 700, color: "#64748b", marginBottom: 4, display: "flex", alignItems: "center", gap: 4 }}>
                      <BookOutlined /> Referenced Policy Sources:
                    </div>
                    {msg.sources.map((src, idx) => (
                      <div key={idx} style={{ fontSize: 11, color: "#334155", backgroundColor: "#f8fafc", padding: "4px 8px", borderRadius: 6, marginBottom: 4 }}>
                        <b>{src.title}</b> ({src.source_type})
                      </div>
                    ))}
                  </div>
                )}
              </div>
              <span style={{ fontSize: 10, color: "#94a3b8", marginTop: 4, padding: "0 4px" }}>
                {msg.timestamp}
              </span>
            </div>
          ))}

          {loading && (
            <div style={{ display: "flex", alignItems: "center", gap: 8, padding: "8px 12px" }}>
              <Spin size="small" />
              <span style={{ fontSize: 12, color: "#64748b" }}>Searching vector database & generating answer...</span>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Quick Suggest Prompts */}
        <div style={{ marginTop: 14, paddingTop: 10, borderTop: "1px solid #e2e8f0" }}>
          <div style={{ fontSize: 11, fontWeight: 600, color: "#64748b", marginBottom: 6, display: "flex", alignItems: "center", gap: 4 }}>
            <BulbOutlined style={{ color: "#faad14" }} /> Suggested Policy Questions:
          </div>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
            {quickPrompts.map((p, idx) => (
              <Tag
                key={idx}
                color="blue"
                onClick={() => handleSendMessage(p)}
                style={{ cursor: "pointer", borderRadius: 12, fontSize: 11, padding: "3px 10px", margin: 0 }}
              >
                {p}
              </Tag>
            ))}
          </div>
        </div>
      </Drawer>
    </>
  );
};
