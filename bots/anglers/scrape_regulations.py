#!/usr/bin/env python3
"""
bots/anglers/scrape_regulations.py
Scrape Alberta fishing regulations from albertaregulations.ca
and save to knowledge_base/ directory.

Usage:
    cd /opt/telebots
    source venv/bin/activate
    python3 bots/anglers/scrape_regulations.py
"""
import time
import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import pdfplumber

# Add telebots to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from bots.anglers.config import Config

# Target directory for scraped content
KB_DIR = Config.KNOWLEDGE_BASE_DIR

# HTML pages to scrape
HTML_PAGES = [
    ("https://albertaregulations.ca/fishingregs/es1.html", "regulations_es1.txt"),
    ("https://albertaregulations.ca/fishingregs/es2.html", "regulations_es2.txt"),
    ("https://albertaregulations.ca/fishingregs/pp1.html", "regulations_pp1.txt"),
    ("https://albertaregulations.ca/fishingregs/pp2.html", "regulations_pp2.txt"),
    ("https://albertaregulations.ca/fishingregs/nb1.html", "regulations_nb1.txt"),
    ("https://albertaregulations.ca/fishingregs/nb2.html", "regulations_nb2.txt"),
    ("https://albertaregulations.ca/fishingregs/general-regs.html", "regulations_general.txt"),
    ("https://albertaregulations.ca/fishingregs/definitions.html", "regulations_definitions.txt"),
    ("https://albertaregulations.ca/fishingregs/fish-stocking.html", "regulations_stocking.txt"),
]

# PDF files to scrape
PDF_FILES = [
    ("https://albertaregulations.ca/fishingregs/ES1-Lakes.pdf", "waterbodies_es1_lakes.txt"),
    ("https://albertaregulations.ca/fishingregs/ES1-Rivers.pdf", "waterbodies_es1_rivers.txt"),
    ("https://albertaregulations.ca/fishingregs/PP1-Lakes.pdf", "waterbodies_pp1_lakes.txt"),
    ("https://albertaregulations.ca/fishingregs/PP1-Rivers.pdf", "waterbodies_pp1_rivers.txt"),
]


def extract_main_content(html: str) -> str:
    """
    Extract main content from HTML, stripping navigation, headers, and footers.
    Preserve structure including headings, lists, and tables.
    """
    soup = BeautifulSoup(html, 'html.parser')

    # Remove common navigation and footer elements
    for element in soup.find_all(['nav', 'header', 'footer', 'script', 'style']):
        element.decompose()

    # Remove elements with common nav/footer classes
    for class_name in ['navigation', 'nav', 'menu', 'footer', 'sidebar', 'header-top']:
        for element in soup.find_all(class_=class_name):
            element.decompose()

    # Try to find main content container
    main_content = None

    # Common content container selectors
    for selector in ['main', 'article', '.content', '#content', '.main-content', '#main']:
        main_content = soup.select_one(selector)
        if main_content:
            break

    # If no specific container found, use body
    if not main_content:
        main_content = soup.find('body')

    if not main_content:
        # Fallback: return all text
        return soup.get_text(separator='\n', strip=True)

    # Extract text while preserving structure
    lines = []
    for element in main_content.descendants:
        if element.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            # Add headings with extra spacing
            text = element.get_text(strip=True)
            if text:
                lines.append(f"\n{'=' * len(text)}")
                lines.append(text.upper())
                lines.append('=' * len(text))
        elif element.name == 'p':
            text = element.get_text(strip=True)
            if text:
                lines.append(f"\n{text}")
        elif element.name == 'li':
            text = element.get_text(strip=True)
            if text:
                lines.append(f"  • {text}")
        elif element.name == 'tr':
            # Extract table rows
            cells = element.find_all(['td', 'th'])
            if cells:
                row_text = ' | '.join(cell.get_text(strip=True) for cell in cells)
                if row_text.strip():
                    lines.append(f"  {row_text}")

    # Clean up multiple blank lines
    text = '\n'.join(lines)
    while '\n\n\n' in text:
        text = text.replace('\n\n\n', '\n\n')

    return text.strip()


def scrape_html_page(url: str, output_filename: str) -> bool:
    """Fetch and scrape an HTML page, save to knowledge base."""
    try:
        print(f"  Fetching {url}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        print(f"  Extracting content...")
        content = extract_main_content(response.text)

        output_path = KB_DIR / output_filename
        output_path.write_text(content, encoding='utf-8')

        print(f"  ✓ Saved to {output_filename} ({len(content)} chars)")
        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def scrape_pdf_file(url: str, output_filename: str) -> bool:
    """Fetch and extract text from PDF, save to knowledge base."""
    try:
        print(f"  Fetching {url}...")
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        # Save PDF temporarily
        temp_pdf = KB_DIR / "_temp.pdf"
        temp_pdf.write_bytes(response.content)

        print(f"  Extracting PDF tables and text...")
        lines = []

        with pdfplumber.open(temp_pdf) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                # Try to extract tables first
                tables = page.extract_tables()
                if tables:
                    for table in tables:
                        for row in table:
                            if row and any(cell for cell in row if cell):
                                # Clean and join cells
                                cells = [str(cell).strip() if cell else '' for cell in row]
                                lines.append(' | '.join(cells))
                        lines.append('')  # Blank line between tables

                # Also extract regular text
                text = page.extract_text()
                if text:
                    lines.append(text)
                    lines.append('')

        # Clean up temp file
        temp_pdf.unlink()

        content = '\n'.join(lines).strip()
        output_path = KB_DIR / output_filename
        output_path.write_text(content, encoding='utf-8')

        print(f"  ✓ Saved to {output_filename} ({len(content)} chars)")
        return True

    except Exception as e:
        print(f"  ✗ Error: {e}")
        # Clean up temp file if it exists
        temp_pdf = KB_DIR / "_temp.pdf"
        if temp_pdf.exists():
            temp_pdf.unlink()
        return False


def main():
    print(f"Alberta Fishing Regulations Scraper")
    print(f"Output directory: {KB_DIR}")
    print("=" * 60)

    # Ensure knowledge base directory exists
    KB_DIR.mkdir(parents=True, exist_ok=True)

    # Scrape HTML pages
    print(f"\n📄 Scraping HTML pages ({len(HTML_PAGES)} total)...")
    html_success = 0
    for i, (url, filename) in enumerate(HTML_PAGES, 1):
        print(f"\n[{i}/{len(HTML_PAGES)}] {filename}")
        if scrape_html_page(url, filename):
            html_success += 1
        time.sleep(1)  # Be polite to the server

    # Scrape PDF files
    print(f"\n\n📊 Scraping PDF files ({len(PDF_FILES)} total)...")
    pdf_success = 0
    for i, (url, filename) in enumerate(PDF_FILES, 1):
        print(f"\n[{i}/{len(PDF_FILES)}] {filename}")
        if scrape_pdf_file(url, filename):
            pdf_success += 1
        time.sleep(1)  # Be polite to the server

    # Summary
    print("\n" + "=" * 60)
    print(f"✓ Complete!")
    print(f"  HTML pages: {html_success}/{len(HTML_PAGES)} successful")
    print(f"  PDF files: {pdf_success}/{len(PDF_FILES)} successful")
    print(f"  Total: {html_success + pdf_success}/{len(HTML_PAGES) + len(PDF_FILES)} files")
    print(f"\nNext step: Run load_kb.py to update the knowledge base.")


if __name__ == "__main__":
    main()
