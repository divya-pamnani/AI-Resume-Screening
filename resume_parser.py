"""
resume_parser.py
-------------------------------
Resume Parsing Utilities
Supports PDF, DOCX and TXT files
"""

import os
import re
import pdfplumber
import docx


# ----------------------------------------
# Extract text from PDF
# ----------------------------------------

def extract_pdf_text(file_path):
    """
    Extract text from PDF file.
    """

    text = ""

    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    return text


# ----------------------------------------
# Extract text from DOCX
# ----------------------------------------

def extract_docx_text(file_path):
    """
    Extract text from DOCX file.
    """

    document = docx.Document(file_path)

    text = ""

    for para in document.paragraphs:
        text += para.text + "\n"

    return text


# ----------------------------------------
# Extract text from TXT
# ----------------------------------------

def extract_txt_text(file_path):
    """
    Extract text from TXT file.
    """

    with open(
        file_path,
        "r",
        encoding="utf-8",
        errors="ignore"
    ) as f:

        return f.read()


# ----------------------------------------
# Main Text Extractor
# ----------------------------------------

def extract_text(file_path):
    """
    Automatically detect file type.
    """

    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":
        return extract_pdf_text(file_path)

    elif extension == ".docx":
        return extract_docx_text(file_path)

    elif extension == ".txt":
        return extract_txt_text(file_path)

    else:
        raise ValueError(
            f"Unsupported file type : {extension}"
        )


# ----------------------------------------
# Clean Text
# ----------------------------------------

def clean_text(text):
    """
    Remove unwanted spaces.
    """

    text = re.sub(r"\s+", " ", text)

    return text.strip()
# ----------------------------------------
# Extract Email
# ----------------------------------------

def extract_email(text):
    """
    Extract email address from resume text.
    """

    pattern = r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"

    match = re.search(pattern, text)

    if match:
        return match.group(0)

    return ""


# ----------------------------------------
# Extract Phone Number
# ----------------------------------------

def extract_phone(text):
    """
    Extract Indian phone number.
    """

    pattern = r"(?:\+91[- ]?)?[6-9]\d{9}"

    match = re.search(pattern, text)

    if match:
        return match.group(0)

    return ""


# ----------------------------------------
# Extract Candidate Name
# ----------------------------------------

def extract_name(text):
    """
    Simple heuristic to extract candidate name.
    """

    lines = text.split("\n")

    for line in lines[:10]:

        line = line.strip()

        if len(line) == 0:
            continue

        if len(line.split()) < 2:
            continue

        if len(line.split()) > 4:
            continue

        # Skip lines containing numbers
        if any(ch.isdigit() for ch in line):
            continue

        # Skip common headings
        skip = [
            "resume",
            "curriculum",
            "vitae",
            "email",
            "phone",
            "mobile",
            "contact",
            "address",
            "career",
            "objective",
            "summary"
        ]

        if any(word in line.lower() for word in skip):
            continue

        return line.title()

    return "Unknown"


# ----------------------------------------
# Basic Information
# ----------------------------------------

def extract_basic_info(text):
    """
    Returns basic resume information.
    """

    return {
        "Name": extract_name(text),
        "Email": extract_email(text),
        "Phone": extract_phone(text)
    }