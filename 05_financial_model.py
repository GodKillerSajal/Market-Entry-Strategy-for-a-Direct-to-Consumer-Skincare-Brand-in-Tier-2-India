"""
Project 1: Market-Entry Strategy for a D2C Skincare Brand in Tier-2 India
Excel Financial Model: 3-Year P&L, Unit Economics, Break-Even Analysis
===============================================================================
"""

import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side, numbers
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, LineChart, Reference
import os

OUTPUT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                           "financials", "financial_model.xlsx")
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

wb = openpyxl.Workbook()

# =============================================================================
# STYLES
# =============================================================================
header_font = Font(name='Calibri', size=12, bold=True, color='FFFFFF')
header_fill = PatternFill(start_color='2E86AB', end_color='2E86AB', fill_type='solid')
subheader_font = Font(name='Calibri', size=11, bold=True, color='333333')
subheader_fill = PatternFill(start_color='D6EAF8', end_color='D6EAF8', fill_type='solid')
title_font = Font(name='Calibri', size=14, bold=True, color='1A1A2E')
section_font = Font(name='Calibri', size=11, bold=True, color='2E86AB')
normal_font = Font(name='Calibri', size=11)
money_fmt = '#,##0.00'
pct_fmt = '0.0%'
thin_border = Border(
    left=Side(style='thin', color='CCCCCC'),
    right=Side(style='thin', color='CCCCCC'),
    top=Side(style='thin', color='CCCCCC'),
    bottom=Side(style='thin', color='CCCCCC')
)
highlight_fill = PatternFill(start_color='E8F8F5', end_color='E8F8F5', fill_type='solid')
negative_font = Font(name='Calibri', size=11, color='C73E1D', bold=True)
positive_font = Font(name='Calibri', size=11, color='27AE60', bold=True)


def style_header_row(ws, row, cols):
    for col in range(1, cols + 1):
        cell = ws.cell(row=row, column=col)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=True)
        cell.border = thin_border


def style_data_cell(ws, row, col, fmt=None, bold=False):
    cell = ws.cell(row=row, column=col)
    cell.font = Font(name='Calibri', size=11, bold=bold)
    cell.border = thin_border
    cell.alignment = Alignment(horizontal='right' if col > 1 else 'left')
    if fmt:
        cell.number_format = fmt


# =============================================================================
# SHEET 1: ASSUMPTIONS
# =============================================================================
ws = wb.active
ws.title = "Assumptions"
ws.sheet_properties.tabColor = '2E86AB'

ws.merge_cells('A1:E1')
ws['A1'] = 'D2C Skincare Brand — Financial Model Assumptions'
ws['A1'].font = title_font
ws['A1'].alignment = Alignment(horizontal='left')

assumptions = [
    ('', '', '', '', ''),
    ('REVENUE ASSUMPTIONS', '', '', '', ''),
    ('', '', 'Year 1', 'Year 2', 'Year 3'),
    ('Total Revenue (Rs Cr)', '', 2.0, 8.5, 22.0),
    ('Revenue Growth Rate', '', '', '325%', '159%'),
    ('Total Customers', '', 8000, 35000, 90000),
    ('Average Order Value (Rs)', '', 250, 280, 310),
    ('Orders per Customer per Year', '', 1.0, 0.86, 0.79),
    ('', '', '', '', ''),
    ('COST STRUCTURE', '', '', '', ''),
    ('COGS as % of Revenue', '', '60%', '55%', '50%'),
    ('Marketing as % of Revenue', '', '30%', '25%', '20%'),
    ('Operating Expenses as % of Revenue', '', '18%', '14%', '12%'),
    ('', '', '', '', ''),
    ('UNIT ECONOMICS', '', '', '', ''),
    ('Customer Acquisition Cost (Rs)', '', 350, 280, 220),
    ('Customer Lifetime Value (Rs)', '', 750, 1050, 1350),
    ('LTV/CAC Ratio', '', '2.1x', '3.8x', '6.1x'),
    ('Gross Margin per Order (Rs)', '', 100, 126, 155),
    ('Contribution Margin per Order (Rs)', '', 25, 56, 93),
    ('', '', '', '', ''),
    ('MARKET DATA', '', '', '', ''),
    ('India Skincare Market TAM (USD B)', '', 9.06, '', ''),
    ('D2C Beauty Market (Rs Lakh Cr)', '', 6.6, '', ''),
    ('SAM - Tier-2 D2C Skincare (Rs Cr)', '', 17325, '', ''),
    ('Target SOM Year 1 (Rs Cr)', '', 866, '', ''),
    ('', '', '', '', ''),
    ('BREAK-EVEN', '', '', '', ''),
    ('Break-even Month', '', 'Month 19', '', ''),
    ('Initial Investment Required (Rs Cr)', '', 1.5, '', ''),
]

