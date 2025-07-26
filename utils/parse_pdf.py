import pymupdf

def extract_info_from_pdf(pdf_url: str):
    pdf_document = pymupdf.open(pdf_url)
    result = {}
    for page_number, page in enumerate(pdf_document):
        result[page_number] = extract_page_content(page)
    return result


def extract_page_content(page):
    """Extract text and text box coordinates from a single PDF page"""
    return {
        'text': page.get_text(),
        'coordinates': page.get_textbox_coordinates(),
        'coordinates_text': page.get_text_with_coordinates(),
        'page_number': page.page_number,
        
    }

