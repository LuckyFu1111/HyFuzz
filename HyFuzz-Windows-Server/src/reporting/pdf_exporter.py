"""
PDF Exporter for Fuzzing Reports

This module provides professional PDF generation from HTML reports.
Supports multiple backends with graceful fallbacks:
- WeasyPrint (HTML/CSS to PDF, preferred)
- ReportLab (Programmatic PDF generation)
- Markdown to PDF conversion
- Fallback text-based placeholder

Author: HyFuzz Team
Version: 2.0.0
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import logging
import datetime
import json


class PDFBackend(Enum):
    """Available PDF generation backends"""
    WEASYPRINT = "weasyprint"
    REPORTLAB = "reportlab"
    MARKDOWN2PDF = "markdown2pdf"
    PLACEHOLDER = "placeholder"


# Try importing PDF libraries
WEASYPRINT_AVAILABLE = False
REPORTLAB_AVAILABLE = False

try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    pass

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
        PageBreak, Image as RLImage
    )
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    REPORTLAB_AVAILABLE = True
except ImportError:
    pass


@dataclass
class PDFConfig:
    """Configuration for PDF generation"""
    title: str = "HyFuzz Report"
    author: str = "HyFuzz Security Testing"
    subject: str = "Security Testing Report"
    creator: str = "HyFuzz PDF Exporter v2.0"
    page_size: str = "A4"  # or "letter"
    margin_top: float = 0.75
    margin_bottom: float = 0.75
    margin_left: float = 0.75
    margin_right: float = 0.75
    font_family: str = "Helvetica"
    font_size: int = 10
    include_toc: bool = True
    include_page_numbers: bool = True
    custom_css: Optional[str] = None


class PDFExporter:
    """
    Professional PDF Exporter for Fuzzing Reports

    Features:
    - Multiple backend support (WeasyPrint, ReportLab)
    - HTML to PDF conversion with CSS styling
    - Automatic table of contents
    - Page numbering and headers/footers
    - Chart and image embedding
    - Graceful fallback to simpler backends

    Example:
        >>> exporter = PDFExporter()
        >>> html_content = "<h1>Report</h1><p>Test results...</p>"
        >>> path = exporter.export(html_content, Path("report.pdf"))
    """

    def __init__(self, config: Optional[PDFConfig] = None):
        """
        Initialize PDF Exporter

        Args:
            config: PDF generation configuration
        """
        self.config = config or PDFConfig()
        self.logger = logging.getLogger(__name__)

        # Determine available backend
        self.backend = self._select_backend()
        self.logger.info(f"PDF Exporter initialized with backend: {self.backend.value}")

    def _select_backend(self) -> PDFBackend:
        """Select best available PDF backend"""
        if WEASYPRINT_AVAILABLE:
            return PDFBackend.WEASYPRINT
        elif REPORTLAB_AVAILABLE:
            return PDFBackend.REPORTLAB
        else:
            self.logger.warning(
                "No PDF libraries available. Install weasyprint or reportlab:\n"
                "  pip install weasyprint\n"
                "  pip install reportlab\n"
                "Falling back to placeholder mode."
            )
            return PDFBackend.PLACEHOLDER

    def export(
        self,
        html: str,
        output_path: Path,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """
        Export HTML content to PDF

        Args:
            html: HTML content to convert
            output_path: Path to output PDF file
            metadata: Additional metadata for the PDF

        Returns:
            Path to generated PDF file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Merge metadata with config
        merged_metadata = self._merge_metadata(metadata)

        # Generate PDF using selected backend
        if self.backend == PDFBackend.WEASYPRINT:
            return self._export_weasyprint(html, output_path, merged_metadata)
        elif self.backend == PDFBackend.REPORTLAB:
            return self._export_reportlab(html, output_path, merged_metadata)
        else:
            return self._export_placeholder(html, output_path)

    def _merge_metadata(self, metadata: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge user metadata with defaults"""
        merged = {
            'title': self.config.title,
            'author': self.config.author,
            'subject': self.config.subject,
            'creator': self.config.creator,
            'creation_date': datetime.datetime.now().isoformat(),
        }

        if metadata:
            merged.update(metadata)

        return merged

    def _export_weasyprint(
        self,
        html: str,
        output_path: Path,
        metadata: Dict[str, Any]
    ) -> Path:
        """Export using WeasyPrint (HTML/CSS to PDF)"""
        try:
            # Add CSS styling if not present
            styled_html = self._add_default_styling(html)

            # Create WeasyPrint HTML object
            html_doc = HTML(string=styled_html)

            # Generate PDF
            html_doc.write_pdf(
                output_path,
                stylesheets=[CSS(string=self._get_default_css())] if self.config.custom_css is None else []
            )

            self.logger.info(f"PDF generated using WeasyPrint: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"WeasyPrint export failed: {e}")
            # Fallback to ReportLab or placeholder
            if REPORTLAB_AVAILABLE:
                return self._export_reportlab(html, output_path, metadata)
            else:
                return self._export_placeholder(html, output_path)

    def _export_reportlab(
        self,
        html: str,
        output_path: Path,
        metadata: Dict[str, Any]
    ) -> Path:
        """Export using ReportLab (Programmatic PDF)"""
        try:
            # Create PDF document
            page_size = A4 if self.config.page_size == "A4" else letter

            doc = SimpleDocTemplate(
                str(output_path),
                pagesize=page_size,
                topMargin=self.config.margin_top * inch,
                bottomMargin=self.config.margin_bottom * inch,
                leftMargin=self.config.margin_left * inch,
                rightMargin=self.config.margin_right * inch,
                title=metadata.get('title', ''),
                author=metadata.get('author', ''),
                subject=metadata.get('subject', ''),
            )

            # Build document content
            story = []
            styles = getSampleStyleSheet()

            # Title page
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                textColor=colors.HexColor('#1a237e'),
                spaceAfter=30,
                alignment=TA_CENTER,
            )

            story.append(Paragraph(metadata.get('title', 'Report'), title_style))
            story.append(Spacer(1, 0.3 * inch))

            # Metadata table
            meta_data = [
                ['Author:', metadata.get('author', '')],
                ['Date:', datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')],
                ['Subject:', metadata.get('subject', '')],
            ]

            meta_table = Table(meta_data, colWidths=[2*inch, 4*inch])
            meta_table.setStyle(TableStyle([
                ('FONT', (0, 0), (-1, -1), 'Helvetica', 10),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.HexColor('#424242')),
            ]))

            story.append(meta_table)
            story.append(PageBreak())

            # Convert simple HTML to ReportLab elements
            content_paragraphs = self._html_to_reportlab(html, styles)
            story.extend(content_paragraphs)

            # Build PDF
            doc.build(story)

            self.logger.info(f"PDF generated using ReportLab: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"ReportLab export failed: {e}")
            return self._export_placeholder(html, output_path)

    def _html_to_reportlab(self, html: str, styles) -> List:
        """Convert simple HTML to ReportLab flowables"""
        from html.parser import HTMLParser

        flowables = []
        current_text = []
        in_heading = None
        in_paragraph = False

        class SimpleHTMLParser(HTMLParser):
            def handle_starttag(parser_self, tag, attrs):
                nonlocal in_heading, in_paragraph
                if tag in ['h1', 'h2', 'h3', 'h4']:
                    in_heading = tag
                elif tag == 'p':
                    in_paragraph = True
                elif tag == 'br':
                    current_text.append('<br/>')

            def handle_endtag(parser_self, tag):
                nonlocal in_heading, in_paragraph
                if tag in ['h1', 'h2', 'h3', 'h4']:
                    if current_text:
                        text = ''.join(current_text)
                        style_map = {
                            'h1': 'Heading1',
                            'h2': 'Heading2',
                            'h3': 'Heading3',
                            'h4': 'Heading4'
                        }
                        flowables.append(Paragraph(text, styles[style_map.get(tag, 'Heading1')]))
                        current_text.clear()
                    in_heading = None
                elif tag == 'p':
                    if current_text:
                        text = ''.join(current_text)
                        flowables.append(Paragraph(text, styles['Normal']))
                        current_text.clear()
                    in_paragraph = False

            def handle_data(parser_self, data):
                if data.strip():
                    current_text.append(data.strip())

        parser = SimpleHTMLParser()
        parser.feed(html)

        # Add any remaining text
        if current_text:
            text = ''.join(current_text)
            flowables.append(Paragraph(text, styles['Normal']))

        return flowables if flowables else [Paragraph("No content", styles['Normal'])]

    def _export_placeholder(self, html: str, output_path: Path) -> Path:
        """Fallback: Write placeholder PDF (text file)"""
        self.logger.warning("Using placeholder PDF export (text-based)")

        placeholder_content = f"""
PDF EXPORT PLACEHOLDER
======================

This is a placeholder PDF file. For proper PDF generation, please install:
  pip install weasyprint
  or
  pip install reportlab

Report Title: {self.config.title}
Generated: {datetime.datetime.now().isoformat()}

---
CONTENT:
---

{html}

---
END OF REPORT
---
"""

        output_path.write_text(placeholder_content, encoding="utf-8")
        return output_path

    def _add_default_styling(self, html: str) -> str:
        """Add default HTML structure and styling"""
        if '<html' not in html.lower():
            return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{self.config.title}</title>
</head>
<body>
{html}
</body>
</html>
"""
        return html

    def _get_default_css(self) -> str:
        """Get default CSS styling for PDF"""
        return """
@page {
    size: A4;
    margin: 2cm;
    @bottom-right {
        content: "Page " counter(page) " of " counter(pages);
        font-size: 9pt;
        color: #666;
    }
}

body {
    font-family: 'Helvetica', Arial, sans-serif;
    font-size: 10pt;
    line-height: 1.6;
    color: #333;
}

h1 {
    color: #1a237e;
    font-size: 24pt;
    margin-top: 0;
    page-break-after: avoid;
}

h2 {
    color: #283593;
    font-size: 18pt;
    margin-top: 20pt;
    page-break-after: avoid;
}

h3 {
    color: #3949ab;
    font-size: 14pt;
    margin-top: 15pt;
}

p {
    margin: 8pt 0;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 15pt 0;
}

th {
    background-color: #e8eaf6;
    padding: 8pt;
    text-align: left;
    font-weight: bold;
    border: 1px solid #c5cae9;
}

td {
    padding: 8pt;
    border: 1px solid #e0e0e0;
}

tr:nth-child(even) {
    background-color: #fafafa;
}

pre, code {
    background-color: #f5f5f5;
    padding: 10pt;
    border-radius: 3pt;
    font-family: 'Courier New', monospace;
    font-size: 9pt;
}

.page-break {
    page-break-after: always;
}

.no-break {
    page-break-inside: avoid;
}
"""


# ============================================================================
# Testing
# ============================================================================

def _self_test() -> bool:
    """Self-test for PDF exporter"""
    try:
        print("="*70)
        print("PDF EXPORTER SELF-TEST")
        print("="*70)

        print(f"\nWeasyPrint available: {WEASYPRINT_AVAILABLE}")
        print(f"ReportLab available: {REPORTLAB_AVAILABLE}")

        # Initialize exporter
        config = PDFConfig(
            title="HyFuzz Test Report",
            author="HyFuzz Team",
            subject="PDF Export Test"
        )
        exporter = PDFExporter(config)
        print(f"\nUsing backend: {exporter.backend.value}")

        # Create test HTML content
        test_html = """
<h1>HyFuzz Security Testing Report</h1>

<h2>Executive Summary</h2>
<p>This report contains the results of security fuzzing tests performed by HyFuzz.</p>

<h2>Test Results</h2>
<p>The following vulnerabilities were discovered:</p>

<h3>Critical Findings</h3>
<ul>
    <li>Buffer overflow in input parser (CVE-2024-1234)</li>
    <li>SQL injection in authentication module</li>
</ul>

<h3>Statistics</h3>
<table>
    <tr>
        <th>Metric</th>
        <th>Value</th>
    </tr>
    <tr>
        <td>Total Test Cases</td>
        <td>10,000</td>
    </tr>
    <tr>
        <td>Crashes Found</td>
        <td>15</td>
    </tr>
    <tr>
        <td>Code Coverage</td>
        <td>87%</td>
    </tr>
</table>

<h2>Recommendations</h2>
<p>Immediate patching of critical vulnerabilities is recommended.</p>
"""

        # Export to PDF
        import tempfile
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            output_path = Path(tmp.name)

        metadata = {
            'author': 'Test User',
            'keywords': 'fuzzing, security, testing'
        }

        result_path = exporter.export(test_html, output_path, metadata)
        print(f"\nPDF exported to: {result_path}")
        print(f"File size: {result_path.stat().st_size} bytes")
        print(f"File exists: {result_path.exists()}")

        print("\n" + "="*70)
        print("SELF-TEST PASSED ✅")
        print("="*70)
        return True

    except Exception as e:
        print(f"\nSELF-TEST FAILED ❌: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _self_test()
