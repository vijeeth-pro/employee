import React, { useEffect, useState, useRef } from "react";
import { Table, Button, Input, Modal, Form, Tag, Space, Typography, Card, message, Popconfirm, Select } from "antd";
import { PlusOutlined, SearchOutlined, EditOutlined, DeleteOutlined, LinkOutlined } from "@ant-design/icons";
import { api } from "../services/api";
import { useAuthStore } from "../store/useAuthStore";

const { Title } = Typography;
const { Option } = Select;

export default function VendorCompanies() {
  const user = useAuthStore((state) => state.user);
  const [vendors, setVendors] = useState<any[]>([]);
  const [companies, setCompanies] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState("");
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isAssignModalOpen, setIsAssignModalOpen] = useState(false);
  const [selectedVendor, setSelectedVendor] = useState<any>(null);
  
  const [form] = Form.useForm();
  const [assignForm] = Form.useForm();
  const fetchedRef = useRef(false);

  const fetchVendors = async () => {
    setLoading(true);
    try {
      const res = await api.get("/vendor-companies/");
      setVendors(res.data);
    } catch (err) {
      message.error("Failed to fetch vendor companies");
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
    fetchVendors();
    fetchCompanies();
  }, []);

  const handleCreateOrUpdate = async (values: any) => {
    try {
      if (selectedVendor && isModalOpen) {
        await api.put(`/vendor-companies/${selectedVendor.id}`, values);
        message.success("Vendor company updated");
      } else {
        await api.post("/vendor-companies/", values);
        message.success("Vendor company created");
      }
      setIsModalOpen(false);
      form.resetFields();
      setSelectedVendor(null);
      fetchVendors();
    } catch (err: any) {
      message.error(err.response?.data?.detail || "Operation failed");
    }
  };

  const handleAssignVendor = async (values: { company_id: number }) => {
    if (!selectedVendor) return;
    try {
      await api.post(`/vendor-companies/${selectedVendor.id}/assign-company/${values.company_id}`);
      message.success("Vendor successfully assigned to company");
      setIsAssignModalOpen(false);
      assignForm.resetFields();
      fetchVendors();
    } catch (err) {
      message.error("Failed to assign vendor");
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await api.delete(`/vendor-companies/${id}`);
      message.success("Vendor company deleted");
      fetchVendors();
    } catch (err) {
      message.error("Failed to delete vendor company");
    }
  };

  const filteredData = vendors.filter(v =>
    v.name?.toLowerCase().includes(searchText.toLowerCase()) ||
    v.code?.toLowerCase().includes(searchText.toLowerCase()) ||
    v.service_type?.toLowerCase().includes(searchText.toLowerCase())
  );

  const columns = [
    {
      title: "Vendor Company",
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
      title: "Service Type",
      dataIndex: "service_type",
      key: "service_type",
      render: (text: string) => <Tag color="purple">{text || "Consulting"}</Tag>,
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
      title: "Contractors",
      dataIndex: "employee_count",
      key: "employee_count",
      render: (count: number) => <Tag color="gold">{count || 0} Active Staff</Tag>,
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
          {(user?.role === "admin" || user?.role === "company") && (
            <Button
              icon={<LinkOutlined />}
              size="small"
              onClick={() => {
                setSelectedVendor(record);
                setIsAssignModalOpen(true);
              }}
            >
              Assign Company
            </Button>
          )}
          <Button
            icon={<EditOutlined />}
            size="small"
            onClick={() => {
              setSelectedVendor(record);
              form.setFieldsValue(record);
              setIsModalOpen(true);
            }}
          >
            Edit
          </Button>
          {user?.role === "admin" && (
            <Popconfirm title="Delete vendor company?" onConfirm={() => handleDelete(record.id)}>
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
          <Title level={3} style={{ margin: 0 }}>Vendor Companies</Title>
          <span>Third-party vendor partners and contractor agencies</span>
        </div>

        {(user?.role === "admin" || user?.role === "company") && (
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => {
              setSelectedVendor(null);
              form.resetFields();
              setIsModalOpen(true);
            }}
          >
            Register Vendor
          </Button>
        )}
      </div>

      <Card style={{ borderRadius: 12 }}>
        <div style={{ marginBottom: 16, maxWidth: 320 }}>
          <Input
            placeholder="Search vendor name, code..."
            prefix={<SearchOutlined />}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            allowClear
          />
        </div>

        <Table dataSource={filteredData} columns={columns} rowKey="id" loading={loading} pagination={{ pageSize: 8 }} />
      </Card>

      {/* Vendor Create/Edit Modal */}
      <Modal
        title={selectedVendor ? "Edit Vendor Company" : "Register Vendor Company"}
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        footer={null}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleCreateOrUpdate}>
          <Form.Item name="name" label="Vendor Company Name" rules={[{ required: true }]}>
            <Input placeholder="TechServe Solutions Ltd." />
          </Form.Item>
          <Form.Item name="code" label="Vendor Code" rules={[{ required: true }]}>
            <Input placeholder="VEND-TECHSERVE" disabled={!!selectedVendor} />
          </Form.Item>
          <Form.Item name="email" label="Email" rules={[{ required: true, type: "email" }]}>
            <Input placeholder="support@techserve.com" />
          </Form.Item>

          <Form.Item name="service_type" label="Service Type">
            <Input placeholder="IT Staffing & Consulting" />
          </Form.Item>

          <Form.Item name="phone" label="Phone">
            <Input placeholder="+1 (555) 088-3411" />
          </Form.Item>

          <Form.Item name="address" label="Address">
            <Input.TextArea placeholder="Austin, TX" rows={2} />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: "right" }}>
            <Space>
              <Button onClick={() => setIsModalOpen(false)}>Cancel</Button>
              <Button type="primary" htmlType="submit">Save</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* Assign Vendor Modal */}
      <Modal
        title={`Assign ${selectedVendor?.name || "Vendor"} to Client Company`}
        open={isAssignModalOpen}
        onCancel={() => setIsAssignModalOpen(false)}
        footer={null}
        destroyOnClose
      >
        <Form form={assignForm} layout="vertical" onFinish={handleAssignVendor}>
          <Form.Item name="company_id" label="Select Client Company" rules={[{ required: true }]}>
            <Select placeholder="Choose Company">
              {companies.map((c) => (
                <Option key={c.id} value={c.id}>{c.name} ({c.code})</Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: "right" }}>
            <Space>
              <Button onClick={() => setIsAssignModalOpen(false)}>Cancel</Button>
              <Button type="primary" htmlType="submit">Assign Contract</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
