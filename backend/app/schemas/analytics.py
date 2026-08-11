from typing import List
from pydantic import BaseModel
from app.schemas.user import UserOut

class DashboardStats(BaseModel):
    total_companies: int
    total_employees: int
    total_vendors: int
    total_vendor_employees: int
    active_contracts: int
    recent_users: List[UserOut]
