# kanch_docs_generator.py
# Generates all required .docx documents for Kanch Innovative Technologies
# Requires: pip install python-docx

from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH

COMPANY = "Kanch Innovative Technologies"

def add_table(doc, headers, rows):
    table = doc.add_table(rows=1, cols=len(headers))
    table.style = 'Table Grid'
    hdr = table.rows[0].cells
    for i, h in enumerate(headers):
        hdr[i].text = h
    for row in rows:
        cells = table.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = str(val)
    doc.add_paragraph()

def add_bullets(doc, items):
    for item in items:
        doc.add_paragraph(item, style='List Bullet')

# ------------------------------------------------------------
# 1. RTSA PRICE LIST
# ------------------------------------------------------------
def create_rtsa_price_list():
    doc = Document()
    doc.add_heading(COMPANY, 0)
    doc.add_heading('RTSA System – Component Price List (USD, China MOQ 1–10)', level=1)
    doc.add_paragraph('Prices are indicative for prototype quantities. Mass production (10,000+ units) reduces costs by 30–50%. MOQ = Minimum Order Quantity.')

    doc.add_heading('1. E-Disc (Windscreen Unit)', level=2)
    headers = ['Component', 'Model', 'Function', 'MOQ', 'Unit Price (USD)']
    rows = [
        ['E-Ink Display', 'E035A26 3.5"', 'Displays tax data', '1', '7.50 – 8.94'],
        ['Microcontroller', 'ESP32-S3-WROOM-1', 'Main processor, BLE', '1', '3.10 – 5.86'],
        ['Cellular Module', 'SIMCom A7670C', 'M2M LTE Cat-1', '1', '3.25 – 4.50'],
        ['GPS Module', 'Quectel L86', 'Live location tracking', '1', '5.00 – 7.00'],
        ['Qi Receiver IC', 'BQ51052B', 'Wireless charging receiver', '1', '2.40 – 4.70'],
        ['Battery', 'LiFePO4 1000mAh', 'High-temp safe battery', '10', '2.00 – 4.00'],
        ['Charge Controller', 'IP3255', 'LiFePO4 charging', '1', '0.10 – 0.88'],
        ['Casing', 'TPU bezel + PC back', 'IP54 enclosure', '10', '1.50 – 2.50'],
        ['PCB & Passives', '4-layer FR4', 'Resistors, capacitors, LEDs', '10', '1.60 – 2.00'],
    ]
    add_table(doc, headers, rows)
    doc.add_paragraph('Subtotal E-Disc: ~$26.45 – $40.38')

    doc.add_heading('2. Wireless Power Adapter', level=2)
    rows = [
        ['Microcontroller', 'ESP32-C3', 'BLE and logic control', '1', '1.20 – 2.00'],
        ['Qi Transmitter IC', 'IP6829', '5W wireless power transmit', '10', '0.48 – 0.80'],
        ['Battery', 'Li-Po 5000mAh', 'Portable power bank', '10', '2.50 – 4.00'],
        ['Power Management', 'IP5306', 'USB-C charging & boost', '10', '0.30 – 0.50'],
        ['Casing', 'ABS + silicone pad', 'Non-slip enclosure', '10', '1.20 – 1.80'],
        ['PCB & Passives', '2-layer FR4', 'Button, LEDs, USB-C', '10', '0.80 – 1.20'],
    ]
    add_table(doc, headers, rows)
    doc.add_paragraph('Subtotal Adapter: ~$6.48 – $10.30')

    doc.add_heading('3. RTSA Patrol Scanner (Officer Handheld/Vehicle Mounted)', level=2)
    rows = [
        ['Microcontroller', 'ESP32-S3', 'Main processor', '1', '3.10 – 5.86'],
        ['Touchscreen', '5" or 7" IPS', 'Displays plates & direction', '1', '12.00 – 18.00'],
        ['BLE AoA Antenna Array', 'Custom 4-antenna', 'Direction finding (angle of arrival)', '1', '10.00 – 15.00'],
        ['GPS Module', 'Quectel L86', 'Officer location', '1', '5.00 – 7.00'],
        ['4G LTE Module', 'SIMCom A7670C', 'Server sync', '1', '3.25 – 4.50'],
        ['Battery', 'Li-Po 10000mAh', 'All-day operation', '5', '6.00 – 9.00'],
        ['Qi Receiver', 'BQ51052B', 'Wireless charging', '1', '2.40 – 4.70'],
        ['Rugged Casing', 'ABS + TPU overmold', 'Drop-resistant', '5', '4.00 – 6.00'],
        ['PCB & Passives', '4-layer FR4', 'Components', '5', '2.50 – 3.50'],
    ]
    add_table(doc, headers, rows)
    doc.add_paragraph('Subtotal Scanner: ~$48.25 – $73.56')

    doc.add_heading('4. Complete RTSA Set per Vehicle + Officer', level=2)
    rows = [
        ['E-Disc', '1', '~$26.45 – $40.38'],
        ['Wireless Power Adapter', '1', '~$6.48 – $10.30'],
        ['RTSA Patrol Scanner', '1 per officer', '~$48.25 – $73.56'],
        ['Total per vehicle + one scanner', '', '~$81.18 – $124.24'],
    ]
    add_table(doc, ['Item', 'Qty', 'Cost'], rows)

    doc.save('RTSA_Price_List.docx')
    print('Created RTSA_Price_List.docx')

