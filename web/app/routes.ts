import { type RouteConfig, index, route, layout } from "@react-router/dev/routes";

export default [
  route("login", "routes/login.tsx"),
  layout("routes/protected-layout.tsx", [
    index("routes/dashboard.tsx"),
    route("employees", "routes/employees.tsx"),
    route("companies", "routes/companies.tsx"),
    route("vendor-companies", "routes/vendor-companies.tsx"),
    route("vendor-employees", "routes/vendor-employees.tsx"),
    route("profile", "routes/profile.tsx"),
    route("policy-management", "routes/policy-management.tsx"),
  ]),
  route("*", "routes/not-found.tsx"),
] satisfies RouteConfig;
