import React, { useEffect } from "react";
import { Form, Input, Button, Card, Typography, Alert, Space, Tag, Divider, Spin, message } from "antd";
import { UserOutlined, LockOutlined, SafetyCertificateOutlined, CheckCircleOutlined } from "@ant-design/icons";
import { useNavigate, Navigate } from "react-router";
import { useAuthStore } from "../store/useAuthStore";

const { Title, Text } = Typography;

export default function Login() {
  const navigate = useNavigate();
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const isInitialized = useAuthStore((state) => state.isInitialized);
  const login = useAuthStore((state) => state.login);
  const isFormSubmitting = useAuthStore((state) => state.isLoading);
  const error = useAuthStore((state) => state.error);
  
  const [form] = Form.useForm();

  useEffect(() => {
    useAuthStore.getState().fetchCurrentUser();
  }, []);

  // 1. If valid JWT cookie exists and user is authenticated, redirect to dashboard
  if (isAuthenticated && isInitialized) {
    return <Navigate to="/" replace />;
  }

  // 2. While initial session check is running in background
  if (!isInitialized) {
    return (
      <div style={{
        minHeight: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        background: "linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)"
      }}>
        <Spin size="large" />
      </div>
    );
  }

  const onFinish = async (values: { email: string; password: string }) => {
    try {
      await login(values.email, values.password);
      message.success("Successfully logged in!");
      navigate("/");
    } catch (err: any) {
      // Error handled by store
    }
  };

  const handleQuickLogin = (email: string, pass: string) => {
    form.setFieldsValue({ email, password: pass });
    onFinish({ email, password: pass });
  };

  const demoAccounts = [
    { title: "System Admin", email: "admin@system.com", pass: "admin123", role: "admin", color: "magenta" },
    { title: "Company Admin", email: "company@apex.com", pass: "company123", role: "company", color: "blue" },
    { title: "Company Employee", email: "employee@apex.com", pass: "emp123", role: "employee", color: "green" },
    { title: "Vendor Admin", email: "vendor@techserve.com", pass: "vendor123", role: "vendor.company", color: "purple" },
    { title: "Vendor Contractor", email: "vendoremp@techserve.com", pass: "vemp123", role: "vendor.employee", color: "orange" },
  ];

  return (
    <div style={{
      minHeight: "100vh",
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      background: "linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%)",
      padding: "24px",
    }}>
      <Card
        style={{
          width: "100%",
          maxWidth: 480,
          borderRadius: 16,
          boxShadow: "0 20px 40px rgba(0,0,0,0.3)",
          border: "1px solid rgba(255,255,255,0.1)",
        }}
      >
        <div style={{ textAlign: "center", marginBottom: 24 }}>
          <SafetyCertificateOutlined style={{ fontSize: 44, color: "#1677ff" }} />
          <Title level={3} style={{ marginTop: 12, marginBottom: 4 }}>Workforce OS</Title>
          <Text type="secondary">Enterprise Employee & Vendor Management Portal</Text>
        </div>

        {error && (
          <Alert message={error} type="error" showIcon style={{ marginBottom: 20 }} />
        )}

        <Form
          form={form}
          name="login_form"
          initialValues={{ remember: true }}
          onFinish={onFinish}
          layout="vertical"
          size="large"
        >
          <Form.Item
            name="email"
            rules={[
              { required: true, message: "Please input your Email!" },
              { type: "email", message: "Please enter a valid email address!" }
            ]}
          >
            <Input prefix={<UserOutlined />} placeholder="Email Address" />
          </Form.Item>

          <Form.Item
            name="password"
            rules={[{ required: true, message: "Please input your Password!" }]}
          >
            <Input.Password prefix={<LockOutlined />} placeholder="Password" />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={isFormSubmitting} block size="large" style={{ borderRadius: 8 }}>
              Log In
            </Button>
          </Form.Item>
        </Form>

        <Divider style={{ margin: "16px 0", fontSize: 12, color: "#8c8c8c" }}>
          One-Click Demo Account Quick Login
        </Divider>

        <Space direction="vertical" style={{ width: "100%" }} size="small">
          {demoAccounts.map((acc) => (
            <Button
              key={acc.role}
              onClick={() => handleQuickLogin(acc.email, acc.pass)}
              block
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                height: 40,
                borderRadius: 8
              }}
            >
              <Space>
                <CheckCircleOutlined style={{ color: "#52c41a" }} />
                <span>{acc.title}</span>
              </Space>
              <Tag color={acc.color}>{acc.role}</Tag>
            </Button>
          ))}
        </Space>
      </Card>
    </div>
  );
}
