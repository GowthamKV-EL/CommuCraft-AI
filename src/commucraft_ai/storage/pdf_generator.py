"""PDF generation module for daily learning content.

This module provides functionality to generate PDF files from daily learning content,
serving as a reliable fallback when Confluence is unavailable.
"""

from datetime import datetime
from pathlib import Path
from typing import Any

from commucraft_ai.utils.logger import setup_logger

logger = setup_logger()


class PDFGenerator:
    """Generate PDF files from daily learning content.

    This class handles PDF creation for daily learning content with proper formatting,
    including vocabulary lists and learning objectives. It serves as a fallback storage
    mechanism when Confluence is unavailable.
    """

    def __init__(self, output_dir: str = "data/pdf_content") -> None:
        """Initialize PDF generator with output directory.

        Args:
            output_dir (str): Directory where PDF files will be saved.
                Defaults to "data/pdf_content".

        Returns:
            None
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"PDF generator initialized with output directory: {self.output_dir}")

    def generate_pdf_from_content(self, content: dict[str, Any]) -> str:
        """Generate a PDF file from daily learning content.

        Creates a formatted PDF with the daily learning content including intro message,
        paragraph, and vocabulary list. The PDF is saved with a date-based filename.

        Args:
            content (dict[str, Any]): Daily learning content dictionary containing:
                - date (str): Date in YYYY-MM-DD format
                - role (str): User's job role
                - proficiency_level (str): User's proficiency level
                - intro_message (str): Learning focus message
                - paragraph (str): Main learning paragraph
                - vocabulary (list[dict]): List of vocabulary words with details

        Returns:
            str: Path to the generated PDF file.

        Errors:
            RuntimeError: If PDF generation fails or file cannot be written.

        Example:
            Input: content = {
                "date": "2026-04-01",
                "role": "bioinformatics scientist",
                "intro_message": "Today's Focus: Data Analysis",
                "paragraph": "...",
                "vocabulary": [...]
            }
            Output: "data/pdf_content/2026-04-01.pdf"
        """
        try:
            date = content.get("date", datetime.now().strftime("%Y-%m-%d"))
            filename = f"{date}.pdf"
            filepath = self.output_dir / filename

            # Import reportlab here to avoid hard dependency if not needed
            try:
                from reportlab.lib.pagesizes import letter
                from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
                from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
                from reportlab.lib import colors
                from reportlab.lib.units import inch
            except ImportError:
                # Fallback: generate simple text-based PDF if reportlab not available
                return self._generate_text_pdf(content, filepath)

            # Create PDF document
            doc = SimpleDocTemplate(str(filepath), pagesize=letter, topMargin=0.5 * inch, bottomMargin=0.5 * inch)

            # Define styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=16,
                textColor=colors.HexColor("#1F4788"),
                spaceAfter=12,
                alignment=1,  # Center alignment
            )
            heading_style = ParagraphStyle(
                "CustomHeading",
                parent=styles["Heading2"],
                fontSize=12,
                textColor=colors.HexColor("#2E5090"),
                spaceAfter=6,
                spaceBefore=6,
            )

            # Build document content
            story = []

            # Title
            title_text = "CommuCraft Daily Learning"
            story.append(Paragraph(title_text, title_style))
            story.append(Spacer(1, 0.2 * inch))

            # Date and role info
            date_str = content.get("date", date)
            role = content.get("role", "N/A")
            level = content.get("proficiency_level", "N/A")
            info_text = f"<b>Date:</b> {date_str} | <b>Role:</b> {role} | <b>Level:</b> {level}"
            story.append(Paragraph(info_text, styles["Normal"]))
            story.append(Spacer(1, 0.15 * inch))

            # Intro message
            intro = content.get("intro_message", "")
            if intro:
                story.append(Paragraph("<b>Today's Focus:</b>", heading_style))
                story.append(Paragraph(intro, styles["Normal"]))
                story.append(Spacer(1, 0.1 * inch))

            # Main paragraph
            story.append(Paragraph("<b>Learning Content:</b>", heading_style))
            paragraph_text = content.get("paragraph", "")
            story.append(Paragraph(paragraph_text, styles["Normal"]))
            story.append(Spacer(1, 0.15 * inch))

            # Vocabulary table
            story.append(Paragraph("<b>Vocabulary:</b>", heading_style))
            vocab_data: list[list[str]] = [["Word", "Meaning", "Example", "Pronunciation"]]

            for word_obj in content.get("vocabulary", []):
                if isinstance(word_obj, dict):
                    word = word_obj.get("word", "")
                    meaning = word_obj.get("meaning", "")
                    example = word_obj.get("usage_example", "")
                    phonetic = word_obj.get("phonetic", "") or word_obj.get("pronunciation", "")

                    vocab_data.append([word, meaning, example, phonetic])

            # Create vocabulary table
            vocab_table = Table(vocab_data, colWidths=[1.2 * inch, 1.8 * inch, 1.5 * inch, 1.0 * inch])
            vocab_table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2E5090")),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("FONTSIZE", (0, 0), (-1, 0), 10),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ("FONTSIZE", (0, 1), (-1, -1), 8),
                        ("VALIGN", (0, 0), (-1, -1), "TOP"),
                    ]
                )
            )
            story.append(vocab_table)

            # Add timestamp
            story.append(Spacer(1, 0.2 * inch))
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            story.append(Paragraph(f"<i>Generated: {timestamp}</i>", styles["Normal"]))

            # Build PDF
            doc.build(story)
            logger.info(f"✓ PDF generated successfully: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Failed to generate PDF: {str(e)}", exc_info=True)
            raise RuntimeError(f"PDF generation failed: {str(e)}") from e

    def _generate_text_pdf(self, content: dict[str, Any], filepath: Path) -> str:
        """Generate a simple text-based PDF as fallback.

        If reportlab is not available, creates a basic PDF with text content only.

        Args:
            content (dict[str, Any]): Daily learning content.
            filepath (Path): Path where PDF should be saved.

        Returns:
            str: Path to the generated PDF file.

        Errors:
            RuntimeError: If text PDF generation fails.
        """
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.pdfgen import canvas
        except ImportError:
            # Fallback to HTML format
            return self._generate_html_fallback(content, filepath)

        try:
            c = canvas.Canvas(str(filepath), pagesize=letter)
            width, height = letter
            y = height - 50

            # Title
            c.setFont("Helvetica-Bold", 14)
            c.drawString(50, y, "CommuCraft Daily Learning")
            y -= 20

            # Date and role
            c.setFont("Helvetica", 10)
            date_str = content.get("date", "N/A")
            role = content.get("role", "N/A")
            level = content.get("proficiency_level", "N/A")
            c.drawString(50, y, f"Date: {date_str} | Role: {role} | Level: {level}")
            y -= 20

            # Intro message
            intro = content.get("intro_message", "")
            if intro:
                c.setFont("Helvetica-Bold", 11)
                c.drawString(50, y, "Today's Focus:")
                y -= 15
                c.setFont("Helvetica", 10)
                c.drawString(50, y, intro)
                y -= 20

            # Main paragraph
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y, "Learning Content:")
            y -= 15
            c.setFont("Helvetica", 10)
            paragraph_text = content.get("paragraph", "")
            for line in self._wrap_text(paragraph_text, 80):
                if y < 50:
                    c.showPage()
                    y = height - 50
                c.drawString(50, y, line)
                y -= 12

            # Vocabulary
            y -= 10
            c.setFont("Helvetica-Bold", 11)
            c.drawString(50, y, "Vocabulary:")
            y -= 15

            c.setFont("Helvetica", 9)
            for word_obj in content.get("vocabulary", []):
                if isinstance(word_obj, dict):
                    word = word_obj.get("word", "")
                    meaning = word_obj.get("meaning", "")
                    if y < 50:
                        c.showPage()
                        y = height - 50
                    c.drawString(50, y, f"• {word}: {meaning[:50]}...")
                    y -= 10

            # Save
            c.save()
            logger.info(f"✓ Text-based PDF generated: {filepath}")
            return str(filepath)

        except Exception as e:
            logger.error(f"Text PDF generation failed: {str(e)}")
            return self._generate_html_fallback(content, filepath)

    def _generate_html_fallback(self, content: dict[str, Any], filepath: Path) -> str:
        """Generate HTML file as final fallback when PDF generation fails.

        Args:
            content (dict[str, Any]): Daily learning content.
            filepath (Path): Path where file should be saved (will use .html extension).

        Returns:
            str: Path to the generated HTML file.

        Errors:
            RuntimeError: If HTML generation fails.
        """
        try:
            html_filepath = filepath.with_suffix(".html")

            date_str = content.get("date", datetime.now().strftime("%Y-%m-%d"))
            role = content.get("role", "N/A")
            level = content.get("proficiency_level", "N/A")
            intro = content.get("intro_message", "")
            paragraph = content.get("paragraph", "")

            html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>CommuCraft Daily Learning - {date_str}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        h1 {{ color: #1F4788; text-align: center; }}
        .info {{ background: #f0f0f0; padding: 10px; border-radius: 5px; margin: 10px 0; }}
        .section {{ margin: 20px 0; }}
        .section h2 {{ color: #2E5090; border-bottom: 2px solid #2E5090; padding-bottom: 5px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #2E5090; color: white; }}
        .timestamp {{ font-style: italic; color: #666; margin-top: 20px; }}
    </style>
</head>
<body>
    <h1>CommuCraft Daily Learning</h1>
    <div class="info">
        <strong>Date:</strong> {date_str} | <strong>Role:</strong> {role} | <strong>Level:</strong> {level}
    </div>

    <div class="section">
        <h2>Today's Focus</h2>
        <p>{intro}</p>
    </div>

    <div class="section">
        <h2>Learning Content</h2>
        <p>{paragraph}</p>
    </div>

    <div class="section">
        <h2>Vocabulary</h2>
        <table>
            <thead>
                <tr>
                    <th>Word</th>
                    <th>Meaning</th>
                    <th>Example</th>
                    <th>Pronunciation</th>
                </tr>
            </thead>
            <tbody>
"""
            for word_obj in content.get("vocabulary", []):
                if isinstance(word_obj, dict):
                    word = word_obj.get("word", "")
                    meaning = word_obj.get("meaning", "")
                    example = word_obj.get("usage_example", "")
                    phonetic = word_obj.get("phonetic", "") or word_obj.get("pronunciation", "")
                    html_content += f"""                <tr>
                    <td><strong>{word}</strong></td>
                    <td>{meaning}</td>
                    <td>{example}</td>
                    <td>{phonetic}</td>
                </tr>
"""

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            html_content += f"""            </tbody>
        </table>
    </div>

    <div class="timestamp">
        Generated: {timestamp}
    </div>
</body>
</html>"""

            html_filepath.write_text(html_content)
            logger.info(f"✓ HTML fallback generated: {html_filepath}")
            return str(html_filepath)

        except Exception as e:
            logger.error(f"HTML fallback generation failed: {str(e)}")
            raise RuntimeError(f"All PDF/HTML generation methods failed: {str(e)}") from e

    @staticmethod
    def _wrap_text(text: str, width: int) -> list[str]:
        """Wrap text to specified width.

        Args:
            text (str): Text to wrap.
            width (int): Maximum width in characters.

        Returns:
            list[str]: List of wrapped text lines.
        """
        lines = []
        for line in text.split("\n"):
            while len(line) > width:
                lines.append(line[:width])
                line = line[width:]
            lines.append(line)
        return lines
