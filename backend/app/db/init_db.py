from sqlalchemy.orm import Session
from app.core.database import engine, SessionLocal
from app.db.base import Base
from app.models import User, Company, VendorCompany, CompanyPolicy, UserRole
from app.core.security import get_password_hash

def init_db():
    print("Dropping and recreating database tables...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db: Session = SessionLocal()
    try:
        print("Seeding database with initial sample data for companies, employees, vendors, and policies...")

        # 1. Create Companies
        apex_company = Company(
            name="Apex Technologies Inc.",
            code="COMP-APEX",
            email="info@apextech.com",
            phone="+1 (555) 019-2831",
            address="100 Silicon Way, San Francisco, CA",
            industry="Software & AI",
            status="active"
        )
        horizon_company = Company(
            name="Horizon Health Solutions",
            code="COMP-HORIZON",
            email="contact@horizonhealth.com",
            phone="+1 (555) 014-9922",
            address="450 Healthcare Blvd, Boston, MA",
            industry="HealthTech",
            status="active"
        )
        db.add_all([apex_company, horizon_company])
        db.commit()
        db.refresh(apex_company)
        db.refresh(horizon_company)

        # 2. Create Vendor Companies
        techserve_vendor = VendorCompany(
            name="TechServe Solutions Ltd.",
            code="VEND-TECHSERVE",
            email="support@techserve.com",
            phone="+1 (555) 088-3411",
            address="75 Innovation Park, Austin, TX",
            service_type="IT Staffing & Cloud Engineering",
            status="active"
        )
        global_vendor = VendorCompany(
            name="Global Staffing Partners",
            code="VEND-GLOBAL",
            email="services@globalstaffing.com",
            phone="+1 (555) 077-1155",
            address="200 Corporate Plaza, Chicago, IL",
            service_type="Contract Recruitment",
            status="active"
        )
        db.add_all([techserve_vendor, global_vendor])
        db.commit()
        db.refresh(techserve_vendor)
        db.refresh(global_vendor)

        # Associate Vendors with Companies
        apex_company.vendors.append(techserve_vendor)
        apex_company.vendors.append(global_vendor)
        horizon_company.vendors.append(techserve_vendor)
        db.commit()

        # 3. Seed Corporate Policies & Rules
        policies = [
            CompanyPolicy(
                title="Apex Annual Leave & Vacation Policy",
                category="Leave Policy",
                content="Apex Technologies provides 20 paid annual leave days, 10 sick leave days, and 12 public holidays. Leave requests exceeding 3 consecutive days require manager approval 2 weeks in advance. Unused annual leave up to 5 days can be rolled over to the next calendar year.",
                company_id=apex_company.id
            ),
            CompanyPolicy(
                title="Apex Remote & Flexible Work Rules",
                category="Remote Work",
                content="Employees at Apex Technologies may work remotely up to 3 days per week (Hybrid model). Core working hours are 10:00 AM to 4:00 PM PST. Remote employees are provided a $500 home office setup allowance.",
                company_id=apex_company.id
            ),
            CompanyPolicy(
                title="Apex Employee Expense Reimbursement Policy",
                category="Expenses",
                content="Business travel, software subscriptions, and client meals are reimbursable up to $1,500 monthly with valid receipts. Expenses must be submitted within 30 days of spend via the finance portal.",
                company_id=apex_company.id
            ),
            CompanyPolicy(
                title="TechServe Vendor Contractor Code of Conduct",
                category="Vendor Guidelines",
                content="All contractors deployed by TechServe Solutions must adhere to client non-disclosure agreements (NDAs), complete mandatory cybersecurity awareness training within 7 days of onboarding, and log billable hours weekly every Friday by 5:00 PM CST.",
                vendor_company_id=techserve_vendor.id
            ),
            CompanyPolicy(
                title="TechServe Timesheet & Overtime Rules",
                category="Timesheets",
                content="Standard contractor work week is 40 hours. Overtime beyond 40 hours requires prior written authorization from both the TechServe Account Director and the client hiring manager.",
                vendor_company_id=techserve_vendor.id
            ),
            CompanyPolicy(
                title="Horizon Health HIPAA Data Compliance Policy",
                category="Compliance",
                content="All employees and contractors working with Horizon Health Solutions must strictly comply with HIPAA regulations. Patient data must never be stored on unencrypted local drives or personal cloud accounts.",
                company_id=horizon_company.id
            )
        ]
        db.add_all(policies)
        db.commit()

        # 4. Create System Users for all 5 roles
        users_to_seed = [
            # Role: Admin
            User(
                email="admin@system.com",
                hashed_password=get_password_hash("admin123"),
                full_name="System Administrator",
                role=UserRole.ADMIN,
                phone="+1 (555) 000-0000",
                designation="Global Administrator",
                department="IT Operations",
                status="active"
            ),
            
            # Role: Company Admin
            User(
                email="company@apex.com",
                hashed_password=get_password_hash("company123"),
                full_name="Apex Enterprise Admin",
                role=UserRole.COMPANY,
                company_id=apex_company.id,
                phone="+1 (555) 019-1111",
                designation="HR Director",
                department="Human Resources",
                status="active"
            ),
            User(
                email="horizon@horizonhealth.com",
                hashed_password=get_password_hash("company123"),
                full_name="Horizon Enterprise Admin",
                role=UserRole.COMPANY,
                company_id=horizon_company.id,
                phone="+1 (555) 014-2222",
                designation="VP Operations",
                department="Executive",
                status="active"
            ),

            # Role: Company Employee
            User(
                email="employee@apex.com",
                hashed_password=get_password_hash("emp123"),
                full_name="John Doe",
                role=UserRole.EMPLOYEE,
                company_id=apex_company.id,
                phone="+1 (555) 019-3333",
                designation="Senior Software Engineer",
                department="Engineering",
                status="active"
            ),
            User(
                email="sarah.apex@apex.com",
                hashed_password=get_password_hash("emp123"),
                full_name="Sarah Connor",
                role=UserRole.EMPLOYEE,
                company_id=apex_company.id,
                phone="+1 (555) 019-4444",
                designation="Lead Product Manager",
                department="Product Management",
                status="active"
            ),
            User(
                email="mark.horizon@horizonhealth.com",
                hashed_password=get_password_hash("emp123"),
                full_name="Mark Sloan",
                role=UserRole.EMPLOYEE,
                company_id=horizon_company.id,
                phone="+1 (555) 014-5555",
                designation="Clinical Data Analyst",
                department="Data & Analytics",
                status="active"
            ),

            # Role: Vendor Company Admin
            User(
                email="vendor@techserve.com",
                hashed_password=get_password_hash("vendor123"),
                full_name="TechServe Vendor Admin",
                role=UserRole.VENDOR_COMPANY,
                vendor_company_id=techserve_vendor.id,
                phone="+1 (555) 088-6666",
                designation="Account Director",
                department="Client Relations",
                status="active"
            ),
            User(
                email="contact@globalstaffing.com",
                hashed_password=get_password_hash("vendor123"),
                full_name="Global Staffing Manager",
                role=UserRole.VENDOR_COMPANY,
                vendor_company_id=global_vendor.id,
                phone="+1 (555) 077-7777",
                designation="Managing Director",
                department="Operations",
                status="active"
            ),

            # Role: Vendor Employee / Contractor
            User(
                email="vendoremp@techserve.com",
                hashed_password=get_password_hash("vemp123"),
                full_name="Sarah Jenkins",
                role=UserRole.VENDOR_EMPLOYEE,
                vendor_company_id=techserve_vendor.id,
                phone="+1 (555) 088-8888",
                designation="Senior DevOps Consultant",
                department="Cloud Infrastructure",
                status="active"
            ),
            User(
                email="alex.vendor@techserve.com",
                hashed_password=get_password_hash("vemp123"),
                full_name="Alex Vance",
                role=UserRole.VENDOR_EMPLOYEE,
                vendor_company_id=techserve_vendor.id,
                phone="+1 (555) 088-9999",
                designation="Cybersecurity Specialist",
                department="Security",
                status="active"
            )
        ]

        db.add_all(users_to_seed)
        db.commit()
        print("Database seeded successfully with sample records & policies for all 5 roles!")
    except Exception as e:
        print("Error seeding database:", e)
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
