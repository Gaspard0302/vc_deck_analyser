import pymupdf
from typing import TypedDict, List, Dict, Any

def extract_info_from_pdf(pdf_path: str) -> tuple[dict, str]:
    """Extract text and coordinate information from a PDF file
    Args:
        pdf_path: str
    Returns:
        tuple: A tuple containing a dictionary of page information and the whole text of the PDF
        page_dict: dict
        whole_text: str
        
        
        
        {0: {'page_number': 0,
      'text': 'Final Jury Pitch\n'
              'Revolutionizing Solar Installation process \n'
              'November 2024\n'
              'solea.framer.website\n',
      'text_with_coordinates': [{'coordinates': {'x0': 351.32977294921875,
                                                 'x1': 1088.645751953125,
                                                 'y0': 421.3800048828125,
                                                 'y1': 519.6243896484375},
                                'text': 'Final Jury Pitch\n' 'Revolutionizing Solar 'Installation process \n'},
                                {'coordinates': {'x0': 81.0,
                                                 'x1': 1358.9830322265625,
                                                 'y0': 703.273193359375,
                                                 'y1': 730.6151733398438},
                                 'text': 'November 2024\n'
                                         'solea.framer.website\n'}]}}
    """
    

# def extract_info_from_pdf(pdf_url: str):
    # pdf_document = pymupdf.open(pdf_url)
    pdf_document = pymupdf.open(pdf_path)
    
    page_dict = {}
    
    # Only process certain pages
    certain_page = True
    if certain_page:
        page_number = 1
        first_page = pdf_document[page_number]
        page_dict = [extract_page_content(first_page)]
        whole_text = page_dict[0]['text']
        
    else:
        for page_number, page in enumerate(pdf_document):
            page_dict.append(extract_page_content(page))
        whole_text = "".join([page_dict[page_number]['text'] for page_number in page_dict])
        
    return page_dict, whole_text


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