# ------------------------------------------------------------
# 2. LCC PRICE LIST
# ------------------------------------------------------------
def create_lcc_price_list():
    doc = Document()
    doc.add_heading(COMPANY, 0)
    doc.add_heading('LCC System – Component Price List (USD, China MOQ 1–10)', level=1)
    doc.add_paragraph('Prices are indicative for prototype quantities. Mass production reduces costs by 30–50%. MOQ = Minimum Order Quantity.')

    doc.add_heading('1. LCC Portrait Display Device (Certificate Display)', level=2)
    headers = ['Component', 'Model', 'Function', 'MOQ', 'Unit Price (USD)']
    rows = [
        ['E-Ink Display', '7.5" or 10.1" portrait', 'Displays municipal certificates', '1', '22.00 – 30.00'],
        ['Microcontroller', 'ESP32-S3-WROOM-1', 'Main processor', '1', '3.10 – 5.86'],
        ['Cellular Module', 'SIMCom A7670C', 'M2M LTE Cat-1', '1', '3.25 – 4.50'],
        ['GPS Module', 'Quectel L86', 'Live location', '1', '5.00 – 7.00'],
        ['Open/Closed Sensor', 'Reed switch + PIR', 'Detects door/motion', '5', '2.00 – 3.50'],
        ['Qi Receiver IC', 'BQ51052B', 'Wireless charging', '1', '2.40 – 4.70'],
        ['Battery', 'LiFePO4 2000mAh', 'High-temp safe', '10', '4.00 – 6.00'],
        ['Charge Controller', 'IP3255', 'LiFePO4 charging', '1', '0.10 – 0.88'],
        ['Casing', 'Wall-mount ABS/PC', 'Secure enclosure', '10', '2.50 – 4.00'],
        ['PCB & Passives', '4-layer FR4', 'Components', '10', '2.00 – 2.80'],
    ]
    add_table(doc, headers, rows)
    doc.add_paragraph('Subtotal LCC Portrait Display: ~$46.35 – $69.24')

    doc.add_heading('2. LCC Wireless Power Adapter', level=2)
    rows = [
        ['Microcontroller', 'ESP32-C3', 'BLE and logic', '1', '1.20 – 2.00'],
        ['Qi Transmitter IC', 'IP6829', '5W transmit', '10', '0.48 – 0.80'],
        ['Battery', 'Li-Po 5000mAh', 'Portable power bank', '10', '2.50 – 4.00'],
        ['Power Management', 'IP5306', 'USB-C charging', '10', '0.30 – 0.50'],
        ['Casing', 'ABS + silicone', 'Non-slip', '10', '1.20 – 1.80'],
        ['PCB & Passives', '2-layer FR4', 'Button, LEDs', '10', '0.80 – 1.20'],
    ]
    add_table(doc, headers, rows)
    doc.add_paragraph('Subtotal LCC Adapter: ~$6.48 – $10.30')

    doc.add_heading('3. LCC Inspector Handheld Scanner', level=2)
    rows = [
        ['Microcontroller', 'ESP32-S3', 'Main processor', '1', '3.10 – 5.86'],
        ['Touchscreen', '5" or 7" IPS', 'Displays compliance map', '1', '12.00 – 18.00'],
        ['BLE AoA Antenna', 'Custom 4-antenna', 'Direction finding', '1', '10.00 – 15.00'],
        ['GPS Module', 'Quectel L86', 'Inspector location', '1', '5.00 – 7.00'],
        ['4G LTE Module', 'SIMCom A7670C', 'Server sync', '1', '3.25 – 4.50'],
        ['Battery', 'Li-Po 10000mAh', 'All-day use', '5', '6.00 – 9.00'],
        ['Qi Receiver', 'BQ51052B', 'Wireless charging', '1', '2.40 – 4.70'],
        ['Rugged Casing', 'ABS + TPU', 'Drop-resistant', '5', '4.00 – 6.00'],
        ['PCB & Passives', '4-layer FR4', 'Components', '5', '2.50 – 3.50'],
    ]
    add_table(doc, headers, rows)
    doc.add_paragraph('Subtotal LCC Inspector Scanner: ~$48.25 – $73.56')

    doc.add_heading('4. LCC Command Dashboard (Software + Existing Hardware)', level=2)
    rows = [
        ['Dashboard Software', 'Custom Python/Web', 'Colored maps: green/red', '1', 'Development cost only'],
        ['Large Display', 'Existing TV/monitor', 'Not manufactured', '—', '—'],
    ]
    add_table(doc, ['Item', 'Model', 'Function', 'MOQ', 'Unit Price'], rows)

    doc.add_heading('5. Complete LCC Set per Business + Inspector', level=2)
    rows = [
        ['LCC Portrait Display', '1 per business', '~$46.35 – $69.24'],
        ['LCC Wireless Adapter', '1 per business', '~$6.48 – $10.30'],
        ['LCC Inspector Scanner', '1 per inspector', '~$48.25 – $73.56'],
        ['Total per business + one scanner', '', '~$101.08 – $153.10'],
    ]
    add_table(doc, ['Item', 'Qty', 'Cost'], rows)

    doc.save('LCC_Price_List.docx')
    print('Created LCC_Price_List.docx')

