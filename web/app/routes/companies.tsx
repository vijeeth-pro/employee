import React, { useEffect, useState, useRef } from "react";
import { Table, Button, Input, Modal, Form, Tag, Space, Typography, Card, message, Popconfirm, Badge } from "antd";
import { PlusOutlined, SearchOutlined, EditOutlined, DeleteOutlined } from "@ant-design/icons";
import { api } from "../services/api";
import { useAuthStore } from "../store/useAuthStore";

const { Title } = Typography;

export default function Companies() {
  const user = useAuthStore((state) => state.user);
  const [companies, setCompanies] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingCompany, setEditingCompany] = useState<any>(null);
  const [form] = Form.useForm();
  const fetchedRef = useRef(false);

  const fetchCompanies = async () => {
    setLoading(true);
    try {
      const res = await api.get("/companies/");
      setCompanies(res.data);
    } catch (err) {
      message.error("Failed to fetch companies");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (fetchedRef.current) return;
    fetchedRef.current = true;
    fetchCompanies();
  }, []);

  const handleCreateOrUpdate = async (values: any) => {
    try {
      if (editingCompany) {
        await api.put(`/companies/${editingCompany.id}`, values);
        message.success("Company updated successfully");
      } else {
        await api.post("/companies/", values);
        message.success("Company created successfully");
      }
      setIsModalOpen(false);
      form.resetFields();
      setEditingCompany(null);
      fetchCompanies();
    } catch (err: any) {
      message.error(err.response?.data?.detail || "Operation failed");
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await api.delete(`/companies/${id}`);
      message.success("Company deleted");
      fetchCompanies();
    } catch (err) {
      message.error("Failed to delete company");
    }
  };

  const openCreateModal = () => {
    setEditingCompany(null);
    form.resetFields();
    setIsModalOpen(true);
  };

  const openEditModal = (record: any) => {
    setEditingCompany(record);
    form.setFieldsValue({
      name: record.name,
      code: record.code,
      email: record.email,
      phone: record.phone,
      address: record.address,
      industry: record.industry,
      status: record.status,
    });
    setIsModalOpen(true);
  };

  const filteredData = companies.filter(c =>
    c.name?.toLowerCase().includes(searchText.toLowerCase()) ||
    c.code?.toLowerCase().includes(searchText.toLowerCase()) ||
    c.industry?.toLowerCase().includes(searchText.toLowerCase())
  );

  const columns = [
    {
      title: "Company Name",
      dataIndex: "name",
      key: "name",
      render: (text: string, record: any) => (
        <Space direction="vertical" size={0}>
          <strong>{text}</strong>
          <span style={{ fontSize: 12, color: "#8c8c8c" }}>Code: {record.code}</span>
        </Space>
      ),
    },
    {
      title: "Industry",
      dataIndex: "industry",
      key: "industry",
      render: (text: string) => <Tag color="geekblue">{text || "Technology"}</Tag>,
    },
    {
      title: "Contact Info",
      key: "contact",
      render: (_: any, record: any) => (
        <div style={{ fontSize: 13 }}>
          <div>{record.email}</div>
          <div style={{ color: "#8c8c8c" }}>{record.phone}</div>
        </div>
      ),
    },
    {
      title: "Employees & Vendors",
      key: "counts",
      render: (_: any, record: any) => (
        <Space size="middle">
          <Badge count={record.employee_count || 0} showZero overflowCount={999} style={{ backgroundColor: "#52c41a" }} title="Employees" />
          <span style={{ fontSize: 12, color: "#8c8c8c" }}>Employees</span>
          <Badge count={record.vendor_count || 0} showZero overflowCount={999} style={{ backgroundColor: "#722ed1" }} title="Vendors" />
          <span style={{ fontSize: 12, color: "#8c8c8c" }}>Vendors</span>
        </Space>
      ),
    },
    {
      title: "Status",
      dataIndex: "status",
      key: "status",
      render: (status: string) => (
        <Tag color={status === "active" ? "green" : "volcano"}>{status?.toUpperCase()}</Tag>
      ),
    },
    {
      title: "Actions",
      key: "actions",
      render: (_: any, record: any) => (
        <Space>
          <Button icon={<EditOutlined />} size="small" onClick={() => openEditModal(record)}>
            Edit
          </Button>
          {user?.role === "admin" && (
            <Popconfirm
              title="Delete company?"
              onConfirm={() => handleDelete(record.id)}
              okText="Yes"
              cancelText="No"
            >
              <Button icon={<DeleteOutlined />} danger size="small">
                Delete
              </Button>
            </Popconfirm>
          )}
        </Space>
      ),
    },
  ];

  return (
    <>
      <div style={{ marginBottom: 20, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <Title level={3} style={{ margin: 0 }}>Company Organizations</Title>
          <span>Maintain client & enterprise company registrations</span>
        </div>

        {user?.role === "admin" && (
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreateModal}>
            Register Company
          </Button>
        )}
      </div>

      <Card style={{ borderRadius: 12 }}>
        <div style={{ marginBottom: 16, maxWidth: 320 }}>
          <Input
            placeholder="Search company by name, code..."
            prefix={<SearchOutlined />}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            allowClear
          />
        </div>

        <Table
          dataSource={filteredData}
          columns={columns}
          rowKey="id"
          loading={loading}
          pagination={{ pageSize: 8 }}
        />
      </Card>

      <Modal
        title={editingCompany ? "Edit Company" : "Register New Company"}
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        footer={null}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleCreateOrUpdate}>
          <Form.Item name="name" label="Company Name" rules={[{ required: true, message: "Enter company name" }]}>
            <Input placeholder="Apex Technologies Inc." />
          </Form.Item>

          <Form.Item name="code" label="Company Code" rules={[{ required: true, message: "Enter code" }]}>
            <Input placeholder="COMP-APEX" disabled={!!editingCompany} />
          </Form.Item>

          <Form.Item name="email" label="Contact Email" rules={[{ required: true, type: "email" }]}>
            <Input placeholder="info@apextech.com" />
          </Form.Item>

          <Form.Item name="phone" label="Phone">
            <Input placeholder="+1 (555) 019-2831" />
          </Form.Item>

          <Form.Item name="industry" label="Industry" initialValue="Technology">
            <Input placeholder="Software & AI" />
          </Form.Item>

          <Form.Item name="address" label="Address">
            <Input.TextArea placeholder="San Francisco, CA" rows={2} />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: "right" }}>
            <Space>
              <Button onClick={() => setIsModalOpen(false)}>Cancel</Button>
              <Button type="primary" htmlType="submit">
                {editingCompany ? "Save Changes" : "Create Company"}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
