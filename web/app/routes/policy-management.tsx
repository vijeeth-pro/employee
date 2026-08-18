import React, { useEffect, useState, useRef } from "react";
import { Table, Button, Input, Modal, Form, Select, Tag, Space, Typography, Card, message, Popconfirm, Upload, Spin, Badge } from "antd";
import { PlusOutlined, UploadOutlined, DeleteOutlined, FilePdfOutlined, BookOutlined, CheckCircleOutlined } from "@ant-design/icons";
import { api } from "../services/api";
import { useAuthStore } from "../store/useAuthStore";
import { SEOHead } from "../components/SEOHead";

const { Title, Text } = Typography;
const { Option } = Select;

export default function PolicyManagement() {
  const user = useAuthStore((state) => state.user);
  const [policies, setPolicies] = useState<any[]>([]);
  const [companies, setCompanies] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [fileList, setFileList] = useState<any[]>([]);
  const [form] = Form.useForm();
  const fetchedRef = useRef(false);

  const fetchPolicies = async () => {
    setLoading(true);
    try {
      const res = await api.get("/policy/");
      setPolicies(res.data);
    } catch (err) {
      message.error("Failed to fetch policy documents");
    } finally {
      setLoading(false);
    }
  };

  const fetchCompanies = async () => {
    try {
      const res = await api.get("/companies/");
      setCompanies(res.data);
    } catch (err) {}
  };

  useEffect(() => {
    if (fetchedRef.current) return;
    fetchedRef.current = true;
    fetchPolicies();
    if (user?.role === "admin") {
      fetchCompanies();
    }
  }, [user]);

  const handleUploadPolicy = async (values: any) => {
    if (fileList.length === 0) {
      message.error("Please select a policy PDF/TXT document to upload.");
      return;
    }

    setUploading(true);
    const formData = new FormData();
    formData.append("title", values.title);
    formData.append("category", values.category || "General Policy");
    if (values.company_id) {
      formData.append("company_id", values.company_id);
    }
    formData.append("file", fileList[0].originFileObj || fileList[0]);

    try {
      await api.post("/policy/upload", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });
      message.success("Policy uploaded, vectorized, and stored in Pinecone DB successfully!");
      setIsModalOpen(false);
      form.resetFields();
      setFileList([]);
      fetchPolicies();
    } catch (err: any) {
      message.error(err.response?.data?.detail || "Policy upload failed.");
    } finally {
      setUploading(false);
    }
  };

  const handleDeletePolicy = async (id: number) => {
    try {
      await api.delete(`/policy/${id}`);
      message.success("Policy document deleted.");
      fetchPolicies();
    } catch (err) {
      message.error("Failed to delete policy.");
    }
  };

  const columns = [
    {
      title: "Document Title",
      dataIndex: "title",
      key: "title",
      render: (text: string, record: any) => (
        <Space>
          <FilePdfOutlined style={{ fontSize: 20, color: "#ff4d4f" }} />
          <div>
            <div style={{ fontWeight: 600, fontSize: 14 }}>{text}</div>
            <div style={{ fontSize: 12, color: "#64748b" }}>{record.file_name || "Text Entry"}</div>
          </div>
        </Space>
      ),
    },
    {
      title: "Category",
      dataIndex: "category",
      key: "category",
      render: (cat: string) => <Tag color="blue">{cat || "General Policy"}</Tag>,
    },
    {
      title: "Vector Status",
      key: "vector",
      render: (_: any, record: any) => (
        <Space>
          <Tag color="green" icon={<CheckCircleOutlined />}>Pinecone Vectorized</Tag>
          <Badge count={`${record.chunk_count || 1} Chunks`} style={{ backgroundColor: "#10b981" }} />
        </Space>
      ),
    },
    {
      title: "File Size",
      dataIndex: "file_size",
      key: "file_size",
      render: (size: number) => size ? `${(size / 1024).toFixed(1)} KB` : "N/A",
    },
    {
      title: "Created At",
      dataIndex: "created_at",
      key: "created_at",
      render: (date: string) => new Date(date).toLocaleDateString(),
    },
    {
      title: "Actions",
      key: "actions",
      render: (_: any, record: any) => (
        <Popconfirm
          title="Delete policy document?"
          description="This will remove the policy and its vectors from Pinecone."
          onConfirm={() => handleDeletePolicy(record.id)}
          okText="Delete"
          cancelText="Cancel"
        >
          <Button icon={<DeleteOutlined />} danger size="small">
            Delete
          </Button>
        </Popconfirm>
      ),
    },
  ];

  return (
    <main id="main-content">
      <SEOHead
        title="Policy RAG Knowledge Base"
        description="Upload corporate policy manuals and vectorize guidelines with Google Gemini & Pinecone Vector RAG."
        canonicalPath="/policy-management"
      />
      <div style={{ marginBottom: 20, display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
        <div>
          <h1>Company Policy Documents & RAG Knowledge Base</h1>
          <span style={{ color: "#64748b", fontSize: 13 }}>Upload corporate policies to train the Gemini & Pinecone Vector AI Assistant</span>
        </div>

        {(user?.role === "admin" || user?.role === "company" || user?.role === "vendor.company") && (
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setIsModalOpen(true)}>
            Upload Policy PDF
          </Button>
        )}
      </div>

      <Card style={{ borderRadius: 12 }}>
        <Table
          dataSource={policies}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 8 }}
          scroll={{ x: 750 }}
        />
      </Card>

      {/* Upload Policy Modal */}
      <Modal
        title="Upload Corporate Policy Document to Vector DB"
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        footer={null}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleUploadPolicy}>
          <Form.Item
            name="title"
            label="Policy Title"
            rules={[{ required: true, message: "Please enter policy title" }]}
          >
            <Input placeholder="Apex Employee Leave & Time-Off Policy 2026" />
          </Form.Item>

          <Form.Item
            name="category"
            label="Category Tag"
            initialValue="Leave Policy"
          >
            <Select>
              <Option value="Leave Policy">Leave & Vacation Policy</Option>
              <Option value="Remote Work">Remote & Hybrid Work Rules</Option>
              <Option value="Expenses">Expenses & Reimbursements</Option>
              <Option value="Vendor Guidelines">Vendor & Contractor Rules</Option>
              <Option value="Compliance">Compliance & Security</Option>
              <Option value="General Policy">General Governance Policy</Option>
            </Select>
          </Form.Item>

          {user?.role === "admin" && (
            <Form.Item name="company_id" label="Scope to Client Company (Optional)">
              <Select placeholder="All Companies (Global)">
                {companies.map((c) => (
                  <Option key={c.id} value={c.id}>{c.name}</Option>
                ))}
              </Select>
            </Form.Item>
          )}

          <Form.Item label="Upload PDF / TXT File" required>
            <Upload
              beforeUpload={() => false}
              fileList={fileList}
              onChange={({ fileList }) => setFileList(fileList)}
              maxCount={1}
              accept=".pdf,.txt,.md"
            >
              <Button icon={<UploadOutlined />}>Select Policy File (.pdf, .txt)</Button>
            </Upload>
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: "right" }}>
            <Space>
              <Button onClick={() => setIsModalOpen(false)}>Cancel</Button>
              <Button type="primary" htmlType="submit" loading={uploading} icon={<BookOutlined />}>
                Upload & Vectorize Document
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </main>
  );
}