for i, (a, b, c, d, e) in enumerate(assumptions, start=3):
    ws.cell(row=i, column=1, value=a).font = section_font if a.isupper() and a else normal_font
    ws.cell(row=i, column=2, value=b)
    for col_idx, val in enumerate([c, d, e], start=3):
        cell = ws.cell(row=i, column=col_idx, value=val if val != '' else None)
        cell.font = normal_font
        cell.alignment = Alignment(horizontal='right')

# Column widths
ws.column_dimensions['A'].width = 38
for c in ['B', 'C', 'D', 'E']:
    ws.column_dimensions[c].width = 16


# =============================================================================
# SHEET 2: 3-YEAR P&L
# =============================================================================
ws2 = wb.create_sheet("3-Year P&L")
ws2.sheet_properties.tabColor = '44BBA4'

ws2.merge_cells('A1:E1')
ws2['A1'] = '3-Year Profit & Loss Statement (Rs Crore)'
ws2['A1'].font = title_font

# Headers
headers = ['', 'Year 1', 'Year 2', 'Year 3', 'CAGR / Notes']
for col, h in enumerate(headers, 1):
    ws2.cell(row=3, column=col, value=h)
style_header_row(ws2, 3, 5)

# P&L Data
pl_data = [
    ('REVENUE', '', '', '', ''),
    ('Product Revenue', 2.0, 8.5, 22.0, '233% CAGR'),
    ('Total Revenue', 2.0, 8.5, 22.0, ''),
    ('', '', '', '', ''),
    ('COST OF GOODS SOLD', '', '', '', ''),
    ('COGS', -1.20, -4.68, -11.00, '60%→50% of Rev'),
    ('Gross Profit', 0.80, 3.82, 11.00, '40%→50% margin'),
    ('Gross Margin %', '40.0%', '44.9%', '50.0%', '+1000 bps'),
    ('', '', '', '', ''),
    ('OPERATING EXPENSES', '', '', '', ''),
    ('Marketing Expense', -0.60, -2.12, -4.40, '30%→20% of Rev'),
    ('Salaries & Payroll', -0.18, -0.60, -1.54, ''),
    ('Technology & Platform', -0.06, -0.18, -0.44, ''),
    ('Logistics & Fulfillment', -0.08, -0.25, -0.66, ''),
    ('Office & Admin', -0.04, -0.16, -0.66, ''),
    ('Total OpEx', -0.96, -3.31, -7.70, ''),
    ('', '', '', '', ''),
    ('EBITDA', -0.16, 0.51, 3.30, 'Turnaround in Y2'),
    ('EBITDA Margin %', '-8.0%', '6.0%', '15.0%', ''),
    ('', '', '', '', ''),
    ('Depreciation & Amortization', -0.03, -0.06, -0.10, ''),
    ('EBIT', -0.19, 0.45, 3.20, ''),
    ('Interest Expense', -0.05, -0.04, -0.03, ''),
    ('EBT', -0.24, 0.41, 3.17, ''),
    ('Tax (25%)', 0.00, -0.10, -0.79, 'Tax holiday Y1'),
    ('Net Income', -0.24, 0.31, 2.38, ''),
    ('', '', '', '', ''),
    ('MARGINS', '', '', '', ''),
    ('Gross Margin', '40.0%', '44.9%', '50.0%', ''),
    ('EBITDA Margin', '-8.0%', '6.0%', '15.0%', ''),
    ('Net Margin', '-12.0%', '3.6%', '10.8%', ''),
]

for i, (a, b, c, d, e) in enumerate(pl_data, start=4):
    ws2.cell(row=i, column=1, value=a)
    ws2.cell(row=i, column=5, value=e)
    if a.isupper() and a:
        ws2.cell(row=i, column=1).font = section_font
        for col in range(1, 6):
            ws2.cell(row=i, column=col).fill = subheader_fill
    elif a in ['Gross Profit', 'EBITDA', 'Net Income', 'EBT', 'EBIT']:
        ws2.cell(row=i, column=1).font = Font(name='Calibri', size=11, bold=True)
        for col_idx, val in enumerate([b, c, d], start=2):
            cell = ws2.cell(row=i, column=col_idx, value=val)
            cell.font = negative_font if isinstance(val, (int, float)) and val < 0 else positive_font
            if isinstance(val, float):
                cell.number_format = money_fmt
    else:
        for col_idx, val in enumerate([b, c, d], start=2):
            cell = ws2.cell(row=i, column=col_idx, value=val if val != '' else None)
            cell.font = normal_font
            if isinstance(val, float):
                cell.number_format = money_fmt

