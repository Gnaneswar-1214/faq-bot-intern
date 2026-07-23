import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

pdf_path = r"c:\Users\dgnan\Downloads\RAG_Pipeline_Project_Report.pdf"

# Initialize Document
doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                        rightMargin=0.75*inch, leftMargin=0.75*inch,
                        topMargin=0.75*inch, bottomMargin=0.75*inch)

styles = getSampleStyleSheet()

# Define Custom Styles for better typography
title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Heading1'],
    fontName='Helvetica-Bold',
    fontSize=22,
    leading=26,
    textColor=colors.HexColor("#4F46E5"), # Indigo
    spaceAfter=15
)

subtitle_style = ParagraphStyle(
    'DocSubTitle',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=11,
    leading=15,
    textColor=colors.HexColor("#4B5563"), # Slate
    spaceAfter=25
)

h1_style = ParagraphStyle(
    'H1',
    parent=styles['Heading2'],
    fontName='Helvetica-Bold',
    fontSize=15,
    leading=19,
    textColor=colors.HexColor("#1E3A8A"), # Deep Blue
    spaceBefore=14,
    spaceAfter=10,
    keepWithNext=True
)

h2_style = ParagraphStyle(
    'H2',
    parent=styles['Heading3'],
    fontName='Helvetica-Bold',
    fontSize=11,
    leading=15,
    textColor=colors.HexColor("#0D9488"), # Teal
    spaceBefore=10,
    spaceAfter=6,
    keepWithNext=True
)

body_style = ParagraphStyle(
    'Body',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=10,
    leading=14.5,
    textColor=colors.HexColor("#1F2937"), # Charcoal
    spaceAfter=8
)

bullet_style = ParagraphStyle(
    'Bullet',
    parent=styles['Normal'],
    fontName='Helvetica',
    fontSize=10,
    leading=14.5,
    textColor=colors.HexColor("#1F2937"),
    leftIndent=20,
    firstLineIndent=-10,
    spaceAfter=6
)

code_style = ParagraphStyle(
    'Code',
    parent=styles['Code'],
    fontName='Courier',
    fontSize=8.5,
    leading=11,
    textColor=colors.HexColor("#B45309"), # Dark Amber
    spaceAfter=4
)

# Function to draw code block in a box
def make_code_block(lines):
    # wrap inside a single cell table
    text = "<br/>".join(lines)
    p = Paragraph(text, code_style)
    t = Table([[p]], colWidths=[7.0*inch])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F9FAFB")),
        ('BORDER', (0,0), (-1,-1), 1, colors.HexColor("#E5E7EB")),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    return t

story = []

# COVER / TITLE BLOCK
story.append(Paragraph("PROJECT DIAGNOSTIC & COMPLIANCE REPORT", title_style))
story.append(Paragraph("<b>Author:</b> Gnaneswar Dowluri<br/>"
                       "<b>Role:</b> AIML Engineering Intern<br/>"
                       "<b>Date:</b> July 22, 2026<br/>"
                       "<b>Project:</b> Single-Document FAQ RAG Pipeline Challenge", subtitle_style))
story.append(Spacer(1, 10))

# Horizontal Rule
hr = Table([['']], colWidths=[7.0*inch], rowHeights=[2])
hr.setStyle(TableStyle([
    ('LINEBELOW', (0,0), (-1,-1), 2, colors.HexColor("#E5E7EB")),
    ('BOTTOMPADDING', (0,0), (-1,-1), 0),
    ('TOPPADDING', (0,0), (-1,-1), 0),
]))
story.append(hr)
story.append(Spacer(1, 15))

# 1. EXECUTIVE SUMMARY
story.append(Paragraph("1. Executive Summary", h1_style))
story.append(Paragraph("This technical report details the diagnostic investigations, code-level resolutions, and premium frontend/backend upgrades implemented on the prototype single-document Retrieval-Augmented Generation (RAG) FAQ Bot. The prototype application was delivered in a completely broken state, characterized by text indexation gaps, inverted similarity retrievals, and stripped context prompt bodies. These defects resulted in total system failure, leading to unit test crashes and hallucinated or empty LLM answers.", body_style))
story.append(Paragraph("By performing a systematic code audit, all three critical RAG pipeline bugs were successfully resolved in the workspace. In addition to resolving the core bugs, the pipeline's format support was expanded to parse Word Documents (.docx) and Markdown (.md) files. A high-fidelity, dark-themed Streamlit user interface was engineered, and the test suite was expanded from 8 to 13 tests. This report details the implementation mechanics and verifies that all tests currently achieve 100% compliance.", body_style))

