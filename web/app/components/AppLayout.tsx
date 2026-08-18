import React, { useMemo, useState } from "react";
import { Layout, Menu, Button, Avatar, Dropdown, Tag, Space, Popconfirm, theme, Grid, Drawer } from "antd";
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
  SafetyCertificateOutlined,
  FilePdfOutlined,
  BookOutlined
} from "@ant-design/icons";
import { useNavigate, useLocation, Link } from "react-router";
import { useAuthStore } from "../store/useAuthStore";
import { useAppStore } from "../store/useAppStore";
import { AiAssistantDrawer } from "./AiAssistantDrawer";

const { Header, Sider, Content, Footer } = Layout;
const { useBreakpoint } = Grid;

export const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const screens = useBreakpoint();
  const isMobile = !screens.md;

  const [drawerOpen, setDrawerOpen] = useState(false);
  
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
      label: <Link to="/" onClick={() => isMobile && setDrawerOpen(false)}>Dashboard</Link>,
    },
    ...(user?.role === "admin"
      ? [
          {
            key: "/companies",
            icon: <BankOutlined />,
            label: <Link to="/companies" onClick={() => isMobile && setDrawerOpen(false)}>Companies</Link>,
          },
        ]
      : []),
    ...(user?.role === "admin" || user?.role === "company" || user?.role === "employee"
      ? [
          {
            key: "/employees",
            icon: <TeamOutlined />,
            label: <Link to="/employees" onClick={() => isMobile && setDrawerOpen(false)}>Company Employees</Link>,
          },
        ]
      : []),
    ...(user?.role === "admin" || user?.role === "company" || user?.role === "vendor.company"
      ? [
          {
            key: "/vendor-companies",
            icon: <SolutionOutlined />,
            label: <Link to="/vendor-companies" onClick={() => isMobile && setDrawerOpen(false)}>Vendor Companies</Link>,
          },
        ]
      : []),
    ...(user?.role === "admin" || user?.role === "vendor.company" || user?.role === "vendor.employee"
      ? [
          {
            key: "/vendor-employees",
            icon: <IdcardOutlined />,
            label: <Link to="/vendor-employees" onClick={() => isMobile && setDrawerOpen(false)}>Vendor Employees</Link>,
          },
        ]
      : []),
    ...(user?.role === "admin" || user?.role === "company" || user?.role === "vendor.company"
      ? [
          {
            key: "/policy-management",
            icon: <BookOutlined />,
            label: <Link to="/policy-management" onClick={() => isMobile && setDrawerOpen(false)}>Policy Upload RAG</Link>,
          },
        ]
      : []),
    {
      key: "/profile",
      icon: <UserOutlined />,
      label: <Link to="/profile" onClick={() => isMobile && setDrawerOpen(false)}>My Profile</Link>,
    },
    {
      key: "/policy-pdf",
      icon: <FilePdfOutlined style={{ color: "#ff4d4f" }} />,
      label: (
        <a href="/docs/Workforce_OS_Policy_Document.pdf" target="_blank" rel="noopener noreferrer" onClick={() => isMobile && setDrawerOpen(false)}>
          Policy Manual (PDF)
        </a>
      ),
    },
  ], [user?.role, isMobile]);

  const userMenuItems = useMemo(() => [
    {
      key: "profile",
      icon: <UserOutlined />,
      label: "My Profile",
      onClick: () => navigate("/profile"),
    },
    {
      key: "policy",
      icon: <FilePdfOutlined style={{ color: "#ff4d4f" }} />,
      label: "Policy Manual (PDF)",
      onClick: () => window.open("/docs/Workforce_OS_Policy_Document.pdf", "_blank"),
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

  const navigationContent = (
    <div style={{ display: "flex", flexDirection: "column", height: "100%" }}>
      <div style={{
        height: 64,
        margin: "12px 16px",
        display: "flex",
        alignItems: "center",
        justifyContent: collapsedSider && !isMobile ? "center" : "flex-start",
        paddingLeft: collapsedSider && !isMobile ? 0 : 8,
        gap: 12
      }}>
        <SafetyCertificateOutlined style={{ fontSize: 24, color: "#1677ff" }} />
        {(!collapsedSider || isMobile) && (
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

      <Menu
        theme={themeMode === "dark" ? "dark" : "light"}
        mode="inline"
        selectedKeys={[location.pathname]}
        items={menuItems}
        style={{ borderRight: 0, flex: 1 }}
      />

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
              justifyContent: collapsedSider && !isMobile ? "center" : "flex-start",
              height: 40,
              borderRadius: 8,
              fontWeight: 600,
            }}
          >
            {(!collapsedSider || isMobile) && <span>Sign Out</span>}
          </Button>
        </Popconfirm>
      </div>
    </div>
  );

  return (
    <Layout style={{ minHeight: "100vh" }}>
      {/* Desktop Sider */}
      {!isMobile && (
        <Sider
          trigger={null}
          collapsible
          collapsed={collapsedSider}
          className={themeMode === "dark" ? "dark-sider" : "light-sider"}
          style={{
            boxShadow: "2px 0 8px 0 rgba(0, 0, 0, 0.05)",
            zIndex: 10,
          }}
        >
          {navigationContent}
        </Sider>
      )}

      {/* Mobile Navigation Drawer */}
      {isMobile && (
        <Drawer
          placement="left"
          onClose={() => setDrawerOpen(false)}
          open={drawerOpen}
          styles={{ body: { padding: 0 } }}
          width={260}
          className={themeMode === "dark" ? "dark-sider" : "light-sider"}
        >
          {navigationContent}
        </Drawer>
      )}

      <Layout>
        <Header
          style={{
            padding: isMobile ? "0 12px" : "0 24px",
            background: themeToken.colorBgContainer,
            display: "flex",
            alignItems: "center",
            justifyContent: "space-between",
            boxShadow: "0 1px 4px rgba(0,21,41,.06)",
            zIndex: 9
          }}
        >
          <Space size={isMobile ? "small" : "large"}>
            <Button
              type="text"
              icon={isMobile ? <MenuUnfoldOutlined /> : collapsedSider ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
              onClick={() => {
                if (isMobile) {
                  setDrawerOpen(true);
                } else {
                  toggleSider();
                }
              }}
              style={{ fontSize: "16px", width: 40, height: 40 }}
            />
            {screens.sm && (
              <span style={{ fontSize: isMobile ? 14 : 16, fontWeight: 600, color: themeToken.colorText }}>
                {isMobile ? "Workforce OS" : "Employee & Vendor Management"}
              </span>
            )}
          </Space>

          <Space size={isMobile ? "small" : "middle"}>
            <Button
              type="text"
              icon={themeMode === "dark" ? <SunOutlined /> : <MoonOutlined />}
              onClick={toggleTheme}
              title={`Switch to ${themeMode === "dark" ? "Light" : "Dark"} Mode`}
            />

            {user && screens.sm && (
              <Tag color={roleColorMap[user.role] || "default"} style={{ padding: "2px 8px", fontSize: 12, borderRadius: 12, margin: 0 }}>
                {roleLabelMap[user.role] || user.role}
              </Tag>
            )}

            <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
              <Space style={{ cursor: "pointer", padding: "4px 4px", borderRadius: 6 }}>
                <Avatar style={{ backgroundColor: "#1677ff" }} icon={<UserOutlined />}>
                  {user?.full_name?.charAt(0).toUpperCase()}
                </Avatar>
                {screens.md && (
                  <div style={{ display: "flex", flexDirection: "column", lineHeight: 1.2 }}>
                    <span style={{ fontWeight: 600, fontSize: 13 }}>{user?.full_name}</span>
                    <span style={{ fontSize: 11, color: themeToken.colorTextSecondary }}>
                      {user?.company_name || user?.vendor_company_name || "System Admin"}
                    </span>
                  </div>
                )}
              </Space>
            </Dropdown>

            {screens.sm && (
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
            )}
          </Space>
        </Header>

        <Content style={{ margin: isMobile ? "12px 8px" : "24px 24px", minHeight: 280 }}>
          <div style={{
            padding: isMobile ? 12 : 24,
            background: themeToken.colorBgContainer,
            borderRadius: 12,
            minHeight: "calc(100vh - 160px)"
          }}>
            {children}
          </div>
        </Content>

        <Footer style={{ textAlign: "center", padding: isMobile ? "16px 12px" : "24px 50px", color: themeToken.colorTextDescription, fontSize: 12 }}>
          Workforce Management System ©2026 Enterprise Solution
        </Footer>
      </Layout>

      {/* Floating Role-Aware RAG AI Assistant Drawer */}
      <AiAssistantDrawer />
    </Layout>
  );
};


