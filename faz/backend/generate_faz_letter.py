# generate_letter.py
"""
Generates a professional business letter from Kanch Innovative Technologies
Limited to the Head of Administration at the Football Association of Zambia
(FAZ), requesting a business meeting to demonstrate two software systems.
"""
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from datetime import date


# ---------------------------------------------------------------------------
# Editable values — replace these with your real details before sending.
# ---------------------------------------------------------------------------
COMPANY_NAME = "Kanch Innovative Technologies Limited"
COMPANY_TAGLINE = "Software Development · ICT Equipment Supply · Digital Solutions"
COMPANY_ADDRESS = "Plot 1234, Great East Road, Lusaka, Zambia"
COMPANY_PHONE = "+260 XXX XXX XXX"
COMPANY_EMAIL = "info@kanchinnovative.com"
COMPANY_WEBSITE = "www.kanchinnovative.com"

RECIPIENT_NAME = "The Head of Administration"
RECIPIENT_ORG = "Football Association of Zambia (FAZ)"
RECIPIENT_ADDRESS = "Football House, Alick Nkhata Road, Lusaka, Zambia"

SENDER_NAME = "[Your Full Name]"
SENDER_TITLE = "Managing Director"
SENDER_EMAIL = "info@kanchinnovative.com"
SENDER_PHONE = "+260 XXX XXX XXX"

LETTER_DATE = date.today().strftime("%d %B %Y")
PROPOSED_DATES = "[e.g. Tuesday, 24 September 2026, at 10:00 hours, or any other date that suits your schedule]"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def set_base_style(doc):
    """Set the document's default font and size."""
    style = doc.styles['Normal']
    style.font.name = 'Calibri'
    style.font.size = Pt(11)
    style.paragraph_format.space_after = Pt(8)
    style.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
    # Ensure the East Asian font mapping is set too
    rpr = style.element.get_or_add_rPr()
    rfonts = rpr.find(qn('w:rFonts'))
    if rfonts is None:
        rfonts = OxmlElement('w:rFonts')
        rpr.append(rfonts)
    rfonts.set(qn('w:ascii'), 'Calibri')
    rfonts.set(qn('w:hAnsi'), 'Calibri')
    rfonts.set(qn('w:cs'), 'Calibri')


def add_letterhead(doc):
    """Add a stylised company letterhead at the top of the page."""
    # Company name
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(COMPANY_NAME.upper())
    run.font.name = 'Cambria'
    run.font.size = Pt(20)
    run.bold = True
    run.font.color.rgb = RGBColor(0x00, 0x5B, 0x2C)   # deep green
    p.paragraph_format.space_after = Pt(2)

    # Tagline
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run(COMPANY_TAGLINE)
    run.font.size = Pt(9)
    run.italic = True
    run.font.color.rgb = RGBColor(0x5B, 0x5B, 0x5B)
    p.paragraph_format.space_after = Pt(2)

    # Contact line
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    contact_line = (
        f"{COMPANY_ADDRESS}  ·  {COMPANY_PHONE}  ·  "
        f"{COMPANY_EMAIL}  ·  {COMPANY_WEBSITE}"
    )
    run = p.add_run(contact_line)
    run.font.size = Pt(8.5)
    run.font.color.rgb = RGBColor(0x5B, 0x5B, 0x5B)
    p.paragraph_format.space_after = Pt(4)

    # Horizontal rule (bottom border on the paragraph)
    hr = doc.add_paragraph()
    ppr = hr._p.get_or_add_pPr()
    pbdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), '12')       # 1.5 pt
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '005B2C')
    pbdr.append(bottom)
    ppr.append(pbdr)
    hr.paragraph_format.space_after = Pt(14)


def add_right_paragraph(doc, text, bold=False, size=None, space_after=None):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run(text)
    run.bold = bold
    if size:
        run.font.size = Pt(size)
    if space_after is not None:
        p.paragraph_format.space_after = Pt(space_after)
    return p


def add_paragraph(doc, text, bold=False, italic=False, size=None,
                  space_after=None, space_before=None):
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    if size:
        run.font.size = Pt(size)
    if space_after is not None:
        p.paragraph_format.space_after = Pt(space_after)
    if space_before is not None:
        p.paragraph_format.space_before = Pt(space_before)
    return p


def add_bullet(doc, text, bold_prefix=None):
    p = doc.add_paragraph(style='List Bullet')
    if bold_prefix:
        run = p.add_run(bold_prefix)
        run.bold = True
    p.add_run(text)
    p.paragraph_format.space_after = Pt(4)
    return p


