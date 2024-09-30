import re, os
from io import StringIO
from typing import Iterator

from docx import Document as DocxDocument
from pdfminer.high_level import extract_pages as extract_pdf_pages
from pdfminer.layout import LTTextContainer as PdfLTTextContainer, LTPage as PdfLTPage, LAParams as PdfLAParams

__all__ = "parse_pdf", "parse_pdf_to_file", "parse_docx", "parse_docx_to_file", "parse_directory", "parse_directory_to_files", "parse_txt"


def parse_pdf(path: str) -> str:

    pages: Iterator[PdfLTPage] = extract_pdf_pages(
        pdf_file = path,
        laparams = PdfLAParams(
            char_margin = 10.0,
            boxes_flow = None
        )
    )

    output = StringIO()

    for page in pages:
        for element in page:
            if isinstance(element, PdfLTTextContainer):
                output.write(re.sub(r"  +", " ", f"{element.get_text().strip()}\n"))

    return re.sub(r"\n\s+", "\n\n", output.getvalue())

def parse_docx(path: str) -> str:
    document = DocxDocument(path)

    output = StringIO()

    for paragraph in document.paragraphs:
        output.write(paragraph.text)

    return output.getvalue()

def parse_pdf_to_file(pdf_path: str, output_path: str, encoding: str = "utf-8") -> None:
    with open(output_path, "w+", encoding = encoding) as file:
        file.write(parse_pdf(pdf_path))

def parse_docx_to_file(docx_path: str, output_path: str, encoding: str = "utf-8") -> None:
    with open(output_path, "w+", encoding = encoding) as file:
        file.write(parse_docx(docx_path))

def parse_txt(path: str) -> str:
    with open(path, "r", encoding = "utf-8") as file:
        return file.read()

def parse_directory(directory_path: str) -> dict[str, str]:
    result: dict[str, str] = {}

    for root, _, files in os.walk(directory_path):
        for file in files:
            file_extension: str = file.split(".")[-1].lower()
            full_path: str = os.path.join(root, file)
            print(f"Parsing: {full_path}")
            if file_extension == "txt":
                result[full_path] = parse_txt(full_path)
            elif file_extension == "docx":
                result[full_path] = parse_docx(full_path)
            elif file_extension == "pdf":
                result[full_path] = parse_pdf(full_path)

    return result

def parse_directory_to_files(input_directory: str, output_directory: str, encoding: str = "utf-8") -> None:
    for file_path, text in parse_directory(input_directory).items():
        with open(os.path.join(output_directory, f"{file_path.split("\\")[-1]}.txt"), "w+", encoding = encoding) as file:
            file.write(text)