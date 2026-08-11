import React, { useState, useRef, useEffect } from "react";
import { Drawer, Button, Input, Space, Tag, Avatar, Typography, Card, Spin, Tooltip, Badge } from "antd";
import {
  RobotOutlined,
  SendOutlined,
  UserOutlined,
  SafetyCertificateOutlined,
  FileTextOutlined,
  ClearOutlined,
  BulbOutlined
} from "@ant-design/icons";
import { api } from "../services/api";
import { useAuthStore } from "../store/useAuthStore";

const { Text, Paragraph } = Typography;

interface ChatMessage {
  id: string;
  sender: "user" | "ai";
  text: string;
  sources?: { title: string; category: string; source_type: string }[];
  roleApplied?: string;
  timestamp: string;
}

export const AiAssistant: React.FC = () => {
  const user = useAuthStore((state) => state.user);
  const [open, setOpen] = useState(false);
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, loading]);

  const handleSend = async (queryText?: string) => {
    const textToSend = queryText || prompt;
    if (!textToSend.trim() || loading) return;

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: "user",
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    if (!queryText) setPrompt("");
    setLoading(true);

    try {
      const res = await api.post("/ai/chat", { prompt: textToSend });
      const aiMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: "ai",
        text: res.data.answer,
        sources: res.data.sources,
        roleApplied: res.data.role_applied,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, aiMsg]);
    } catch (err: any) {
      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: "ai",
        text: "Sorry, I encountered an error connecting to the AI vector assistant. Please try again.",
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setMessages([]);
  };

  const suggestedPrompts = [
    "What is our annual leave policy?",
    "What are the remote work rules?",
    "Show contractor code of conduct",
    "What are my designation details?",
  ];

  return (
    <>
      {/* Floating Action Trigger Button */}
      <div style={{ position: "fixed", bottom: 28, right: 28, zIndex: 1000 }}>
        <Badge count="AI RAG" style={{ backgroundColor: "#722ed1" }}>
          <Button
            type="primary"
            shape="circle"
            size="large"
            icon={<RobotOutlined style={{ fontSize: 24 }} />}
            onClick={() => setOpen(true)}
            style={{
              width: 56,
              height: 56,
              boxShadow: "0 8px 24px rgba(114, 46, 209, 0.4)",
              background: "linear-gradient(135deg, #722ed1 0%, #1677ff 100%)",
              border: "none"
            }}
          />
        </Badge>
      </div>

      {/* AI Assistant Drawer */}
      <Drawer
        title={
          <Space align="center" style={{ justifyContent: "space-between", width: "100%" }}>
            <Space>
              <Avatar style={{ backgroundColor: "#722ed1" }} icon={<RobotOutlined />} />
              <div>
                <div style={{ fontWeight: 700, fontSize: 16 }}>Workforce OS AI Assistant</div>
                <Text type="secondary" style={{ fontSize: 11 }}>
                  Role Context: <Tag color="purple">{user?.role || "guest"}</Tag>
                </Text>
              </div>
            </Space>
            <Tooltip title="Clear Chat">
              <Button type="text" icon={<ClearOutlined />} onClick={handleClear} />
            </Tooltip>
          </Space>
        }
        placement="right"
        width={440}
        onClose={() => setOpen(false)}
        open={open}
        styles={{
          body: { display: "flex", flexDirection: "column", padding: "16px 20px", background: "#f8fafc" }
        }}
      >
        {/* Chat History Area */}
        <div style={{ flex: 1, overflowY: "auto", paddingRight: 4, display: "flex", flexDirection: "column", gap: 16 }}>
          {messages.length === 0 && (
            <Card
              style={{
                borderRadius: 16,
                background: "linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%)",
                border: "1px solid #e9d5ff",
                textAlign: "center"
              }}
            >
              <RobotOutlined style={{ fontSize: 36, color: "#722ed1", marginBottom: 12 }} />
              <Paragraph style={{ fontWeight: 600, fontSize: 15, marginBottom: 4 }}>
                Hello {user?.full_name || "there"}!
              </Paragraph>
              <Paragraph type="secondary" style={{ fontSize: 13, marginBottom: 16 }}>
                I am your enterprise AI assistant. Ask me questions about company policies, leave rules, vendor contractors, or team profiles.
              </Paragraph>

              <Text style={{ fontSize: 12, fontWeight: 600, color: "#6b21a8", display: "block", marginBottom: 8 }}>
                Suggested Quick Prompts:
              </Text>
              <Space direction="vertical" style={{ width: "100%" }} size="small">
                {suggestedPrompts.map((p, idx) => (
                  <Button
                    key={idx}
                    size="small"
                    block
                    onClick={() => handleSend(p)}
                    style={{ borderRadius: 8, textAlign: "left", fontSize: 12 }}
                  >
                    <BulbOutlined style={{ color: "#722ed1" }} /> {p}
                  </Button>
                ))}
              </Space>
            </Card>
          )}

          {messages.map((msg) => (
            <div
              key={msg.id}
              style={{
                display: "flex",
                justifyContent: msg.sender === "user" ? "flex-end" : "flex-start",
              }}
            >
              <div
                style={{
                  maxWidth: "85%",
                  padding: "12px 16px",
                  borderRadius: msg.sender === "user" ? "16px 16px 4px 16px" : "16px 16px 16px 4px",
                  background: msg.sender === "user" ? "linear-gradient(135deg, #1677ff 0%, #0958d9 100%)" : "#ffffff",
                  color: msg.sender === "user" ? "#ffffff" : "#0f172a",
                  boxShadow: "0 2px 8px rgba(0,0,0,0.06)",
                  border: msg.sender === "user" ? "none" : "1px solid #e2e8f0"
                }}
              >
                <div style={{ fontSize: 13, lineHeight: 1.5, whiteSpace: "pre-wrap" }}>
                  {msg.text}
                </div>

                {/* Source Citation Badges */}
                {msg.sources && msg.sources.length > 0 && (
                  <div style={{ marginTop: 10, paddingTop: 8, borderTop: "1px solid #f1f5f9" }}>
                    <Text type="secondary" style={{ fontSize: 11, fontWeight: 600, display: "block", marginBottom: 4 }}>
                      Retrieved Context Sources:
                    </Text>
                    <Space wrap size={[0, 4]}>
                      {msg.sources.map((src, i) => (
                        <Tag key={i} color="blue" icon={<FileTextOutlined />} style={{ fontSize: 10, borderRadius: 4 }}>
                          {src.title}
                        </Tag>
                      ))}
                    </Space>
                  </div>
                )}

                <div style={{
                  fontSize: 10,
                  textAlign: "right",
                  marginTop: 6,
                  color: msg.sender === "user" ? "rgba(255,255,255,0.7)" : "#94a3b8"
                }}>
                  {msg.timestamp}
                </div>
              </div>
            </div>
          ))}

          {loading && (
            <div style={{ display: "flex", justifyContent: "flex-start" }}>
              <Card size="small" style={{ borderRadius: 12 }}>
                <Space>
                  <Spin size="small" />
                  <Text type="secondary" style={{ fontSize: 12 }}>Searching vector store & generating response...</Text>
                </Space>
              </Card>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div style={{ marginTop: 16, paddingTop: 12, borderTop: "1px solid #e2e8f0" }}>
          <Space.Compact style={{ width: "100%" }}>
            <Input
              placeholder="Ask AI about policies, employees, vendors..."
              value={prompt}
              onChange={(e) => setPrompt(e.target.value)}
              onPressEnter={() => handleSend()}
              disabled={loading}
              style={{ borderRadius: "8px 0 0 8px" }}
            />
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={() => handleSend()}
              loading={loading}
              style={{ borderRadius: "0 8px 8px 0", background: "#722ed1" }}
            >
              Send
            </Button>
          </Space.Compact>
        </div>
      </Drawer>
    </>
  );
};