ws2.column_dimensions['A'].width = 35
for c in ['B', 'C', 'D', 'E']:
    ws2.column_dimensions[c].width = 16


# =============================================================================
# SHEET 3: MONTHLY BREAK-EVEN
# =============================================================================
ws3 = wb.create_sheet("Monthly Break-Even")
ws3.sheet_properties.tabColor = 'F18F01'

ws3.merge_cells('A1:H1')
ws3['A1'] = 'Monthly Financial Breakdown (24 Months)'
ws3['A1'].font = title_font

monthly_headers = ['Month', 'Revenue\n(Rs Lakhs)', 'COGS\n(Rs Lakhs)', 'Marketing\n(Rs Lakhs)',
                   'OpEx\n(Rs Lakhs)', 'EBITDA\n(Rs Lakhs)', 'Cumulative\nEBITDA (Rs Lakhs)', 'Notes']
for col, h in enumerate(monthly_headers, 1):
    ws3.cell(row=3, column=col, value=h)
style_header_row(ws3, 3, 8)

# Monthly data
import csv
monthly_data_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                  "data", "processed", "monthly_breakdown_24m.csv")

with open(monthly_data_path) as f:
    reader = csv.DictReader(f)
    rows = list(reader)

for i, row in enumerate(rows, start=4):
    month = int(row['Month'])
    rev = float(row['Revenue_Lakhs'])
    cogs = float(row['COGS_Lakhs'])
    mkt = float(row['Marketing_Lakhs'])
    opex = float(row['OpEx_Lakhs'])
    ebitda = float(row['EBITDA_Lakhs'])
    cum_ebitda = float(row['Cumulative_EBITDA_Lakhs'])
    
    ws3.cell(row=i, column=1, value=month)
    ws3.cell(row=i, column=2, value=rev).number_format = money_fmt
    ws3.cell(row=i, column=3, value=cogs).number_format = money_fmt
    ws3.cell(row=i, column=4, value=mkt).number_format = money_fmt
    ws3.cell(row=i, column=5, value=opex).number_format = money_fmt
    ws3.cell(row=i, column=6, value=ebitda)
    ws3.cell(row=i, column=7, value=cum_ebitda)
    
    # Highlight break-even row
    if i > 4 and cum_ebitda >= 0:
        prev_cum = float(rows[i-5]['Cumulative_EBITDA_Lakhs'])
        if prev_cum < 0:
            for col in range(1, 9):
                ws3.cell(row=i, column=col).fill = highlight_fill
            ws3.cell(row=i, column=8, value='BREAK-EVEN')
            ws3.cell(row=i, column=8).font = Font(name='Calibri', size=11, bold=True, color='27AE60')
    
    # Color negative EBITDA
    if ebitda < 0:
        ws3.cell(row=i, column=6).font = negative_font
    elif ebitda > 0:
        ws3.cell(row=i, column=6).font = positive_font
    
    if cum_ebitda < 0:
        ws3.cell(row=i, column=7).font = negative_font
    elif cum_ebitda > 0:
        ws3.cell(row=i, column=7).font = positive_font

for c_idx in range(1, 9):
    ws3.column_dimensions[get_column_letter(c_idx)].width = 16


# =============================================================================
# SHEET 4: UNIT ECONOMICS
# =============================================================================
ws4 = wb.create_sheet("Unit Economics")
ws4.sheet_properties.tabColor = 'A23B72'

ws4.merge_cells('A1:E1')
ws4['A1'] = 'Unit Economics & Customer Metrics'
ws4['A1'].font = title_font

ue_headers = ['Metric', 'Year 1', 'Year 2', 'Year 3', 'Trend']
for col, h in enumerate(ue_headers, 1):
    ws4.cell(row=3, column=col, value=h)
style_header_row(ws4, 3, 5)

