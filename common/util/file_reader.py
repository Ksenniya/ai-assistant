import io
import os
import json
import csv
import fitz
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup


def read_file_content(file):
    """
    Reads the contents of an uploaded file based on its extension and returns the content.
    Supports .txt, .json, .csv, .pdf, .drawio, .xml, .html, .java, .kt, .py extensions.

    :param file: A file-like object (e.g. from Quart's request.files) with a .filename attribute.
    :return: The file's contents in an appropriate format.
    """
    ext = os.path.splitext(file.filename)[1].lower()

    # Ensure the file pointer is at the beginning
    file.seek(0)

    if ext == '.txt':
        # Read bytes and decode to a string
        content = file.read()
        return content.decode('utf-8') if isinstance(content, bytes) else content

    elif ext == '.json':
        # Read and decode before parsing JSON
        file.seek(0)
        content = file.read().decode('utf-8')
        return json.loads(content)

    elif ext == '.csv':
        # Read as text then use io.StringIO for csv.reader
        file.seek(0)
        content = file.read().decode('utf-8')
        file_like = io.StringIO(content)
        reader = csv.reader(file_like)
        return "\n".join([", ".join(row) for row in reader])

    elif ext == '.pdf':
        file.seek(0)
        return read_pdf(file)  # Ensure read_pdf handles file-like objects

    elif ext == '.drawio':
        file.seek(0)
        return read_drawio(file)

    elif ext == '.xml':
        file.seek(0)
        return read_xml(file)

    elif ext == '.html':
        file.seek(0)
        return read_html(file)

    elif ext in {'.java', '.kt', '.py'}:
        file.seek(0)
        return read_code_file(file)

    else:
        raise ValueError(f"Unsupported file extension: {ext}")

def read_file_content_by_file_path(file_path):
    """
    Reads the contents of a file based on its extension and returns the content.
    Supports .txt, .json, .csv, .pdf, .drawio, .xml, .html, .java, .kt, .py extensions.
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext == '.txt':
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    elif ext == '.json':
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)  # Assumes file content is a JSON array

    elif ext == '.csv':
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            return "\n".join([", ".join(row) for row in reader])  # Flatten CSV rows into a single string

    elif ext == '.pdf':
        return read_pdf(file_path)

    elif ext == '.drawio':
        return read_drawio(file_path)

    elif ext == '.xml':
        return read_xml(file_path)

    elif ext == '.html':
        return read_html(file_path)

    else:
        try:
            return read_code_file(file_path)
        except Exception as e:
            raise ValueError("Unsupported file extension")


def read_pdf(file_path):
    """
    Extracts text from a PDF file using PyMuPDF (fitz).
    """
    document = fitz.open(file_path)
    pdf_text = ""
    for page_num in range(document.page_count):
        page = document.load_page(page_num)
        pdf_text += page.get_text("text")  # Extract text as plain text
    return pdf_text


def read_drawio(file_path):
    """
    Extracts relevant text from a Draw.io (XML) file.
    This function extracts the XML structure, focusing on shapes' labels.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        xml_content = file.read()

    # Parse the XML content
    root = ET.fromstring(xml_content)

    # Assuming we are interested in extracting the text from the XML 'mxCell' elements
    drawio_text = ""
    for cell in root.iter('mxCell'):
        # Each 'mxCell' may contain a 'value' attribute that holds the text of the diagram element
        value = cell.get('value')
        if value:
            drawio_text += value + "\n"

    return drawio_text


def read_xml(file_path):
    """
    Reads and extracts text from an XML file.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        xml_content = file.read()

    # Parse the XML content
    root = ET.fromstring(xml_content)

    # Extract all text from the XML tree (this is just an example, you may want to refine this based on your XML structure)
    xml_text = "\n".join([elem.text for elem in root.iter() if elem.text])  # Collecting text from all elements
    return xml_text


def read_html(file_path):
    """
    Extracts text from an HTML file using BeautifulSoup.
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()

    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Extract and return all text from the HTML page
    html_text = soup.get_text()
    return html_text


def read_code_file(file_path):
    """
    Reads content of code files like .java, .kt, .py (Plain text).
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        code_content = file.read()

    return code_content
