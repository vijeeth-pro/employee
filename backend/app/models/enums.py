import enum

class UserRole(str, enum.Enum):
    ADMIN = "admin"
    COMPANY = "company"
    EMPLOYEE = "employee"
    VENDOR_COMPANY = "vendor.company"
    VENDOR_EMPLOYEE = "vendor.employee"
