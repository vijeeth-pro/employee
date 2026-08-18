import React, { useEffect, useState, useRef } from "react";
import { Row, Col, Card, Statistic, Table, Tag, Button, Typography, Space, Spin, message, Popconfirm, Avatar } from "antd";
import {
  BankOutlined,
  TeamOutlined,
  SolutionOutlined,
  IdcardOutlined,
  ReloadOutlined,
  SafetyCertificateOutlined,
  RightOutlined,
  FilePdfOutlined
} from "@ant-design/icons";
import { useNavigate } from "react-router";
import { api } from "../services/api";
import { useAuthStore } from "../store/useAuthStore";
import { SEOHead } from "../components/SEOHead";

const { Title, Text } = Typography;

export default function Dashboard() {
  const navigate = useNavigate();
  const user = useAuthStore((state) => state.user);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<any>(null);
  const fetchedRef = useRef(false);

  const fetchStats = async () => {
    setLoading(true);
    try {
      const res = await api.get("/analytics/stats/");
      setStats(res.data);
    } catch (err) {
      message.error("Failed to load dashboard statistics");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (fetchedRef.current) return;
    fetchedRef.current = true;
    fetchStats();
  }, []);

  const handleResetSeed = async () => {
    try {
      await api.post("/analytics/reset-seed/");
      message.success("Database sample data re-seeded successfully!");
      fetchStats();
    } catch (err) {
      message.error("Failed to reset seed data");
    }
  };

  const columns = [
    {
      title: "User Profile",
      dataIndex: "full_name",
      key: "full_name",
      render: (text: string, record: any) => (
        <Space>
          <Avatar style={{ backgroundColor: "#1677ff", fontWeight: 600 }}>
            {text.charAt(0).toUpperCase()}
          </Avatar>
          <div>
            <div style={{ fontWeight: 600, fontSize: 14 }}>{text}</div>
            <div style={{ fontSize: 12, color: "#64748b" }}>{record.email}</div>
          </div>
        </Space>
      ),
    },
    {
      title: "System Role",
      dataIndex: "role",
      key: "role",
      render: (role: string) => {
        const colors: Record<string, string> = {
          admin: "magenta",
          company: "blue",
          employee: "green",
          "vendor.company": "purple",
          "vendor.employee": "orange",
        };
        return <Tag color={colors[role] || "default"} style={{ borderRadius: 6, fontWeight: 500 }}>{role}</Tag>;
      },
    },
    {
      title: "Assigned Organization",
      key: "organization",
      render: (_: any, record: any) => (
        <span style={{ fontWeight: 500, color: "#334155" }}>
          {record.company_name || record.vendor_company_name || "System Admin"}
        </span>
      ),
    },
    {
      title: "Designation",
      dataIndex: "designation",
      key: "designation",
      render: (text: string) => text || "Staff Member",
    },
  ];

  return (
    <main id="main-content">
      <SEOHead
        title="Dashboard & Enterprise Analytics"
        description="Workforce OS Dashboard: Real-time management metrics for client companies, employees, vendor staffing agencies, contractors, and policy RAG compliance."
        canonicalPath="/"
      />
      {/* Top Banner Header */}
      <div style={{
        marginBottom: 28,
        padding: "20px 24px",
        background: "linear-gradient(135deg, #0f172a 0%, #1e293b 100%)",
        borderRadius: 16,
        color: "#ffffff",
        display: "flex",
        flexDirection: "row",
        flexWrap: "wrap",
        justifyContent: "space-between",
        alignItems: "center",
        gap: 16,
        boxShadow: "0 10px 25px -5px rgba(15, 23, 42, 0.25)"
      }}>
        <div style={{ flex: 1, minWidth: 260 }}>
          <Space align="center" style={{ marginBottom: 6, flexWrap: "wrap" }}>
            <SafetyCertificateOutlined style={{ fontSize: 24, color: "#38bdf8" }} />
            <Title level={3} style={{ color: "#ffffff", margin: 0, fontWeight: 700, fontSize: "calc(1.1rem + 0.4vw)" }}>
              Welcome back, {user?.full_name}!
            </Title>
          </Space>
          <div style={{ color: "#94a3b8", fontSize: 13, flexWrap: "wrap" }}>
            Role: <Tag color="blue" style={{ marginLeft: 4 }}>{user?.role}</Tag> | Org: <span style={{ color: "#f1f5f9" }}>{user?.company_name || user?.vendor_company_name || "Global Administrator"}</span>
          </div>
        </div>

        <Space size="middle" style={{ flexWrap: "wrap" }}>
          <a href="/docs/Workforce_OS_Policy_Document.pdf" target="_blank" rel="noopener noreferrer">
            <Button icon={<FilePdfOutlined style={{ color: "#ff4d4f" }} />} style={{ borderRadius: 8, height: 38 }}>
              Policy PDF
            </Button>
          </a>
          <Button icon={<ReloadOutlined />} onClick={fetchStats} style={{ borderRadius: 8, height: 38 }}>
            Refresh
          </Button>
          {user?.role === "admin" && (
            <Popconfirm
              title="Reset Database Seed?"
              description="This will restore all sample companies, employees, and vendors to initial state."
              onConfirm={handleResetSeed}
              okText="Reset Data"
              cancelText="Cancel"
            >
              <Button type="primary" danger icon={<ReloadOutlined />} style={{ borderRadius: 8, height: 38 }}>
                Reset Seed
              </Button>
            </Popconfirm>
          )}
        </Space>
      </div>

      {loading ? (
        <div style={{ textAlign: "center", padding: 60 }}>
          <Spin size="large" />
        </div>
      ) : (
        <>
          {/* Stat Cards with Modern Gradients */}
          <Row gutter={[16, 16]} style={{ marginBottom: 28 }}>
            <Col xs={24} sm={12} lg={6}>
              <Card
                className="stat-card-gradient"
                style={{
                  background: "linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%)",
                  border: "1px solid #bfdbfe",
                  borderRadius: 16
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div>
                    <Text style={{ color: "#1e40af", fontWeight: 600, fontSize: 12 }}>TOTAL COMPANIES</Text>
                    <div style={{ fontSize: 28, fontWeight: 800, color: "#1e3a8a", marginTop: 4 }}>
                      {stats?.total_companies || 0}
                    </div>
                  </div>
                  <Avatar size={44} style={{ backgroundColor: "#2563eb", boxShadow: "0 4px 12px rgba(37,99,235,0.3)" }}>
                    <BankOutlined style={{ fontSize: 22 }} />
                  </Avatar>
                </div>
              </Card>
            </Col>

            <Col xs={24} sm={12} lg={6}>
              <Card
                className="stat-card-gradient"
                style={{
                  background: "linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%)",
                  border: "1px solid #bbf7d0",
                  borderRadius: 16
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div>
                    <Text style={{ color: "#166534", fontWeight: 600, fontSize: 12 }}>COMPANY EMPLOYEES</Text>
                    <div style={{ fontSize: 28, fontWeight: 800, color: "#14532d", marginTop: 4 }}>
                      {stats?.total_employees || 0}
                    </div>
                  </div>
                  <Avatar size={44} style={{ backgroundColor: "#16a34a", boxShadow: "0 4px 12px rgba(22,163,74,0.3)" }}>
                    <TeamOutlined style={{ fontSize: 22 }} />
                  </Avatar>
                </div>
              </Card>
            </Col>

            <Col xs={24} sm={12} lg={6}>
              <Card
                className="stat-card-gradient"
                style={{
                  background: "linear-gradient(135deg, #faf5ff 0%, #f3e8ff 100%)",
                  border: "1px solid #e9d5ff",
                  borderRadius: 16
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div>
                    <Text style={{ color: "#6b21a8", fontWeight: 600, fontSize: 12 }}>VENDOR AGENCIES</Text>
                    <div style={{ fontSize: 28, fontWeight: 800, color: "#581c87", marginTop: 4 }}>
                      {stats?.total_vendors || 0}
                    </div>
                  </div>
                  <Avatar size={44} style={{ backgroundColor: "#9333ea", boxShadow: "0 4px 12px rgba(147,51,234,0.3)" }}>
                    <SolutionOutlined style={{ fontSize: 22 }} />
                  </Avatar>
                </div>
              </Card>
            </Col>

            <Col xs={24} sm={12} lg={6}>
              <Card
                className="stat-card-gradient"
                style={{
                  background: "linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%)",
                  border: "1px solid #fed7aa",
                  borderRadius: 16
                }}
              >
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div>
                    <Text style={{ color: "#9a3412", fontWeight: 600, fontSize: 12 }}>VENDOR CONTRACTORS</Text>
                    <div style={{ fontSize: 28, fontWeight: 800, color: "#7c2d12", marginTop: 4 }}>
                      {stats?.total_vendor_employees || 0}
                    </div>
                  </div>
                  <Avatar size={44} style={{ backgroundColor: "#ea580c", boxShadow: "0 4px 12px rgba(234,88,12,0.3)" }}>
                    <IdcardOutlined style={{ fontSize: 22 }} />
                  </Avatar>
                </div>
              </Card>
            </Col>
          </Row>

          {/* Recent Activity Table Card */}
          <Card
            title={<span style={{ fontSize: 16, fontWeight: 700 }}>Recent Workforce Activity</span>}
            extra={
              <Button type="link" onClick={() => navigate("/employees")} style={{ fontWeight: 600 }}>
                View Personnel <RightOutlined />
              </Button>
            }
            style={{ borderRadius: 16 }}
          >
            <Table
              dataSource={stats?.recent_users || []}
              columns={columns}
              rowKey="id"
              pagination={false}
              scroll={{ x: 650 }}
            />
          </Card>
        </>
      )}
    </main>
  );
}