# ------------------------------------------------------------
# 3. TECHNICAL DESIGNS
# ------------------------------------------------------------
def create_technical_designs():
    doc = Document()
    doc.add_heading(COMPANY, 0)
    doc.add_heading('Technical Designs for Manufacturers – RTSA & LCC Systems', level=1)

    doc.add_heading('1. RTSA E-Disc', level=2)
    doc.add_paragraph('Dimensions: 100 mm diameter × 8.5 mm thickness. Materials: TPU bezel (front), polycarbonate back, aluminium mid-frame. 3M VHB adhesive only on TPU bezel ring. E-Ink screen recessed 1 mm behind front face to create thermal air gap. Qi receiver coil 40 mm behind PCB. GPS antenna placed on top edge. SIM slot sealed with rubber gasket. LEDs: red (low battery), green (charging). IP54 rated. Operating temp: -10°C to +80°C. Battery: LiFePO4 1000mAh. MCU: ESP32-S3 with secure boot and flash encryption. Cellular: SIMCom A7670C. GPS: Quectel L86. Firmware: MicroPython; uses CoAP over private APN. Thermal throttling: disable Qi charging above 65°C; safe mode above 80°C.')

    doc.add_heading('2. RTSA Wireless Power Adapter', level=2)
    doc.add_paragraph('Dimensions: 100 × 65 × 18 mm. Top: non-slip silicone with 50 mm Qi transmitter coil. Front edge: USB-C input, 4× LED battery indicators, multi-function button. Internal: 5000mAh Li-Po, IP6829 Qi transmitter, ESP32-C3, IP5306. Foreign object detection (FOD). BLE communication with disc for screen toggle. Short press: screen on/off; long press: charging on/off. Operating temp: -10°C to +60°C.')

    doc.add_heading('3. RTSA Patrol Scanner', level=2)
    doc.add_paragraph('Handheld or vehicle-mounted. Dimensions: 180 × 90 × 30 mm. 5" or 7" IPS touchscreen. 4-antenna BLE AoA array for direction finding. ESP32-S3, SIMCom A7670C, Quectel L86 GPS, 10000mAh Li-Po, Qi receiver. Rugged ABS + TPU casing. Software: scans BLE advertisements from discs within 100 m. Each disc broadcasts encrypted beacon containing hashed plate, compliance status, direction data. Scanner aggregates, displays plates of non-compliant vehicles, shows direction arrow. QR scanner for fraud verification. Syncs with central server via 4G. Can be charged wirelessly or via USB-C.')

    doc.add_heading('4. RTSA GPS Tracking', level=2)
    doc.add_paragraph('Every E-Disc includes Quectel L86 GPS. Location transmitted every 5 minutes via M2M. Can be triggered remotely from central system for live tracking. Used for stolen vehicle recovery, compliance mapping, and fleet oversight. Privacy: location data encrypted; only authorized RTSA officials can access.')

    doc.add_heading('5. LCC Portrait Display Device', level=2)
    doc.add_paragraph('Dimensions: 250 × 180 × 12 mm (portrait). 7.5" or 10.1" E-Ink portrait display. Wall-mount ABS/PC casing. ESP32-S3, SIMCom A7670C, Quectel L86 GPS, reed switch + PIR motion sensor, Qi receiver, LiFePO4 2000mAh. Displays business levy, fire certificate, health certificate, etc. Certificates slide automatically if multiple. Updates via server polling LCC payment API every 1–2 minutes. Open/closed detection: if door closed but PIR detects motion, alert sent to inspector scanner. GPS for live location. Charged wired (USB-C) or wirelessly.')

    doc.add_heading('6. LCC Inspector Handheld Scanner', level=2)
    doc.add_paragraph('Similar hardware to RTSA Patrol Scanner. Software displays colored map: green = compliant, red = non-compliant. Receives open/closed sensor alerts. Direction finding to locate non-compliant premises. QR scan for certificate verification. Syncs with LCC Command Dashboard.')

    doc.add_heading('7. LCC Command Dashboard', level=2)
    doc.add_paragraph('Web-based dashboard for Director of Finance, Town Clerk, Mayor. Displays colored maps (green/red) of Lusaka. Real-time compliance status. Drill-down by business, certificate type, expiry. API integration with LCC payment system. Alerts for non-compliant premises. Access control by role.')

    doc.add_heading('8. Server & API Integration', level=2)
    doc.add_paragraph('Central server: Python/PostgreSQL. Polls RTSA and LCC existing online payment APIs every 1–2 minutes. On detecting new payment, updates client gadget via MQTT/CoAP over M2M. Uses AES-256 encryption. M2M SIMs on private APN – no internet bundles needed. Fallback SMS for critical updates. Supports OTA firmware updates.')

    doc.add_heading('9. Standards & Compliance', level=2)
    add_bullets(doc, [
        'ISO 9001 – Quality management',
        'ISO 14001 – Environmental management',
        'IEC 62368-1 – Safety of electronic equipment',
        'ISO 16750 – Road vehicle environmental conditions',
        'ZICTA type approval – Zambia',
        'CE / FCC – Export markets',
        'WEEE / ZEMA – E-waste disposal'
    ])

    doc.save('Technical_Designs_RTSA_LCC.docx')
    print('Created Technical_Designs_RTSA_LCC.docx')

