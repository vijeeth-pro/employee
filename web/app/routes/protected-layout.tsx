import React from "react";
import { Outlet } from "react-router";
import { ProtectedRoute } from "../components/ProtectedRoute";
import { AppLayout } from "../components/AppLayout";

export default function ProtectedLayout() {
  return (
    <ProtectedRoute>
      <AppLayout>
        <Outlet />
      </AppLayout>
    </ProtectedRoute>
  );
}