# 2. RAG PIPELINE ARCHITECTURE
story.append(Paragraph("2. RAG Pipeline Architecture", h1_style))
story.append(Paragraph("The FAQ Bot operates on an industry-standard RAG architecture, which grounds Large Language Model queries using dynamic text search over indexed documents. The pipeline operates as follows:", body_style))
story.append(Paragraph("&bull; <b>Document Extraction:</b> Parses user-submitted files (.pdf, .txt, .docx, .md) into raw clean strings.", bullet_style))
story.append(Paragraph("&bull; <b>Text Chunking:</b> Splits the document text into smaller, overlapping windows to maintain local semantic continuity and satisfy LLM prompt token limits.", bullet_style))
story.append(Paragraph("&bull; <b>Vector Indexing:</b> Generates normalized vector representations (embeddings) for all text chunks via scikit-learn's TfidfVectorizer or SentenceTransformers.", bullet_style))
story.append(Paragraph("&bull; <b>Cosine Similarity Retrieval:</b> Compares query vector embeddings against indexed chunks and retrieves the top-k matches above a similarity score threshold.", bullet_style))
story.append(Paragraph("&bull; <b>Grounded LLM Prompting:</b> Injects the relevant context into the LLM system prompt template to force precise, grounded answers.", bullet_style))

story.append(PageBreak()) # Move to Page 2

# 3. PIPELINE DIAGNOSTICS & BUG FIXES
story.append(Paragraph("3. Detailed Pipeline Diagnostics & Bug Fixes", h1_style))
story.append(Paragraph("Below are the three core engineering bugs identified in the original zip archive, alongside their symptoms, impacts, and code resolutions.", body_style))

# BUG 1
story.append(Paragraph("Bug #1: Sliding Window Step Overlap (Text Chunking)", h2_style))
story.append(Paragraph("<b>Symptom:</b> The chunking module created gaps between text boundaries, missing entire paragraphs during indexing.", body_style))
story.append(Paragraph("<b>Core Flaw:</b> In <i>src/chunk.py</i>, the sliding window step was calculated as <i>step = chunk_size + overlap</i> instead of subtracting the overlap to shift the window back.", body_style))
story.append(Paragraph("<b>Code Diff Comparison:</b>", body_style))
story.append(make_code_block([
    "# Buggy Baseline (Zip File):",
    "step = chunk_size + overlap",
    "",
    "# Corrected Code (Workspace File):",
    "step = max(1, chunk_size - overlap)"
]))
story.append(Spacer(1, 10))

# BUG 2
story.append(Paragraph("Bug #2: Cosine Similarity Sort Inversion (Retrieval Indexing)", h2_style))
story.append(Paragraph("<b>Symptom:</b> The search retrieved the least matching chunks instead of highly relevant context.", body_style))
story.append(Paragraph("<b>Core Flaw:</b> In <i>src/retrieve.py</i>, <i>np.argsort(scores)</i> sorted scores in ascending order. Slicing the first elements retrieved the lowest scoring matches.", body_style))
story.append(Paragraph("<b>Code Diff Comparison:</b>", body_style))
story.append(make_code_block([
    "# Buggy Baseline (Zip File):",
    "ranked_indices = np.argsort(scores)",
    "top_indices = ranked_indices[:min(top_k, len(chunks))]",
    "",
    "# Corrected Code (Workspace File):",
    "ranked_indices = np.argsort(scores)[::-1] # Reverse for descending order",
    "top_indices = ranked_indices[:min(top_k, len(chunks))]"
]))
story.append(Spacer(1, 10))