# ------------------------------------------------------------
# 4. INVESTOR PROPOSAL
# ------------------------------------------------------------
def create_investor_proposal():
    doc = Document()
    doc.add_heading(COMPANY, 0)
    doc.add_heading('Business Proposal for Investors', level=1)
    doc.add_paragraph('Executive Summary: Kanch Innovative Technologies has developed a patented electronic road tax disc and municipal certificate display system. It replaces paper discs and certificates with dynamic E-Ink devices that update automatically via M2M cellular networks. The system includes patrol scanners, GPS tracking, and API integration with existing government payment systems. Target markets: RTSA (Zambia) and Lusaka City Council, with global expansion potential.')

    doc.add_heading('Problem', level=2)
    add_bullets(doc, [
        'Paper discs and certificates are easily forged, damaged, and require manual printing/courier.',
        'Traffic officers stop every vehicle to check compliance, causing congestion.',
        'Businesses must queue for hard-copy certificates.',
        'No real-time visibility of compliance or stolen vehicles.'
    ])

    doc.add_heading('Solution', level=2)
    add_bullets(doc, [
        'E-Disc with E-Ink display, M2M SIM, GPS, Qi wireless charging.',
        'RTSA Patrol Scanner: detects all discs within 100m, displays non-compliant plates and direction.',
        'LCC Portrait Display: shows municipal certificates, detects open/closed premises.',
        'LCC Inspector Scanner: colored maps, non-compliance alerts.',
        'Central server polls existing payment APIs every 1–2 minutes and pushes updates.'
    ])

    doc.add_heading('Market Size', level=2)
    doc.add_paragraph('Zambia has over 1 million registered vehicles and over 50,000 businesses in Lusaka alone. Initial target: 100,000 vehicles and 10,000 businesses in first 3 years. Global market: millions of vehicles and businesses.')

    doc.add_heading('Business Model', level=2)
    add_bullets(doc, [
        'Hardware sales: E-Disc, adapters, scanners.',
        'SaaS subscription: monthly fee per device for server, updates, GPS tracking.',
        'API integration fees: one-time setup for RTSA/LCC.',
        'Maintenance and support contracts.'
    ])

    doc.add_heading('Financial Projections (USD)', level=2)
    rows = [
        ['Year 1', '10,000 vehicles', '$350,000', '$120,000', '$230,000'],
        ['Year 2', '50,000 vehicles', '$1,750,000', '$600,000', '$1,150,000'],
        ['Year 3', '100,000 vehicles', '$3,500,000', '$1,200,000', '$2,300,000'],
    ]
    add_table(doc, ['Year', 'Units', 'Revenue', 'Cost', 'Profit'], rows)

    doc.add_heading('Investment Required', level=2)
    doc.add_paragraph('Seeking $500,000 USD for: tooling ($50k), first production run ($300k), server development ($50k), marketing ($30k), working capital ($70k).')

    doc.add_heading('Team', level=2)
    doc.add_paragraph('Kanch Innovative Technologies – Zambian engineering team with expertise in embedded systems, Python, and telecom. Partnering with Shenzhen manufacturers for production.')

    doc.add_heading('Exit Strategy', level=2)
    doc.add_paragraph('Acquisition by RTSA/LCC, telecom operator, or smart city company. IPO on Lusaka Securities Exchange in 7–10 years.')

    doc.save('Investor_Proposal_Kanch_Innovative_Technologies.docx')
    print('Created Investor_Proposal_Kanch_Innovative_Technologies.docx')

