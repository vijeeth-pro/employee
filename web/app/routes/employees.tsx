import React, { useEffect, useState, useRef } from "react";
import { Table, Button, Input, Modal, Form, Select, Tag, Space, Typography, Card, message, Popconfirm } from "antd";
import { PlusOutlined, SearchOutlined, EditOutlined, DeleteOutlined } from "@ant-design/icons";
import { api } from "../services/api";
import { useAuthStore } from "../store/useAuthStore";

const { Title } = Typography;
const { Option } = Select;

export default function Employees() {
  const user = useAuthStore((state) => state.user);
  const [employees, setEmployees] = useState<any[]>([]);
  const [companies, setCompanies] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchText, setSearchText] = useState("");
  
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingEmployee, setEditingEmployee] = useState<any>(null);
  const [form] = Form.useForm();
  const fetchedRef = useRef(false);

  const fetchEmployees = async () => {
    setLoading(true);
    try {
      const res = await api.get("/employees/");
      setEmployees(res.data);
    } catch (err) {
      message.error("Failed to fetch employees");
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
    fetchEmployees();
    fetchCompanies();
  }, []);

  const handleCreateOrUpdate = async (values: any) => {
    try {
      if (editingEmployee) {
        await api.put(`/users/${editingEmployee.id}`, values);
        message.success("Employee updated successfully");
      } else {
        await api.post("/employees/", values);
        message.success("Employee created successfully");
      }
      setIsModalOpen(false);
      form.resetFields();
      setEditingEmployee(null);
      fetchEmployees();
    } catch (err: any) {
      message.error(err.response?.data?.detail || "Operation failed");
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await api.delete(`/users/${id}`);
      message.success("Employee deleted");
      fetchEmployees();
    } catch (err: any) {
      message.error("Failed to delete employee");
    }
  };

  const openCreateModal = () => {
    setEditingEmployee(null);
    form.resetFields();
    setIsModalOpen(true);
  };

  const openEditModal = (record: any) => {
    setEditingEmployee(record);
    form.setFieldsValue({
      full_name: record.full_name,
      email: record.email,
      phone: record.phone,
      designation: record.designation,
      department: record.department,
      company_id: record.company_id,
      status: record.status,
    });
    setIsModalOpen(true);
  };

  const filteredData = employees.filter((emp) =>
    emp.full_name?.toLowerCase().includes(searchText.toLowerCase()) ||
    emp.email?.toLowerCase().includes(searchText.toLowerCase()) ||
    emp.department?.toLowerCase().includes(searchText.toLowerCase())
  );

  const columns = [
    {
      title: "Employee Name",
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
      title: "Designation & Dept",
      key: "designation",
      render: (_: any, record: any) => (
        <span>
          {record.designation || "N/A"} <Tag color="blue">{record.department || "General"}</Tag>
        </span>
      ),
    },
    {
      title: "Company",
      dataIndex: "company_name",
      key: "company_name",
      render: (text: string) => text || "N/A",
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
          {(user?.role === "admin" || user?.role === "company") && (
            <Popconfirm
              title="Delete employee?"
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
          <Title level={3} style={{ margin: 0 }}>Company Employees</Title>
          <span>Manage internal organization workforce and employee details</span>
        </div>

        {(user?.role === "admin" || user?.role === "company") && (
          <Button type="primary" icon={<PlusOutlined />} onClick={openCreateModal}>
            Add Employee
          </Button>
        )}
      </div>

      <Card style={{ borderRadius: 12 }}>
        <div style={{ marginBottom: 16, maxWidth: 320 }}>
          <Input
            placeholder="Search by name, email, dept..."
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
        title={editingEmployee ? "Edit Employee" : "Add New Employee"}
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        footer={null}
        destroyOnClose
      >
        <Form form={form} layout="vertical" onFinish={handleCreateOrUpdate}>
          <Form.Item
            name="full_name"
            label="Full Name"
            rules={[{ required: true, message: "Please enter full name" }]}
          >
            <Input placeholder="John Doe" />
          </Form.Item>

          <Form.Item
            name="email"
            label="Email Address"
            rules={[
              { required: true, message: "Please enter email" },
              { type: "email", message: "Enter a valid email" }
            ]}
          >
            <Input placeholder="john@apex.com" disabled={!!editingEmployee} />
          </Form.Item>

          {!editingEmployee && (
            <Form.Item
              name="password"
              label="Initial Password"
              rules={[{ required: true, message: "Please set password" }]}
            >
              <Input.Password placeholder="Password" />
            </Form.Item>
          )}

          {user?.role === "admin" && (
            <Form.Item
              name="company_id"
              label="Assign to Company"
              rules={[{ required: true, message: "Please select company" }]}
            >
              <Select placeholder="Select Company">
                {companies.map((c) => (
                  <Option key={c.id} value={c.id}>{c.name}</Option>
                ))}
              </Select>
            </Form.Item>
          )}

          <Form.Item name="designation" label="Designation">
            <Input placeholder="Software Engineer" />
          </Form.Item>

          <Form.Item name="department" label="Department">
            <Input placeholder="Engineering" />
          </Form.Item>

          <Form.Item name="phone" label="Phone Number">
            <Input placeholder="+1 555 019 2831" />
          </Form.Item>

          <Form.Item name="status" label="Status" initialValue="active">
            <Select>
              <Option value="active">Active</Option>
              <Option value="inactive">Inactive</Option>
            </Select>
          </Form.Item>

          <Form.Item style={{ marginBottom: 0, textAlign: "right" }}>
            <Space>
              <Button onClick={() => setIsModalOpen(false)}>Cancel</Button>
              <Button type="primary" htmlType="submit">
                {editingEmployee ? "Save Changes" : "Create Employee"}
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </>
  );
}