# ---------------------------------------------------------------------------
# Build the letter
# ---------------------------------------------------------------------------
def build_letter(output_path="Kanch_Innovative_FAZ_Meeting_Request.docx"):
    doc = Document()
    set_base_style(doc)

    # Page margins
    for section in doc.sections:
        section.top_margin = Cm(2.0)
        section.bottom_margin = Cm(2.0)
        section.left_margin = Cm(2.2)
        section.right_margin = Cm(2.2)

    # Letterhead
    add_letterhead(doc)

    # Date
    add_right_paragraph(doc, LETTER_DATE, space_after=16)

    # Recipient block
    add_paragraph(doc, RECIPIENT_NAME, bold=True, space_after=0)
    add_paragraph(doc, RECIPIENT_ORG, space_after=0)
    add_paragraph(doc, RECIPIENT_ADDRESS, space_after=14)

    # Salutation
    add_paragraph(doc, "Dear Sir/Madam,", space_after=10)

    # Subject
    p = doc.add_paragraph()
    run = p.add_run(
        "RE: REQUEST FOR A BUSINESS MEETING TO PRESENT TWO DIGITAL SYSTEMS "
        "DEVELOPED FOR THE FOOTBALL ASSOCIATION OF ZAMBIA"
    )
    run.bold = True
    run.underline = True
    p.paragraph_format.space_after = Pt(14)

    # --- Body ---------------------------------------------------------------
    add_paragraph(
        doc,
        f"We write on behalf of {COMPANY_NAME}, a Zambian information "
        f"technology company specialising in software development and the "
        f"supply of ICT equipment. Our team recently had the privilege of "
        f"speaking with your office by telephone, during which we briefly "
        f"introduced two digital systems that we have developed with the "
        f"Football Association of Zambia in mind. As requested during that "
        f"conversation, we are now formally writing to request a business "
        f"meeting at which we can present both systems to you and your "
        f"designated team.",
    )

    add_paragraph(
        doc,
        "The two systems we would like to demonstrate are:",
        space_after=6,
    )

    add_bullet(
        doc,
        "a comprehensive public-facing web platform that serves as the "
        "official digital home of the Association. It provides news and "
        "press releases, competition and league information, live match "
        "updates, fixture and result management, player and club profiles, "
        "media galleries, ticket information, partner showcases, and "
        "governance and administrative content. The platform is responsive, "
        "fast, and built to scale with the growing digital presence of the "
        "Association.",
        bold_prefix="The Main Website — ",
    )

    add_bullet(
        doc,
        "an end-to-end solution for online ticket sales and stadium entry. "
        "It includes a competition and fixture management back-office, "
        "configurable ticket types (Open Wing, Grand Stand, VIP, VVIP, and "
        "others), seat-map setup with sections, rows and individual seats, "
        "live stadium views in 2D and 3D, secure online payments, digital "
        "tickets with QR codes, and a fast verification workflow at the "
        "stadium gates. The system is designed to reduce queues, eliminate "
        "counterfeit tickets, and give the Association real-time visibility "
        "of sales and attendance.",
        bold_prefix="The Ticketing System — ",
    )

    add_paragraph(
        doc,
        "Both systems are already functional and can be demonstrated live. "
        "They were designed with the specific needs of football administration "
        "in mind — from grassroots to elite competitions — and can be adapted "
        "to fit the Association's brand, structure, and internal workflows. "
        "We are confident that, once you have seen them in operation, you "
        "will agree that they represent a significant step forward for the "
        "digitisation of Zambian football.",
    )

    add_paragraph(
        doc,
        "We would therefore like to request a meeting of approximately "
        "forty-five (45) minutes at a venue and time of your convenience. "
        "Our preferred dates are " + PROPOSED_DATES + ", but we will gladly "
        "adjust to any date that suits your office. During the meeting we "
        "will give a guided walkthrough of both systems, answer any questions, "
        "and leave you with documentation and access credentials for a "
        "hands-on evaluation at your own pace.",
    )

    add_paragraph(
        doc,
        "We would be grateful if you could kindly advise us of a suitable "
        "date and confirm the names and roles of any colleagues you would "
        "like to include in the demonstration. Should you require any "
        "further information before the meeting, please do not hesitate to "
        "reach out to us using the contact details below.",
    )

    add_paragraph(
        doc,
        "Thank you for your time and consideration. We look forward to the "
        "opportunity to present our work to the Football Association of "
        "Zambia and to explore how we can contribute meaningfully to the "
        "growth of the game in our country.",
        space_after=18,
    )

    add_paragraph(doc, "Yours faithfully,", space_after=30)

    # Signature block
    add_paragraph(doc, "_______________________________", space_after=2)
    add_paragraph(doc, SENDER_NAME, bold=True, space_after=0)
    add_paragraph(doc, SENDER_TITLE, space_after=0)
    add_paragraph(doc, COMPANY_NAME, space_after=0)
    add_paragraph(doc, f"Email: {SENDER_EMAIL}", space_after=0)
    add_paragraph(doc, f"Phone: {SENDER_PHONE}", space_after=16)

    # Enclosures line
    p = doc.add_paragraph()
    run = p.add_run("Enclosures: ")
    run.bold = True
    p.add_run(
        "Company profile · System overview document · "
        "Two reference letters from previous clients (optional)."
    )
    p.paragraph_format.space_after = Pt(0)

    # CC line (optional, useful when sending copies)
    p = doc.add_paragraph()
    run = p.add_run("cc: ")
    run.bold = True
    p.add_run(
        "Managing Director, Kanch Innovative Technologies Limited; "
        "Project Lead, FAZ Digital Systems."
    )

    doc.save(output_path)
    print(f"Letter saved to: {output_path}")


if __name__ == "__main__":
    build_letter()