# ------------------------------------------------------------
# 5. RTSA PROPOSAL
# ------------------------------------------------------------
def create_rtsa_proposal():
    doc = Document()
    doc.add_heading(COMPANY, 0)
    doc.add_heading('Proposal to Road Transport and Safety Agency (RTSA)', level=1)

    doc.add_heading('1. Executive Summary', level=2)
    doc.add_paragraph('Kanch Innovative Technologies proposes to replace paper road tax discs with electronic E-Ink discs that update automatically. The system includes a patrol scanner for officers, GPS tracking, and API integration with RTSA payment systems. This will reduce traffic congestion, eliminate fraud, and provide real-time compliance data.')

    doc.add_heading('2. Current Challenges', level=2)
    add_bullets(doc, [
        'Paper discs are easily forged and damaged.',
        'Officers stop every vehicle, causing traffic jams.',
        'No real-time verification of compliance.',
        'Difficult to track stolen vehicles.'
    ])

    doc.add_heading('3. Proposed Solution', level=2)
    add_bullets(doc, [
        'E-Disc: 3.5" E-Ink, M2M SIM, GPS, Qi wireless charging, tamper detection.',
        'Wireless Power Adapter: portable charging for disc.',
        'RTSA Patrol Scanner: detects all discs within 100m, displays non-compliant plates and direction. QR scanner for fraud.',
        'Central server: polls RTSA payment API every 1–2 minutes, pushes updates to discs.',
        'GPS tracking: live location of all discs, triggered remotely for stolen vehicles.'
    ])

    doc.add_heading('4. Benefits to RTSA', level=2)
    add_bullets(doc, [
        'Reduce traffic congestion by only stopping non-compliant vehicles.',
        'Eliminate paper disc fraud and printing costs.',
        'Real-time compliance dashboard for management.',
        'Stolen vehicle recovery via GPS.',
        'Automated updates – no queueing for citizens.'
    ])

    doc.add_heading('5. Implementation Plan', level=2)
    rows = [
        ['Phase 1', 'Prototype & testing', '3 months', '$50,000'],
        ['Phase 2', 'Pilot with 1,000 vehicles', '6 months', '$200,000'],
        ['Phase 3', 'Full rollout', '12 months', '$1,500,000'],
    ]
    add_table(doc, ['Phase', 'Activity', 'Duration', 'Cost (USD)'], rows)

    doc.add_heading('6. Cost per Vehicle', level=2)
    doc.add_paragraph('E-Disc + Adapter: ~$33–$51 USD. Patrol Scanner: ~$48–$74 USD per officer. Monthly SaaS: $2 per vehicle for server, updates, GPS.')

    doc.add_heading('7. Conclusion', level=2)
    doc.add_paragraph('Kanch Innovative Technologies is ready to partner with RTSA to modernize road tax compliance. We request a pilot program to demonstrate the system.')

    doc.save('RTSA_Proposal.docx')
    print('Created RTSA_Proposal.docx')

