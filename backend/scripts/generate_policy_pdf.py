import os
import sys
from datetime import datetime

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute and render 'Page X of Y' 
    along with professional running headers and footers.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, page_count):
        self.saveState()
        
        # We omit header/footer on page 1 (cover header card is displayed inline)
        if self._pageNumber > 1:
            # Header
            self.setFont("Helvetica-Bold", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawString(54, 11 * inch - 36, "WORKFORCE OS  |  ENTERPRISE GOVERNANCE & POLICY MANUAL")
            self.setFont("Helvetica", 8)
            self.drawRightString(8.5 * inch - 54, 11 * inch - 36, "CONFIDENTIAL")
            
            self.setStrokeColor(colors.HexColor("#e2e8f0"))
            self.setLineWidth(0.75)
            self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)
            
            # Footer
            self.line(54, 46, 8.5 * inch - 54, 46)
            self.setFont("Helvetica", 8)
            self.setFillColor(colors.HexColor("#64748b"))
            self.drawString(54, 32, "© 2026 Workforce OS Inc. All rights reserved.")
            self.drawRightString(8.5 * inch - 54, 32, f"Page {self._pageNumber} of {page_count}")

        self.restoreState()


def build_pdf(filename):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()

    # Custom Color Palette
    PRIMARY_DARK = colors.HexColor("#0f172a")  # Slate 900
    ACCENT_BLUE = colors.HexColor("#1677ff")   # Ant Design Blue
    TEXT_DARK = colors.HexColor("#1e293b")     # Slate 800
    TEXT_MUTED = colors.HexColor("#64748b")    # Slate 500
    BG_LIGHT = colors.HexColor("#f8fafc")      # Slate 50
    BORDER_COLOR = colors.HexColor("#cbd5e1")  # Slate 300

    # Custom Typography Styles
    styles.add(ParagraphStyle(
        name="DocTitle",
        fontName="Helvetica-Bold",
        fontSize=22,
        leading=26,
        textColor=PRIMARY_DARK,
        spaceAfter=4
    ))

    styles.add(ParagraphStyle(
        name="DocSubtitle",
        fontName="Helvetica-Bold",
        fontSize=11,
        leading=15,
        textColor=ACCENT_BLUE,
        spaceAfter=10
    ))

    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=PRIMARY_DARK,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name="SubSectionHeader",
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=ACCENT_BLUE,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    ))

    styles.add(ParagraphStyle(
        name="BodyTextCustom",
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=TEXT_DARK,
        spaceAfter=5
    ))

    styles.add(ParagraphStyle(
        name="BulletCustom",
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=TEXT_DARK,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=3
    ))

    styles.add(ParagraphStyle(
        name="CalloutText",
        fontName="Helvetica-Oblique",
        fontSize=8.5,
        leading=12,
        textColor=colors.HexColor("#0369a1")
    ))

    styles.add(ParagraphStyle(
        name="TableHeader",
        fontName="Helvetica-Bold",
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=0
    ))

    styles.add(ParagraphStyle(
        name="TableCell",
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=TEXT_DARK
    ))

    styles.add(ParagraphStyle(
        name="TableCellBold",
        fontName="Helvetica-Bold",
        fontSize=8,
        leading=11,
        textColor=PRIMARY_DARK
    ))

    story = []

    # =========================================================================
    # HEADER BANNER / TITLE BLOCK
    # =========================================================================
    banner_data = [
        [
            Paragraph("WORKFORCE OS ENTERPRISE", styles["DocTitle"]),
        ],
        [
            Paragraph("Corporate Roles, Operational Governance & Comprehensive Leave Policy Manual", styles["DocSubtitle"]),
        ],
        [
            Paragraph("<b>Version:</b> 2.0 &nbsp;&nbsp;|&nbsp;&nbsp; <b>Effective Date:</b> August 16, 2026 &nbsp;&nbsp;|&nbsp;&nbsp; <b>Scope:</b> Global Enterprise & Vendors", ParagraphStyle("Meta", fontName="Helvetica", fontSize=8, textColor=TEXT_MUTED)),
        ]
    ]

    banner_table = Table(banner_data, colWidths=[504])
    banner_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#f1f5f9")),
        ('PADDING', (0,0), (-1,-1), 12),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('LINEBELOW', (0,0), (-1,0), 1.5, ACCENT_BLUE),
        ('BOTTOMPADDING', (0,-1), (-1,-1), 10),
    ]))
    story.append(banner_table)
    story.append(Spacer(1, 12))

    # =========================================================================
    # SECTION 1: EXECUTIVE SUMMARY & GOVERNANCE SCOPE
    # =========================================================================
    story.append(Paragraph("1. Executive Summary & Governance Scope", styles["SectionHeader"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_BLUE, spaceAfter=6, spaceBefore=0))
    
    story.append(Paragraph(
        "This Policy Document establishes mandatory operational guidelines, system security standards, role definitions, and employee/vendor leave management policies governing all operations within <b>Workforce OS</b>. This framework ensures complete regulatory compliance, data privacy, operational transparency, and standardized personnel management across enterprise entities and third-party contractor agencies.",
        styles["BodyTextCustom"]
    ))

    story.append(Paragraph("<b>Applicability:</b> This policy binds all of the following stakeholders:", styles["BodyTextCustom"]))
    story.append(Paragraph("• <b>System Administrators:</b> Master personnel overseeing enterprise platform operations.", styles["BulletCustom"]))
    story.append(Paragraph("• <b>Client Companies:</b> Enterprise client organizations registered within the platform.", styles["BulletCustom"]))
    story.append(Paragraph("• <b>Direct Employees:</b> Full-time and part-time internal staff employed directly by client companies.", styles["BulletCustom"]))
    story.append(Paragraph("• <b>Vendor Agencies:</b> Third-party staffing, consulting, and contractor agencies.", styles["BulletCustom"]))
    story.append(Paragraph("• <b>Vendor Contractors / Employees:</b> External consultants assigned to client projects via registered vendor agencies.", styles["BulletCustom"]))

    story.append(Spacer(1, 8))

    # =========================================================================
    # SECTION 2: SYSTEM ROLES & PERMISSION MATRIX (RBAC)
    # =========================================================================
    story.append(Paragraph("2. System Roles & Role-Based Access Control (RBAC)", styles["SectionHeader"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_BLUE, spaceAfter=6, spaceBefore=0))

    story.append(Paragraph(
        "Workforce OS enforces strict Multi-Tenant Role-Based Access Control (RBAC). User privileges are automatically scoped to tenant boundaries based on five primary role designations:",
        styles["BodyTextCustom"]
    ))

    # Roles description list
    story.append(Paragraph("<b>1. System Administrator (<code>admin</code>):</b> Global oversight role. Has unrestricted access across all client companies, vendor agencies, user profiles, and system audit logs. Authorizes data resets, system seeding, and global registrations.", styles["BulletCustom"]))
    story.append(Paragraph("<b>2. Company Admin (<code>company</code>):</b> Administrative head of an enterprise company. Manages internal company details, registers direct employees, assigns contracted vendor agencies, and views company analytics.", styles["BulletCustom"]))
    story.append(Paragraph("<b>3. Company Employee (<code>employee</code>):</b> Internal staff member. Has access to personal profile settings, departmental directory, colleague organization charts, and personal leave requests.", styles["BulletCustom"]))
    story.append(Paragraph("<b>4. Vendor Company Admin (<code>vendor.company</code>):</b> Executive manager of a third-party vendor agency. Registers external contractors/consultants, views client contract assignments, and manages agency details.", styles["BulletCustom"]))
    story.append(Paragraph("<b>5. Vendor Employee / Contractor (<code>vendor.employee</code>):</b> External contractor assigned to client initiatives. Has access to personal contractor profile, assigned client company info, and contractor task records.", styles["BulletCustom"]))

    story.append(Spacer(1, 6))

    # RBAC Permission Matrix Table
    story.append(Paragraph("<b>Role Permission Matrix:</b>", styles["SubSectionHeader"]))

    rbac_headers = [
        Paragraph("System Feature / Action", styles["TableHeader"]),
        Paragraph("Admin", styles["TableHeader"]),
        Paragraph("Company", styles["TableHeader"]),
        Paragraph("Employee", styles["TableHeader"]),
        Paragraph("Vendor Admin", styles["TableHeader"]),
        Paragraph("Vendor Staff", styles["TableHeader"]),
    ]

    rbac_matrix = [
        rbac_headers,
        [Paragraph("Create / Edit Companies", styles["TableCellBold"]), Paragraph("Full", styles["TableCell"]), Paragraph("None", styles["TableCell"]), Paragraph("None", styles["TableCell"]), Paragraph("None", styles["TableCell"]), Paragraph("None", styles["TableCell"])],
        [Paragraph("Manage Internal Employees", styles["TableCellBold"]), Paragraph("Full", styles["TableCell"]), Paragraph("Own Org", styles["TableCell"]), Paragraph("View Dept", styles["TableCell"]), Paragraph("None", styles["TableCell"]), Paragraph("None", styles["TableCell"])],
        [Paragraph("Register Vendor Agencies", styles["TableCellBold"]), Paragraph("Full", styles["TableCell"]), Paragraph("Own Org", styles["TableCell"]), Paragraph("None", styles["TableCell"]), Paragraph("None", styles["TableCell"]), Paragraph("None", styles["TableCell"])],
        [Paragraph("Assign Vendor to Client", styles["TableCellBold"]), Paragraph("Full", styles["TableCell"]), Paragraph("Own Contracts", styles["TableCell"]), Paragraph("None", styles["TableCell"]), Paragraph("View Contracts", styles["TableCell"]), Paragraph("None", styles["TableCell"])],
        [Paragraph("Manage Vendor Contractors", styles["TableCellBold"]), Paragraph("Full", styles["TableCell"]), Paragraph("View Assigned", styles["TableCell"]), Paragraph("None", styles["TableCell"]), Paragraph("Own Agency", styles["TableCell"]), Paragraph("Self Profile", styles["TableCell"])],
        [Paragraph("View Platform Analytics", styles["TableCellBold"]), Paragraph("Global", styles["TableCell"]), Paragraph("Own Org", styles["TableCell"]), Paragraph("None", styles["TableCell"]), Paragraph("Agency Stats", styles["TableCell"]), Paragraph("None", styles["TableCell"])],
        [Paragraph("Reset Database Seed Data", styles["TableCellBold"]), Paragraph("Allowed", styles["TableCell"]), Paragraph("Denied", styles["TableCell"]), Paragraph("Denied", styles["TableCell"]), Paragraph("Denied", styles["TableCell"]), Paragraph("Denied", styles["TableCell"])],
    ]

    rbac_table = Table(rbac_matrix, colWidths=[154, 70, 70, 70, 70, 70])
    rbac_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_DARK),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(rbac_table)

    story.append(Spacer(1, 10))

    # =========================================================================
    # SECTION 3: COMPANY & VENDOR GOVERNANCE RULES
    # =========================================================================
    story.append(Paragraph("3. Company & Vendor Governance Rules", styles["SectionHeader"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_BLUE, spaceAfter=6, spaceBefore=0))

    story.append(Paragraph("<b>A. Client Company Registration Rules:</b>", styles["SubSectionHeader"]))
    story.append(Paragraph("• Every company must possess a unique legal identifier code (e.g. <code>COMP-APEX</code>, <code>COMP-NEXUS</code>).", styles["BulletCustom"]))
    story.append(Paragraph("• Corporate contact details (valid official email domain and telephone number) are mandatory prior to active status approval.", styles["BulletCustom"]))
    story.append(Paragraph("• Deactivation of a company automatically restricts platform access for all associated employees.", styles["BulletCustom"]))

    story.append(Paragraph("<b>B. Vendor Agency Onboarding & Service Categorization:</b>", styles["SubSectionHeader"]))
    story.append(Paragraph("• Vendor agencies must register with explicit service type tags (e.g. <i>IT Staffing, Management Consulting, Cloud Infrastructure, Legal Compliance</i>).", styles["BulletCustom"]))
    story.append(Paragraph("• Vendor agency codes must follow the <code>VEND-XXXX</code> format to ensure automated billing and log routing.", styles["BulletCustom"]))

    story.append(Paragraph("<b>C. Vendor-to-Company Contract Binding Rules:</b>", styles["SubSectionHeader"]))
    story.append(Paragraph("• A vendor agency can only deploy contractors to a client company after an official <b>Contract Assignment</b> is linked between the entities.", styles["BulletCustom"]))
    story.append(Paragraph("• Client companies maintain full authority to terminate vendor agency assignments upon 30-day written notice.", styles["BulletCustom"]))

    story.append(Spacer(1, 8))

    # =========================================================================
    # SECTION 4: EMPLOYEE & CONTRACTOR WORKFORCE POLICY
    # =========================================================================
    story.append(Paragraph("4. Employee & Contractor Workforce Policy", styles["SectionHeader"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_BLUE, spaceAfter=6, spaceBefore=0))

    story.append(Paragraph("<b>A. Direct Internal Employee Rules:</b>", styles["SubSectionHeader"]))
    story.append(Paragraph("• Full-time internal employees are assigned to a primary Department (e.g., <i>Engineering, Product, Operations, HR</i>).", styles["BulletCustom"]))
    story.append(Paragraph("• Passwords must adhere to standard security requirements (minimum 6 characters, regular quarterly updates enforced).", styles["BulletCustom"]))

    story.append(Paragraph("<b>B. External Vendor Contractor Rules:</b>", styles["SubSectionHeader"]))
    story.append(Paragraph("• All vendor contractors must sign Non-Disclosure Agreements (NDAs) and Intellectual Property (IP) Transfer agreements prior to system access.", styles["BulletCustom"]))
    story.append(Paragraph("• Contractor accounts must be linked to a valid Vendor Agency ID. Independent un-attached contractor accounts are strictly prohibited.", styles["BulletCustom"]))

    story.append(Spacer(1, 8))

    # =========================================================================
    # SECTION 5: COMPREHENSIVE LEAVE & TIME-OFF POLICY
    # =========================================================================
    story.append(Paragraph("5. Comprehensive Leave & Time-Off Policy", styles["SectionHeader"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_BLUE, spaceAfter=6, spaceBefore=0))

    story.append(Paragraph(
        "Workforce OS provides a structured time-off policy designed to promote work-life balance while ensuring operational continuity. Leave entitlements depend on employment type and tenure.",
        styles["BodyTextCustom"]
    ))

    # Leave Entitlement Master Table
    leave_headers = [
        Paragraph("Leave Category", styles["TableHeader"]),
        Paragraph("Annual Quota", styles["TableHeader"]),
        Paragraph("Eligible Roles", styles["TableHeader"]),
        Paragraph("Carry-Forward", styles["TableHeader"]),
        Paragraph("Encashment", styles["TableHeader"]),
    ]

    leave_table_data = [
        leave_headers,
        [Paragraph("Privilege Leave (PL / Annual)", styles["TableCellBold"]), Paragraph("21 Days", styles["TableCell"]), Paragraph("Direct Employees", styles["TableCell"]), Paragraph("Max 10 Days", styles["TableCell"]), Paragraph("Allowed on Exit", styles["TableCell"])],
        [Paragraph("Casual & Sick Leave (CL/SL)", styles["TableCellBold"]), Paragraph("12 Days", styles["TableCell"]), Paragraph("Direct Employees", styles["TableCell"]), Paragraph("Lapses Year-End", styles["TableCell"]), Paragraph("Not Allowed", styles["TableCell"])],
        [Paragraph("Maternity Leave", styles["TableCellBold"]), Paragraph("26 Weeks", styles["TableCell"]), Paragraph("Female Employees", styles["TableCell"]), Paragraph("N/A", styles["TableCell"]), Paragraph("Paid Fully", styles["TableCell"])],
        [Paragraph("Paternity Leave", styles["TableCellBold"]), Paragraph("15 Days", styles["TableCell"]), Paragraph("Male Employees", styles["TableCell"]), Paragraph("N/A", styles["TableCell"]), Paragraph("Paid Fully", styles["TableCell"])],
        [Paragraph("Bereavement Leave", styles["TableCellBold"]), Paragraph("5 Days", styles["TableCell"]), Paragraph("All Personnel", styles["TableCell"]), Paragraph("N/A", styles["TableCell"]), Paragraph("Paid Fully", styles["TableCell"])],
        [Paragraph("Vendor Contractor Leave", styles["TableCellBold"]), Paragraph("As per Agency", styles["TableCell"]), Paragraph("Vendor Contractors", styles["TableCell"]), Paragraph("Agency Terms", styles["TableCell"]), Paragraph("Agency Terms", styles["TableCell"])],
        [Paragraph("Loss of Pay (LOP)", styles["TableCellBold"]), Paragraph("Uncapped*", styles["TableCell"]), Paragraph("All Personnel", styles["TableCell"]), Paragraph("N/A", styles["TableCell"]), Paragraph("Unpaid", styles["TableCell"])],
    ]

    leave_table = Table(leave_table_data, colWidths=[130, 80, 104, 95, 95])
    leave_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY_DARK),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, BG_LIGHT]),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(leave_table)

    story.append(Spacer(1, 8))

    # Detailed Leave Rules
    story.append(Paragraph("<b>Detailed Leave Guidelines & Procedures:</b>", styles["SubSectionHeader"]))
    
    story.append(Paragraph("<b>1. Privilege Leave (PL) / Annual Vacation:</b>", styles["BodyTextCustom"]))
    story.append(Paragraph("• Accrual Rate: Employees earn 1.75 days of PL per completed calendar month of service.", styles["BulletCustom"]))
    story.append(Paragraph("• Notice Requirement: Planned vacation exceeding 3 consecutive days requires manager approval at least <b>10 business days</b> in advance.", styles["BulletCustom"]))
    story.append(Paragraph("• Maximum Accumulation: Employees can carry forward a maximum of 10 PL days into the subsequent calendar year. Excess unused balance lapses.", styles["BulletCustom"]))

    story.append(Paragraph("<b>2. Sick Leave (SL) & Casual Leave (CL):</b>", styles["BodyTextCustom"]))
    story.append(Paragraph("• Allocated at 1 day per month (total 12 days annually).", styles["BulletCustom"]))
    story.append(Paragraph("• Medical Documentation: Consecutive sick leave exceeding <b>2 business days</b> mandates submission of a certified doctor's medical certificate.", styles["BulletCustom"]))

    story.append(Paragraph("<b>3. Vendor Contractor Time-Off Rules:</b>", styles["BodyTextCustom"]))
    story.append(Paragraph("• Vendor Contractors are governed primarily by their parent Vendor Agency employment terms.", styles["BulletCustom"]))
    story.append(Paragraph("• <b>Dual Notice Mandate:</b> Contractors taking planned leave must notify BOTH their Vendor Agency Manager AND their assigned Client Enterprise Project Lead at least <b>5 business days</b> prior.", styles["BulletCustom"]))
    story.append(Paragraph("• <b>Billing Adjustments:</b> Client companies are not billed for contractor unworked days under Time & Materials (T&M) contract terms.", styles["BulletCustom"]))

    story.append(Spacer(1, 8))

    # =========================================================================
    # SECTION 6: SECURITY, AUDIT & COMPLIANCE
    # =========================================================================
    story.append(Paragraph("6. System Security, Data Protection & Audit", styles["SectionHeader"]))
    story.append(HRFlowable(width="100%", thickness=1, color=ACCENT_BLUE, spaceAfter=6, spaceBefore=0))

    story.append(Paragraph("• <b>HttpOnly Cookie Security:</b> Authentication tokens (JWT) are stored strictly inside encrypted <code>HttpOnly</code> and <code>SameSite=Lax</code> browser cookies to prevent XSS script theft.", styles["BulletCustom"]))
    story.append(Paragraph("• <b>Multi-Tenant Data Isolation:</b> Data queries strictly scope records by <code>company_id</code> or <code>vendor_company_id</code> to prevent cross-tenant data leaks.", styles["BulletCustom"]))
    story.append(Paragraph("• <b>Audit Trail Logging:</b> All security actions (login attempts, user creation, vendor assignments, seed resets) are recorded in server logs with client IP, timestamp, and duration.", styles["BulletCustom"]))

    story.append(Spacer(1, 10))

    # Callout Box
    callout_data = [[
        Paragraph("<b>POLICY GOVERNANCE NOTICE:</b> Workforce OS Management reserves the right to amend, update, or modify these operational guidelines and leave structures. All changes will be published in official system updates and communicated to company administrators.", styles["CalloutText"])
    ]]
    callout_table = Table(callout_data, colWidths=[504])
    callout_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#e0f2fe")),
        ('BORDER', (0,0), (-1,-1), 1, colors.HexColor("#38bdf8")),
        ('PADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(callout_table)

    story.append(Spacer(1, 14))

    # Sign-off Approval Box
    signoff_data = [
        [
            Paragraph("<b>Policy Approvals & Authorization</b>", ParagraphStyle("SignHeader", fontName="Helvetica-Bold", fontSize=9.5, textColor=PRIMARY_DARK)),
            Paragraph("", styles["TableCell"])
        ],
        [
            Paragraph("<b>Chief Human Resources Officer (CHRO):</b><br/><i>Approved & Signed</i>", styles["TableCell"]),
            Paragraph("<b>Chief Information Security Officer (CISO):</b><br/><i>Approved & Signed</i>", styles["TableCell"])
        ],
        [
            Paragraph("Date: August 16, 2026", ParagraphStyle("SignDate", fontName="Helvetica", fontSize=8, textColor=TEXT_MUTED)),
            Paragraph("Date: August 16, 2026", ParagraphStyle("SignDate", fontName="Helvetica", fontSize=8, textColor=TEXT_MUTED))
        ]
    ]
    signoff_table = Table(signoff_data, colWidths=[252, 252])
    signoff_table.setStyle(TableStyle([
        ('SPAN', (0,0), (1,0)),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#f1f5f9")),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(KeepTogether(signoff_table))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Policy PDF successfully generated: {filename}")

if __name__ == "__main__":
    output_path = "/Users/vijeethsankar/project/employee/docs/Workforce_OS_Policy_Document.pdf"
    if len(sys.argv) > 1:
        output_path = sys.argv[1]
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    build_pdf(output_path)
