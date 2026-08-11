import React, { useEffect } from "react";
import { Navigate, useLocation } from "react-router";
import { Spin } from "antd";
import { useAuthStore } from "../store/useAuthStore";

interface ProtectedRouteProps {
  children: React.ReactNode;
  allowedRoles?: string[];
}

export const ProtectedRoute: React.FC<ProtectedRouteProps> = ({
  children,
  allowedRoles,
}) => {
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated);
  const user = useAuthStore((state) => state.user);
  const isLoading = useAuthStore((state) => state.isLoading);
  const isInitialized = useAuthStore((state) => state.isInitialized);
  
  const location = useLocation();

  useEffect(() => {
    if (!isInitialized) {
      useAuthStore.getState().fetchCurrentUser();
    }
  }, [isInitialized]);

  if (!isInitialized || isLoading) {
    return (
      <div style={{ display: "flex", justifyContent: "center", alignItems: "center", height: "100vh" }}>
        <Spin size="large" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (allowedRoles && user && !allowedRoles.includes(user.role) && user.role !== "admin") {
    return (
      <div style={{ padding: 40, textAlign: "center" }}>
        <h2>Access Denied</h2>
        <p>You do not have permission to access this section.</p>
      </div>
    );
  }

  return <>{children}</>;
};