ue_data = [
    ('CUSTOMER METRICS', '', '', '', ''),
    ('New Customers Acquired', 8000, 27000, 55000, '+587% growth'),
    ('Repeat Customers', 0, 8000, 35000, 'Retention ramp-up'),
    ('Total Active Customers', 8000, 35000, 90000, '+1025%'),
    ('Repeat Purchase Rate', '0%', '23%', '39%', 'Improving'),
    ('', '', '', '', ''),
    ('UNIT ECONOMICS', '', '', '', ''),
    ('Average Order Value (Rs)', 250, 280, 310, '+24% improvement'),
    ('Orders per Customer/Year', 1.0, 0.86, 0.79, 'Normalizing'),
    ('Annual Revenue per Customer (Rs)', 250, 241, 245, 'Stable'),
    ('', '', '', '', ''),
    ('COST METRICS', '', '', '', ''),
    ('Customer Acquisition Cost (Rs)', 350, 280, 220, '-37% reduction'),
    ('Cost per Order (Fulfillment, Rs)', 45, 40, 35, 'Scale benefits'),
    ('Gross Margin per Order (Rs)', 100, 126, 155, '+55% improvement'),
    ('Contribution Margin per Order (Rs)', 25, 56, 93, '+272% improvement'),
    ('', '', '', '', ''),
    ('LTV ANALYSIS', '', '', '', ''),
    ('Customer Lifetime Value (Rs)', 750, 1050, 1350, '+80% improvement'),
    ('LTV/CAC Ratio', '2.1x', '3.8x', '6.1x', 'Healthy scaling'),
    ('Payback Period (months)', 14, 11, 9, 'Improving'),
    ('', '', '', '', ''),
    ('CHANNEL MIX', '', '', '', ''),
    ('Own D2C Website %', '30%', '45%', '55%', 'Shift to owned'),
    ('Nykaa/Myntra %', '45%', '35%', '28%', 'Reducing dependency'),
    ('Amazon %', '25%', '15%', '12%', 'Reducing dependency'),
    ('Offline %', '0%', '5%', '5%', 'Selective expansion'),
]

for i, (a, b, c, d, e) in enumerate(ue_data, start=4):
    ws4.cell(row=i, column=1, value=a)
    ws4.cell(row=i, column=5, value=e)
    if a.isupper() and a:
        ws4.cell(row=i, column=1).font = section_font
        for col in range(1, 6):
            ws4.cell(row=i, column=col).fill = subheader_fill
    else:
        for col_idx, val in enumerate([b, c, d], start=2):
            cell = ws4.cell(row=i, column=col_idx, value=val if val != '' else None)
            cell.font = normal_font
            if isinstance(val, (int, float)):
                cell.number_format = '#,##0'

ws4.column_dimensions['A'].width = 38
for c in ['B', 'C', 'D', 'E']:
    ws4.column_dimensions[c].width = 18


# =============================================================================
# SHEET 5: PRICING STRATEGY
# =============================================================================
ws5 = wb.create_sheet("Pricing Strategy")
ws5.sheet_properties.tabColor = 'C73E1D'

ws5.merge_cells('A1:F1')
ws5['A1'] = 'Pricing Tier Strategy & Product Portfolio'
ws5['A1'].font = title_font

price_headers = ['Tier', 'Price Range (Rs)', 'Target Segment', 'Key Products', 
                 'Est. Revenue Share', 'Gross Margin %']
for col, h in enumerate(price_headers, 1):
    ws5.cell(row=3, column=col, value=h)
style_header_row(ws5, 3, 6)

pricing_data = [
    ('Mass', '199-399', 'Value-Conscious Seekers\nDigital-First Experimenters (B)',
     'Face Wash, Cleanser,\nBody Lotion', '45%', '35%'),
    ('Mid', '399-799', 'Digital-First Experimenters\nMainstream Urban Women',
     'Serum, Moisturizer,\nSunscreen, Face Mask', '40%', '45%'),
    ('Premium', '799-1,499', 'Conscious Premium Spenders',
     'Anti-Pollution Serum,\nNight Cream, Vitamin C Serum', '15%', '55%'),
]

tier_fills = [
    PatternFill(start_color='E8F8F5', end_color='E8F8F5', fill_type='solid'),
    PatternFill(start_color='D6EAF8', end_color='D6EAF8', fill_type='solid'),
    PatternFill(start_color='F5EEF8', end_color='F5EEF8', fill_type='solid'),
]

for i, (a, b, c, d, e, f) in enumerate(pricing_data, start=4):
    vals = [a, b, c, d, e, f]
    for col, val in enumerate(vals, 1):
        cell = ws5.cell(row=i, column=col, value=val)
        cell.font = normal_font
        cell.border = thin_border
        cell.fill = tier_fills[i-4]
        cell.alignment = Alignment(wrap_text=True, vertical='center')

# Set row heights
for r in range(4, 7):
    ws5.row_dimensions[r].height = 45

ws5.column_dimensions['A'].width = 12
ws5.column_dimensions['B'].width = 18
ws5.column_dimensions['C'].width = 30
ws5.column_dimensions['D'].width = 28
ws5.column_dimensions['E'].width = 20
ws5.column_dimensions['F'].width = 16

# Save workbook
wb.save(OUTPUT_PATH)
print(f"Financial model saved to: {OUTPUT_PATH}")
print("Sheets: Assumptions, 3-Year P&L, Monthly Break-Even, Unit Economics, Pricing Strategy")