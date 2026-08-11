import React from "react";
import { Link, useLocation } from "react-router";
import { Result, Button } from "antd";

export default function NotFound() {
  const location = useLocation();

  if (location.pathname.startsWith("/.well-known")) {
    return null;
  }

  return (
    <div style={{ display: "flex", justifyContent: "center", alignItems: "center", minHeight: "100vh", padding: 24 }}>
      <Result
        status="404"
        title="404"
        subTitle="Sorry, the page you visited does not exist."
        extra={
          <Link to="/">
            <Button type="primary">Back to Dashboard</Button>
          </Link>
        }
      />
    </div>
  );
}