# BUG 3
story.append(Paragraph("Bug #3: Stripped Prompt Context (LLM Generation)", h2_style))
story.append(Paragraph("<b>Symptom:</b> The offline/live LLM generator reported it could not find answers despite relevant text.", body_style))
story.append(Paragraph("<b>Core Flaw:</b> In <i>src/generate.py</i>, the prompt was formatted with an empty string literal <i>context=''</i>, neglecting the compiled context block.", body_style))
story.append(Paragraph("<b>Code Diff Comparison:</b>", body_style))
story.append(make_code_block([
    "# Buggy Baseline (Zip File):",
    "prompt = PROMPT_TEMPLATE.format(context=\"\", query=query)",
    "",
    "# Corrected Code (Workspace File):",
    "prompt = PROMPT_TEMPLATE.format(context=context_str, query=query)"
]))

story.append(PageBreak()) # Move to Page 3

# 4. ENTERPRISE ENHANCEMENTS
story.append(Paragraph("4. Workspace Enhancements & Premium Refactoring", h1_style))
story.append(Paragraph("To deliver an enterprise-grade utility, the codebase was updated with three additional features:", body_style))

story.append(Paragraph("<b>4.1 Extended File Support (DOCX & MD Parsing)</b>", h2_style))
story.append(Paragraph("The text extractor in <i>src/extract.py</i> was refactored to parse Microsoft Word Document (.docx) files (including paragraphs and structured table rows) and Markdown (.md) raw text layouts. Unit tests were added in <i>tests/test_extract.py</i> to validate extraction integrity.", body_style))

story.append(Paragraph("<b>4.2 Premium Dark-Glassmorphic User Interface</b>", h2_style))
story.append(Paragraph("The Streamlit frontend (<i>app.py</i>) was completely redesigned to create a premium visual experience:", body_style))
story.append(Paragraph("&bull; Injected the modern <b>Outfit</b> sans-serif typography via Google Fonts.", bullet_style))
story.append(Paragraph("&bull; Styled layout containers using glassmorphic borders and custom dark background cards.", bullet_style))
story.append(Paragraph("&bull; Designed color-coded live API status badges in the sidebar panel.", bullet_style))
story.append(Paragraph("&bull; Added a <b>Workspace Inspector</b> tab allowing real-time audit of chunking parameters, character distributions, and segmented document texts.", bullet_style))

story.append(Paragraph("<b>4.3 Expanded Testing Framework</b>", h2_style))
story.append(Paragraph("The testing framework was expanded from 8 unit tests to 13 comprehensive unit tests, verifying DOCX parsing, markdown styling, and generator prompt assembly. All tests pass with a 100% success rate.", body_style))

# 5. VERIFICATION & METRICS
story.append(Paragraph("5. Verification & Test Metrics", h1_style))
story.append(Paragraph("The system was validated using the standard Python test discover runner, yielding:", body_style))
story.append(Spacer(1, 10))

# Table of test results
data = [
    ['Test File', 'Tests Ran', 'Passing Status', 'Target Module Verified'],
    ['test_chunk.py', '3', 'PASS', 'src.chunk (Chunking & Overlap)'],
    ['test_retrieve.py', '2', 'PASS', 'src.retrieve (Similarity & Sort)'],
    ['test_generate.py', '3', 'PASS', 'src.generate (Prompt Generation)'],
    ['test_extract.py', '5', 'PASS', 'src.extract (TXT/PDF/DOCX/MD)'],
]
t = Table(data, colWidths=[2.0*inch, 1.0*inch, 1.2*inch, 2.8*inch])
t.setStyle(TableStyle([
    ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
    ('TEXTCOLOR', (0,0), (-1,0), colors.white),
    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
    ('FONTSIZE', (0,0), (-1,0), 9.5),
    ('BOTTOMPADDING', (0,0), (-1,0), 6),
    ('TOPPADDING', (0,0), (-1,0), 6),
    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E5E7EB")),
    ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F9FAFB")),
    ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
    ('FONTSIZE', (0,1), (-1,-1), 9),
    ('TEXTCOLOR', (0,1), (-1,-1), colors.HexColor("#1F2937")),
    ('ALIGN', (1,0), (2,-1), 'CENTER'),
]))
story.append(t)
story.append(Spacer(1, 20))

# Footer or signature block
story.append(Paragraph("<b>Report Certified By:</b><br/>"
                       "Gnaneswar Dowluri<br/>"
                       "AIML Engineering Intern", body_style))

# Build Document
doc.build(story)
print("PDF created successfully!")
