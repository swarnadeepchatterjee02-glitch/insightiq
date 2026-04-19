import pandas as pd
import numpy as np
from fpdf import FPDF
from datetime import datetime

def clean(text):
    if not text:
        return ""
    text = str(text)
    replacements = {
        '\u2014': '-', '\u2013': '-', '\u2192': '->',
        '\u2019': "'", '\u2018': "'", '\u201c': '"',
        '\u201d': '"', '\u2022': '*', '\u2026': '...',
        '\u00e2': '', '\u0080': '', '\u0093': '-',
        '\u0094': '-', '\u00e2\u0080\u0094': '-'
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode('latin-1', errors='replace').decode('latin-1')


class ReportGenerator:

    def __init__(self):
        self.pdf = None

    def generate_report(self, dp, ig, insights_text=None):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        primary = (79, 142, 247)
        text_color = (40, 40, 40)
        muted = (100, 100, 120)
        green = (34, 197, 94)
        red = (239, 68, 68)

        # COVER PAGE
        pdf.set_fill_color(15, 17, 23)
        pdf.rect(0, 0, 210, 297, 'F')

        pdf.set_font("Helvetica", "B", 32)
        pdf.set_text_color(79, 142, 247)
        pdf.set_xy(20, 60)
        pdf.cell(170, 15, "InsightIQ", align="C",
                 new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 16)
        pdf.set_text_color(232, 234, 246)
        pdf.set_xy(20, 80)
        pdf.cell(170, 10, "AI-Powered Business Intelligence Report",
                 align="C", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 12)
        pdf.set_text_color(136, 146, 176)
        pdf.set_xy(20, 100)
        pdf.cell(170, 8, clean(f"Dataset: {dp.filename}"),
                 align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_xy(20, 112)
        pdf.cell(170, 8,
                 clean(f"Generated: {datetime.now().strftime('%B %d, %Y')}"),
                 align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_xy(20, 124)
        pdf.cell(170, 8,
                 clean(f"Records: {len(dp.df):,} rows x {len(dp.df.columns)} columns"),
                 align="C", new_x="LMARGIN", new_y="NEXT")

        # PAGE 2 - EXECUTIVE SUMMARY
        pdf.add_page()
        self._add_header(pdf, "Executive Summary", primary)

        metrics = dp.get_business_metrics()
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*primary)
        pdf.cell(0, 8, "Key Performance Indicators",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        x_start = 15
        card_width = 85
        card_height = 25
        x = x_start
        y = pdf.get_y()
        count = 0

        for key, value in metrics.items():
            pdf.set_fill_color(26, 29, 39)
            pdf.set_draw_color(*primary)
            pdf.rect(x, y, card_width, card_height, 'FD')

            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(*muted)
            pdf.set_xy(x + 3, y + 4)
            pdf.cell(card_width - 6, 5, clean(key.upper()))

            pdf.set_font("Helvetica", "B", 13)
            pdf.set_text_color(*primary)
            pdf.set_xy(x + 3, y + 11)
            pdf.cell(card_width - 6, 8, clean(str(value)))

            count += 1
            if count % 2 == 0:
                x = x_start
                y += card_height + 5
            else:
                x += card_width + 10

        pdf.ln(card_height + 10)

        growth = ig.get_growth_analysis(dp.df)
        if growth:
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(*primary)
            pdf.cell(0, 8, "Growth Analysis",
                     new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)

            for g in growth:
                direction = "increased" if g['growth_pct'] > 0 else "decreased"
                pdf.set_font("Helvetica", "", 10)
                pdf.set_text_color(*text_color)
                pdf.set_fill_color(240, 248, 255)
                line = clean(
                    f"  {g['metric']}: {direction} by "
                    f"{abs(g['growth_pct'])}% from "
                    f"{g['from_year']} to {g['to_year']}"
                )
                pdf.cell(0, 7, line, fill=True,
                         new_x="LMARGIN", new_y="NEXT")
                pdf.ln(1)

        # PAGE 3 - DATA QUALITY
        pdf.add_page()
        self._add_header(pdf, "Data Quality Report", primary)

        quality = dp.get_data_quality_report()
        score = quality['score']
        color = green if score >= 80 else (
            (255, 165, 0) if score >= 60 else red)

        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(*color)
        pdf.cell(0, 10, clean(f"Data Quality Score: {score}/100"),
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        stats = [
            ("Total Records", f"{quality['total_rows']:,}"),
            ("Total Columns", f"{quality['total_cols']}"),
            ("Missing Values", f"{quality['missing_total']:,}"),
            ("Duplicate Rows", f"{quality['duplicates']:,}")
        ]

        for label, value in stats:
            pdf.set_font("Helvetica", "", 10)
            pdf.set_text_color(*text_color)
            pdf.set_fill_color(245, 245, 250)
            pdf.cell(80, 7, clean(f"  {label}:"), fill=True)
            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(100, 7, clean(str(value)),
                     new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)

        pdf.ln(5)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*primary)
        pdf.cell(0, 8, "Issues Found:",
                 new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

        for issue in quality['issues']:
            clean_issue = clean(
                issue.replace('*', '[!]').replace('#', '')
            )
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(*text_color)
            pdf.cell(0, 6, f"  - {clean_issue}",
                     new_x="LMARGIN", new_y="NEXT")

        # PAGE 4 - AI INSIGHTS
        if insights_text:
            pdf.add_page()
            self._add_header(pdf, "AI-Generated Insights", primary)

            cleaned = clean(insights_text)

            # Split by newline first
            lines = cleaned.split('\n')

            for line in lines:
                line = line.strip()
                if not line:
                    pdf.ln(3)
                    continue

                # Remove ** markers
                line = line.replace('**', '')

                # Check if it's a header line
                is_header = any(k in line.upper() for k in
                    ['TOP 3 TREND', 'TOP 3 RISK', 'TOP 3 OPPORTUNIT',
                     'EXECUTIVE SUMMARY'])

                if is_header:
                    pdf.ln(4)
                    pdf.set_font("Helvetica", "B", 12)
                    pdf.set_text_color(*primary)
                    try:
                        pdf.multi_cell(0, 7, clean(line))
                    except Exception:
                        pass
                    pdf.ln(2)
                else:
                    pdf.set_font("Helvetica", "", 9)
                    pdf.set_text_color(*text_color)
                    try:
                        pdf.multi_cell(0, 6, clean(line))
                    except Exception:
                        pass
        # PAGE 5 - TOP PERFORMERS
        pdf.add_page()
        self._add_header(pdf, "Performance Analysis", primary)

        performers = ig.get_top_performers(dp.df)
        if performers and 'top' in performers:
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(*primary)
            pdf.cell(0, 8,
                     clean(f"Top Performers by "
                           f"{performers.get('numeric_col', 'Value')}"),
                     new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)

            headers = [
                performers.get('cat_col', 'Category'),
                performers.get('numeric_col', 'Value')
            ]
            col_widths = [120, 60]

            pdf.set_fill_color(*primary)
            pdf.set_text_color(255, 255, 255)
            pdf.set_font("Helvetica", "B", 10)
            for i, header in enumerate(headers):
                pdf.cell(col_widths[i], 8,
                         clean(f"  {header}"),
                         fill=True, border=1)
            pdf.ln()

            for i, item in enumerate(performers['top']):
                cat = clean(str(item.get(
                    performers['cat_col'], 'N/A'))[:40])
                val = item.get(performers['numeric_col'], 0)
                fill_color = (240, 248, 255) if i % 2 == 0 else (
                    255, 255, 255)
                pdf.set_fill_color(*fill_color)
                pdf.set_text_color(*text_color)
                pdf.set_font("Helvetica", "", 9)
                pdf.cell(col_widths[0], 7,
                         f"  {cat}", fill=True, border=1)
                pdf.cell(col_widths[1], 7,
                         clean(f"  ${val:,.0f}"),
                         fill=True, border=1)
                pdf.ln()

        # FINAL PAGE
        pdf.add_page()
        pdf.set_fill_color(15, 17, 23)
        pdf.rect(0, 0, 210, 297, 'F')

        pdf.set_font("Helvetica", "B", 18)
        pdf.set_text_color(79, 142, 247)
        pdf.set_xy(20, 120)
        pdf.cell(170, 10, "Report Generated by InsightIQ",
                 align="C", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 12)
        pdf.set_text_color(136, 146, 176)
        pdf.set_xy(20, 138)
        pdf.cell(170, 8,
                 "AI-Powered Business Intelligence Platform",
                 align="C", new_x="LMARGIN", new_y="NEXT")

        output_path = "InsightIQ_Report.pdf"
        pdf.output(output_path)
        return output_path

    def _add_header(self, pdf, title, color):
        pdf.set_fill_color(*color)
        pdf.rect(0, pdf.get_y(), 210, 12, 'F')
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(255, 255, 255)
        pdf.cell(0, 12, clean(f"  {title}"),
                 new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(40, 40, 40)
        pdf.ln(4)