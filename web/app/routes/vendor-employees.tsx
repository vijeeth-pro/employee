import React, { useEffect, useState, useRef } from "react";
import { Table, Button, Input, Modal, Form, Select, Tag, Space, Typography, Card, message, Popconfirm } from "antd";
import { PlusOutlined, SearchOutlined, EditOutlined, DeleteOutlined } from "@ant-design/icons";
import { api } from "../services/api";
import { useAuthStore } from "../store/useAuthStore";
import { SEOHead } from "../components/SEOHead";

const { Title } = Typography;
const { Option } = Select;

export default function VendorEmployees() {
  const user = useAuthStore((state) => state.user);
  const [vendorEmployees, setVendorEmployees] = useState<any[]>([]);
  const [vendorCompanies, setVendorCompanies] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState("");
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingItem, setEditingItem] = useState<any>(null);
  const [form] = Form.useForm();
  const fetchedRef = useRef(false);

  const fetchVendorEmployees = async () => {
    setLoading(true);
    try {
      const res = await api.get("/vendor-employees/");
      setVendorEmployees(res.data);
    } catch (err) {
      message.error("Failed to fetch vendor employees");
    } finally {
      setLoading(false);
    }
  };

  const fetchVendorCompanies = async () => {
    try {
      const res = await api.get("/vendor-companies/");
      setVendorCompanies(res.data);
    } catch (err) {}
  };

  useEffect(() => {
    if (fetchedRef.current) return;
    fetchedRef.current = true;
    fetchVendorEmployees();
    fetchVendorCompanies();
  }, []);

  const handleCreateOrUpdate = async (values: any) => {
    try {
      if (editingItem) {
        await api.put(`/users/${editingItem.id}`, values);
        message.success("Vendor employee updated");
      } else {
        await api.post("/vendor-employees/", values);
        message.success("Vendor employee created");
      }
      setIsModalOpen(false);
      form.resetFields();
      setEditingItem(null);
      fetchVendorEmployees();
    } catch (err: any) {
      message.error(err.response?.data?.detail || "Operation failed");
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await api.delete(`/users/${id}`);
      message.success("Vendor employee deleted");
      fetchVendorEmployees();
    } catch (err) {
      message.error("Failed to delete");
    }
  };

  const openCreateModal = () => {
    setEditingItem(null);
    form.resetFields();
    setIsModalOpen(true);
  };

  const openEditModal = (record: any) => {
    setEditingItem(record);
    form.setFieldsValue({
      full_name: record.full_name,
      email: record.email,
      phone: record.phone,
      designation: record.designation,
      department: record.department,
      vendor_company_id: record.vendor_company_id,
      status: record.status,
    });
    setIsModalOpen(true);
  };

  const filteredData = vendorEmployees.filter(ve =>
    ve.full_name?.toLowerCase().includes(searchText.toLowerCase()) ||
    ve.email?.toLowerCase().includes(searchText.toLowerCase()) ||
    ve.vendor_company_name?.toLowerCase().includes(searchText.toLowerCase())
  );

  const columns = [
    {
      title: "Contractor Name",
      dataIndex: "full_name",
      key: "full_name",
      render: (text: string, record: any) => (
        <Space direction="vertical" size={0}>
          <strong>{text}</strong>
          <span style={{ fontSize: 12, color: "#8c8c8c" }}>{record.email}</span>
        </Space>
      ),
    },
    {
      title: "Vendor Agency",
      dataIndex: "vendor_company_name",
      key: "vendor_company_name",
      render: (text: string) => <Tag color="purple">{text || "N/A"}</Tag>,
    },
    {
      title: "Role & Designation",
      key: "designation",
      render: (_: any, record: any) => (
        <span>{record.designation || "Contractor"} ({record.department || "Consulting"})</span>
      ),
    },
    {
      title: "Phone",
      dataIndex: "phone",
      key: "phone",
      render: (text: string) => text || "N/A",
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
          {(user?.role === "admin" || user?.role === "vendor.company") && (
            <Popconfirm title="Delete vendor employee?" onConfirm={() => handleDelete(record.id)}>
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
    <main id="main-content">
      <SEOHead
        title="Vendor Contractors & Staff"
        description="Manage external vendor contractors, client allocations, timesheet compliance, and security clearance."
        canonicalPath="/vendor-employees"
      />
      <div style={{ marginBottom: 20, display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: 12 }}>
        <div>
          <h1>Vendor Employees & Contractors</h1>
          <span style={{ color: "#64748b", fontSize: 13 }}>External vendor agency contractors and deployed personnel</span>
        </div>

        {(user?.role === "admin" || user?.role === "vendor.company") && (
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreateModal}>
            Add Vendor Contractor
          </Button>
        )}
      </div>

      <Card style={{ borderRadius: 12 }}>
        <div style={{ marginBottom: 16, maxWidth: 320, width: "100%" }}>
          <Input
            placeholder="Search contractor name, vendor..."
            prefix={<SearchOutlined />}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            allowClear
          />
        </div>

        <Table dataSource={filteredData} columns={columns} rowKey="id" loading={loading} pagination={{ pageSize: 8 }} scroll={{ x: 750 }} />
      </Card>

      <Modal
        title={editingItem ? "Edit Vendor Contractor" : "Add Vendor Contractor"}
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        footer={null}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleCreateOrUpdate}>
          <Form.Item name="full_name" label="Full Name" rules={[{ required: true }]}>
            <Input placeholder="Sarah Jenkins" />
          </Form.Item>
          <Form.Item name="email" label="Email Address" rules={[{ required: true, type: "email" }]}>
            <Input placeholder="sarah@techserve.com" disabled={!!editingItem} />
          </Form.Item>

          {!editingItem && (
            <Form.Item name="password" label="Initial Password" rules={[{ required: true }]}>
              <Input.Password placeholder="Password" />
            </Form.Item>
          )}

          {user?.role === "admin" && (
            <Form.Item name="vendor_company_id" label="Vendor Company Agency" rules={[{ required: true }]}>
              <Select placeholder="Select Vendor Agency">
                {vendorCompanies.map((v) => (
                  <Option key={v.id} value={v.id}>{v.name}</Option>
                ))}
              </Select>
            </Form.Item>
          )}

          <Form.Item name="designation" label="Designation">
            <Input placeholder="Senior DevOps Consultant" />
          </Form.Item>
          <Form.Item name="department" label="Department">
            <Input placeholder="Cloud Infrastructure" />
          </Form.Item>

          <Form.Item name="phone" label="Phone">
            <Input placeholder="+1 555 088 8888" />
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: "right" }}>
            <Space>
              <Button onClick={() => setIsModalOpen(false)}>Cancel</Button>
              <Button type="primary" htmlType="submit">Save</Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </main>
  );
}
