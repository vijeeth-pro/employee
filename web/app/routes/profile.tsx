import React, { useState } from "react";
import { Card, Descriptions, Tag, Typography, Avatar, Row, Col, Form, Input, Button, message, Tabs, Space } from "antd";
import { UserOutlined, LockOutlined, MailOutlined, PhoneOutlined, BankOutlined, SafetyCertificateOutlined } from "@ant-design/icons";
import { useAuthStore } from "../store/useAuthStore";
import { api } from "../services/api";
import { SEOHead } from "../components/SEOHead";

const { Title, Text } = Typography;

export default function Profile() {
  const { user } = useAuthStore();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const handlePasswordUpdate = async (values: any) => {
    if (!user) return;
    setLoading(true);
    try {
      await api.put(`/users/${user.id}`, { password: values.password });
      message.success("Password updated successfully");
      form.resetFields();
    } catch (err) {
      message.error("Failed to update password");
    } finally {
      setLoading(false);
    }
  };

  const roleColors: Record<string, string> = {
    admin: "magenta",
    company: "blue",
    employee: "green",
    "vendor.company": "purple",
    "vendor.employee": "orange",
  };

  return (
    <main id="main-content">
      <SEOHead
        title="User Profile & Security Settings"
        description="View your user profile information, role permissions, organization details, and account security settings in Workforce OS."
        canonicalPath="/profile"
      />
      <h1>User Profile & Settings</h1>

      <Row gutter={[20, 20]}>
        <Col xs={24} lg={8}>
          <Card style={{ textAlign: "center", borderRadius: 12 }}>
            <Avatar
              size={88}
              icon={<UserOutlined />}
              style={{ backgroundColor: "#1677ff", marginBottom: 16 }}
            >
              {user?.full_name?.charAt(0).toUpperCase()}
            </Avatar>

            <Title level={4} style={{ margin: 0 }}>{user?.full_name}</Title>
            <Text type="secondary">{user?.designation || "Staff Member"}</Text>

            <div style={{ marginTop: 16 }}>
              <Tag color={roleColors[user?.role || ""] || "default"} style={{ padding: "4px 12px", fontSize: 13 }}>
                {user?.role?.toUpperCase()}
              </Tag>
            </div>

            <div style={{ marginTop: 24, textAlign: "left", fontSize: 13, borderTop: "1px solid #f0f0f0", paddingTop: 16 }}>
              <Space direction="vertical" style={{ width: "100%" }} size="middle">
                <div>
                  <MailOutlined style={{ marginRight: 8, color: "#1677ff" }} />
                  <span style={{ wordBreak: "break-all" }}>{user?.email}</span>
                </div>
                <div>
                  <PhoneOutlined style={{ marginRight: 8, color: "#52c41a" }} />
                  <span>{user?.phone || "No phone listed"}</span>
                </div>
                <div>
                  <BankOutlined style={{ marginRight: 8, color: "#722ed1" }} />
                  <span>{user?.company_name || user?.vendor_company_name || "System Admin"}</span>
                </div>
              </Space>
            </div>
          </Card>
        </Col>

        <Col xs={24} lg={16}>
          <Card style={{ borderRadius: 12 }}>
            <Tabs
              items={[
                {
                  key: "info",
                  label: "Account Information",
                  children: (
                    <Descriptions column={1} bordered style={{ marginTop: 8 }}>
                      <Descriptions.Item label="Full Name">{user?.full_name}</Descriptions.Item>
                      <Descriptions.Item label="Email Address">{user?.email}</Descriptions.Item>
                      <Descriptions.Item label="System Role">
                        <Tag color={roleColors[user?.role || ""]}>{user?.role}</Tag>
                      </Descriptions.Item>
                      <Descriptions.Item label="Designation">{user?.designation || "N/A"}</Descriptions.Item>
                      <Descriptions.Item label="Department">{user?.department || "N/A"}</Descriptions.Item>
                      <Descriptions.Item label="Assigned Organization">
                        {user?.company_name || user?.vendor_company_name || "Global Administrator"}
                      </Descriptions.Item>
                      <Descriptions.Item label="Account Status">
                        <Tag color="green">{user?.status?.toUpperCase()}</Tag>
                      </Descriptions.Item>
                    </Descriptions>
                  ),
                },
                {
                  key: "security",
                  label: "Security & Password",
                  children: (
                    <Form form={form} layout="vertical" onFinish={handlePasswordUpdate} style={{ maxWidth: 400, width: "100%", marginTop: 16 }}>
                      <Form.Item
                        name="password"
                        label="New Password"
                        rules={[{ required: true, message: "Enter new password" }, { min: 6, message: "At least 6 chars" }]}
                      >
                        <Input.Password prefix={<LockOutlined />} placeholder="New Password" />
                      </Form.Item>

                      <Form.Item>
                        <Button type="primary" htmlType="submit" loading={loading} icon={<SafetyCertificateOutlined />}>
                          Update Password
                        </Button>
                      </Form.Item>
                    </Form>
                  ),
                },
              ]}
            />
          </Card>
        </Col>
      </Row>
    </main>
  );
}