# ------------------------------------------------------------
# 6. LCC PROPOSAL
# ------------------------------------------------------------
def create_lcc_proposal():
    doc = Document()
    doc.add_heading(COMPANY, 0)
    doc.add_heading('Proposal to Lusaka City Council (LCC)', level=1)

    doc.add_heading('1. Executive Summary', level=2)
    doc.add_paragraph('Kanch Innovative Technologies proposes a digital municipal certificate display system. Instead of paper certificates hung on walls, businesses will use a portrait E-Ink device that updates automatically when payments are made. Inspectors will use handheld scanners with colored maps (green/red) to target only non-compliant premises. GPS and open/closed sensors will ensure compliance.')

    doc.add_heading('2. Current Challenges', level=2)
    add_bullets(doc, [
        'Businesses must queue for hard-copy certificates.',
        'Paper certificates are easily forged or damaged.',
        'Inspectors waste time entering compliant premises.',
        'No real-time view of compliance across Lusaka.'
    ])

    doc.add_heading('3. Proposed Solution', level=2)
    add_bullets(doc, [
        'LCC Portrait Display: 7.5"–10.1" E-Ink, displays business levy, fire certificate, health certificate, etc. Slides if multiple.',
        'Wireless Power Adapter: portable charging.',
        'LCC Inspector Scanner: colored map (green/red), direction finding, open/closed alerts.',
        'GPS tracking: live location of all displays.',
        'Open/closed sensor: detects when premises are opened/closed, alerts inspectors.',
        'Central server: polls LCC payment API every 1–2 minutes, updates displays.',
        'Command Dashboard: big screen for Director of Finance, Town Clerk, Mayor.'
    ])

    doc.add_heading('4. Benefits to LCC', level=2)
    add_bullets(doc, [
        'Eliminate paper certificate printing and queueing.',
        'Inspectors focus only on non-compliant businesses.',
        'Real-time compliance map of Lusaka.',
        'Reduce fraud and increase revenue.',
        'Data-driven decision making.'
    ])

    doc.add_heading('5. Implementation Plan', level=2)
    rows = [
        ['Phase 1', 'Prototype & testing', '3 months', '$40,000'],
        ['Phase 2', 'Pilot with 500 businesses', '6 months', '$150,000'],
        ['Phase 3', 'Full rollout', '12 months', '$800,000'],
    ]
    add_table(doc, ['Phase', 'Activity', 'Duration', 'Cost (USD)'], rows)

    doc.add_heading('6. Cost per Business', level=2)
    doc.add_paragraph('LCC Portrait Display + Adapter: ~$53–$80 USD. Inspector Scanner: ~$48–$74 USD per inspector. Monthly SaaS: $3 per business for server, updates, GPS, sensors.')

    doc.add_heading('7. Conclusion', level=2)
    doc.add_paragraph('Kanch Innovative Technologies is ready to partner with LCC to digitize municipal certificates and streamline compliance. We request a pilot program to demonstrate the system.')

    doc.save('LCC_Proposal.docx')
    print('Created LCC_Proposal.docx')

# ------------------------------------------------------------
# MAIN
# ------------------------------------------------------------
if __name__ == '__main__':
    create_rtsa_price_list()
    create_lcc_price_list()
    create_technical_designs()
    create_investor_proposal()
    create_rtsa_proposal()
    create_lcc_proposal()
    print('\nAll documents generated successfully.')