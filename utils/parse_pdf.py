import pymupdf
from typing import TypedDict, List, Dict, Any

def extract_info_from_pdf(pdf_path: str) -> tuple[list, str]:
    """Extract text and coordinate information from a PDF file
    Args:
        pdf_path: str
    Returns:
        tuple: A tuple containing a list of page information and the whole text of the PDF
        page_list: list
        whole_text: str
    """

    # pdf_document = pymupdf.open(pdf_url)
    pdf_document = pymupdf.open(pdf_path)

    page_list = []

    # Only process certain pages
    certain_page = False
    if certain_page:
        page_number = 1
        first_page = pdf_document[page_number]
        page_list = [extract_page_content(first_page)]
        whole_text = page_list[0]['text']

    else:
        for page_number, page in enumerate(pdf_document):
            page_list.append(extract_page_content(page))
        whole_text = "".join([page['text'] for page in page_list])

    return page_list, whole_text


def extract_page_content(page) -> dict:
    """Extract text and coordinate information from a single PDF page with normalized coordinates. Normalized coordinates are in the range of 0-900 for x and 0-1600 for y.
    Args:
        page: pymupdf.Page
    Returns:
        dict: A dictionary containing the text and coordinate information for the page with normalized coordinates

    """
    # Get page dimensions
    page_rect = page.rect
    page_width = page_rect.width
    page_height = page_rect.height
    print("##########")
    print(page_width, page_height)
    print("##########")

    text_blocks = page.get_text("blocks")
    text_with_coords = []

    for block in text_blocks:
        # block format: (x0, y0, x1, y1, text, block_no, block_type)
        # Normalize coordinates to 0-1 range
        text_with_coords.append({
            'text': block[4],
            'coordinates': {
                'x0': block[0] / page_width * 900,
                'y0': block[1] / page_height * 1600,
                'x1': block[2] / page_width * 900,
                'y1': block[3] / page_height * 1600
            }
        })

    return {
        'text': page.get_text(),
        'text_with_coordinates': text_with_coords,
        'page_number': page.number,
    }

if __name__ == "__main__":
    import pprint
    pprint.pprint(extract_info_from_pdf("test_pitch_solea.pdf"))
