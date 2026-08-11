import React, { useMemo } from "react";
import { Layout, Menu, Button, Avatar, Dropdown, Tag, Space, Popconfirm, theme } from "antd";
import {
  DashboardOutlined,
  BankOutlined,
  UserOutlined,
  TeamOutlined,
  SolutionOutlined,
  IdcardOutlined,
  LogoutOutlined,
  SunOutlined,
  MoonOutlined,
  MenuFoldOutlined,
  MenuUnfoldOutlined,
  SafetyCertificateOutlined
} from "@ant-design/icons";
import { useNavigate, useLocation, Link } from "react-router";
import { useAuthStore } from "../store/useAuthStore";
import { useAppStore } from "../store/useAppStore";
import { AiAssistant } from "./AiAssistant";

const { Header, Sider, Content, Footer } = Layout;

export const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  
  const user = useAuthStore((state) => state.user);
  const logout = useAuthStore((state) => state.logout);

  const themeMode = useAppStore((state) => state.themeMode);
  const collapsedSider = useAppStore((state) => state.collapsedSider);
  const toggleTheme = useAppStore((state) => state.toggleTheme);
  const toggleSider = useAppStore((state) => state.toggleSider);

  const { token: themeToken } = theme.useToken();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  const roleColorMap: Record<string, string> = {
    admin: "magenta",
    company: "blue",
    employee: "green",
    "vendor.company": "purple",
    "vendor.employee": "orange",
  };

  const roleLabelMap: Record<string, string> = {
    admin: "Admin",
    company: "Company Admin",
    employee: "Company Employee",
    "vendor.company": "Vendor Company Admin",
    "vendor.employee": "Vendor Contractor",
  };

  const menuItems = useMemo(() => [
    {
      key: "/",
      icon: <DashboardOutlined />,
      label: <Link to="/">Dashboard</Link>,
    },
    ...(user?.role === "admin"
      ? [
          {
            key: "/companies",
            icon: <BankOutlined />,
            label: <Link to="/companies">Companies</Link>,
          },
        ]
      : []),
    ...(user?.role === "admin" || user?.role === "company" || user?.role === "employee"
      ? [
          {
            key: "/employees",
            icon: <TeamOutlined />,
            label: <Link to="/employees">Company Employees</Link>,
          },
        ]
      : []),
    ...(user?.role === "admin" || user?.role === "company" || user?.role === "vendor.company"
      ? [
          {
            key: "/vendor-companies",
            icon: <SolutionOutlined />,
            label: <Link to="/vendor-companies">Vendor Companies</Link>,
          },
        ]
      : []),
    ...(user?.role === "admin" || user?.role === "vendor.company" || user?.role === "vendor.employee"
      ? [
          {
            key: "/vendor-employees",
            icon: <IdcardOutlined />,
            label: <Link to="/vendor-employees">Vendor Employees</Link>,
          },
        ]
      : []),
    {
      key: "/profile",
      icon: <UserOutlined />,
      label: <Link to="/profile">My Profile</Link>,
    },
  ], [user?.role]);

  const userMenuItems = useMemo(() => [
    {
      key: "profile",
      icon: <UserOutlined />,
      label: "My Profile",
      onClick: () => navigate("/profile"),
    },
    {
      type: "divider" as const,
    },
    {
      key: "logout",
      icon: <LogoutOutlined />,
      danger: true,
      label: "Sign Out",
      onClick: handleLogout,
    },
  ], [navigate, logout]);

  return (
    <Layout style={{ minHeight: "100vh" }}>
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsedSider}
        className={themeMode === "dark" ? "dark-sider" : "light-sider"}
        style={{
          boxShadow: "2px 0 8px 0 rgba(0, 0, 0, 0.05)",
          zIndex: 10,
          display: "flex",
          flexDirection: "column",
        }}
      >
        <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
          {/* Logo Brand Header */}
          <div style={{
            height: 64,
            margin: "12px 16px",
            display: "flex",
            alignItems: "center",
            justifyContent: collapsedSider ? "center" : "flex-start",
            paddingLeft: collapsedSider ? 0 : 8,
            gap: 12
          }}>
            <SafetyCertificateOutlined style={{ fontSize: 24, color: "#1677ff" }} />
            {!collapsedSider && (
              <span style={{
                fontSize: 16,
                fontWeight: 700,
                color: themeMode === "dark" ? "#ffffff" : "#0f172a",
                whiteSpace: "nowrap"
              }}>
                Workforce OS
              </span>
            )}
          </div>

          {/* Navigation Menu */}
          <Menu
            theme={themeMode === "dark" ? "dark" : "light"}
            mode="inline"
            selectedKeys={[location.pathname]}
            items={menuItems}
            style={{ borderRight: 0 }}
          />
        </div>

        {/* Sidebar Footer Logout Button */}
        <div style={{
          padding: "16px 12px",
          borderTop: themeMode === "dark" ? "1px solid rgba(255, 255, 255, 0.1)" : "1px solid #e2e8f0",
          marginTop: "auto"
        }}>
          <Popconfirm
            title="Sign Out?"
            description="Are you sure you want to log out of Workforce OS?"
            onConfirm={handleLogout}
            okText="Sign Out"
            cancelText="Cancel"
            placement="rightBottom"
          >
            <Button
              danger
              type={themeMode === "dark" ? "text" : "default"}
              icon={<LogoutOutlined />}
              block
              style={{
                display: "flex",
                alignItems: "center",
                justifyContent: collapsedSider ? "center" : "flex-start",
                height: 40,
                borderRadius: 8,
                fontWeight: 600,
              }}
            >
              {!collapsedSider && <span>Sign Out</span>}
            </Button>
          </Popconfirm>
        </div>
      </Sider>

      <Layout>
        <Header
          style={{
            padding: "0 24px",
            background: themeToken.colorBgContainer,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            boxShadow: "0 1px 4px rgba(0,21,41,.06)",
            zIndex: 9
          }}
        >
          <Space size="large">
            <Button
              type="text"
              icon={collapsedSider ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={toggleSider}
              style={{ fontSize: "16px", width: 40, height: 40 }}
            />
            <span style={{ fontSize: 16, fontWeight: 600, color: themeToken.colorText }}>
              Employee & Vendor Management
            </span>
          </Space>

          <Space size="middle">
            <Button
              type="text"
              icon={themeMode === "dark" ? <SunOutlined /> : <MoonOutlined />}
              onClick={toggleTheme}
              title={`Switch to ${themeMode === "dark" ? "Light" : "Dark"} Mode`}
            />

            {user && (
              <Tag color={roleColorMap[user.role] || "default"} style={{ padding: "4px 10px", fontSize: 12, borderRadius: 12 }}>
                {roleLabelMap[user.role] || user.role}
              </Tag>
            )}

            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
              <Space style={{ cursor: "pointer", padding: "4px 8px", borderRadius: 6 }}>
                <Avatar style={{ backgroundColor: "#1677ff" }} icon={<UserOutlined />}>
                  {user?.full_name?.charAt(0).toUpperCase()}
                </Avatar>
                <div style={{ display: "flex", flexDirection: "column", lineHeight: 1.2 }}>
                  <span style={{ fontWeight: 600, fontSize: 13 }}>{user?.full_name}</span>
                  <span style={{ fontSize: 11, color: themeToken.colorTextSecondary }}>
                    {user?.company_name || user?.vendor_company_name || "System Admin"}
                  </span>
                </div>
              </Space>
            </Dropdown>

            <Popconfirm
              title="Sign Out?"
              description="Are you sure you want to log out?"
              onConfirm={handleLogout}
              okText="Sign Out"
              cancelText="Cancel"
              placement="bottomRight"
            >
              <Button danger icon={<LogoutOutlined />} style={{ borderRadius: 8 }}>
                Logout
              </Button>
            </Popconfirm>
          </Space>
        </Header>

        <Content style={{ margin: "24px 24px", minHeight: 280 }}>
          <div style={{ padding: 24, background: themeToken.colorBgContainer, borderRadius: 12, minHeight: "calc(100vh - 160px)" }}>
            {children}
          </div>
        </Content>

        <Footer style={{ textAlign: "center", color: themeToken.colorTextDescription }}>
          Workforce Management System ©2026 Enterprise Solution w/ Ant Design & FastAPI
        </Footer>
      </Layout>

      {/* Floating Role-Aware AI Assistant Drawer */}
      <AiAssistant />
    </Layout>
  );
};
