from anthropic import Anthropic
import base64
import pymupdf

try:
    from utils.config import ANTHROPIC_API_KEY
except ImportError:
    from config import ANTHROPIC_API_KEY

client = Anthropic(api_key=ANTHROPIC_API_KEY)

def generate_text(prompt):
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=4000,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.content[0].text

def query_pdf_page(pdf_page_number: int, prompt: str, pdf_path: str):
    """Query Claude with a specific page from a PDF document
    Args:
        pdf_page_number: int
        prompt: str
        pdf_path: str
    Returns:
        str: The response from Claude
    """
    # Open the PDF and get the specific page
    pdf_document = pymupdf.open(pdf_path)
    page = pdf_document[pdf_page_number]
    
    # Start with lower DPI to avoid 5MB limit
    dpi = 100
    max_size_bytes = 5 * 1024 * 1024  # 5MB limit
    
    while dpi >= 50:  # Don't go below 50 DPI for readability
        # Convert the page to an image (pixmap)
        pixmap = page.get_pixmap(dpi=dpi)
        
        # Convert to JPEG for better compression (instead of PNG)
        image_data = pixmap.tobytes("jpeg", jpg_quality=85)
        
        # Check if image is under 5MB limit
        if len(image_data) <= max_size_bytes:
            break
            
        # Reduce DPI and try again
        dpi -= 10
        pixmap = None  # Free memory
    
    if dpi < 50:
        # Fallback: use very low DPI if still too large
        pixmap = page.get_pixmap(dpi=50)
        image_data = pixmap.tobytes("jpeg", jpg_quality=70)
    
    # Encode as base64
    image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    # Close the PDF document
    pdf_document.close()
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_base64
                    }
                }
            ]
        }]
    )
    return response.content[0].text


def query_image(prompt: str, image_path: str):
    """Query Claude with a regular image file (PNG, JPEG, etc.)"""
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        image_base64 = base64.b64encode(image_data).decode('utf-8')
    
    # Determine media type based on file extension
    if image_path.lower().endswith('.png'):
        media_type = "image/png"
    elif image_path.lower().endswith(('.jpg', '.jpeg')):
        media_type = "image/jpeg"
    elif image_path.lower().endswith('.gif'):
        media_type = "image/gif"
    elif image_path.lower().endswith('.webp'):
        media_type = "image/webp"
    else:
        media_type = "image/png"  # Default fallback
    
    response = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=4000,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image", 
                    "source": {
                        "type": "base64",
                        "media_type": media_type,
                        "data": image_base64
                    }
                }
            ]
        }]
    )
    return response.content[0].text


if __name__ == "__main__":
    print(query_pdf_page(1, "What is the main idea of the pitch?", "test_pitch_solea.pdf"))
#     print(generate_text("test"))