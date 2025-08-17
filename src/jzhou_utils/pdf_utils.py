import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path, page_range=None, page_separator: str = ""):
    """
    Extract text from a PDF file using PyMuPDF.
    
    Args:
        pdf_path (str): Path to the PDF file
        page_range (tuple, optional): Tuple of (start_page, end_page) to extract specific pages.
                                    If None, extracts all pages. Pages are 0-indexed.
        page_sepeartor: "\n\n--- Page Break ---\n\n"
    Returns:
        str: Extracted text from the PDF
    
    Raises:
        FileNotFoundError: If the PDF file doesn't exist
        Exception: For other PDF processing errors
    """
    try:
        # Open the PDF document
        doc = fitz.open(pdf_path)
        
        # Determine page range
        if page_range is None:
            start_page, end_page = 0, len(doc)
        else:
            start_page, end_page = page_range
            # Ensure page range is valid
            start_page = max(0, start_page)
            end_page = min(len(doc), end_page)
        
        extracted_text = []
        
        # Extract text from each page
        for page_num in range(start_page, end_page):
            page = doc.load_page(page_num)
            text = page.get_text()
            extracted_text.append(text)
        
        # Close the document
        doc.close()
        
        # Join all text with page separators
        return page_separator.join(extracted_text)
        
    except FileNotFoundError:
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    except Exception as e:
        raise Exception(f"Error processing PDF: {str(e)}")


def clean_line(line):
    """
        to-do: make this into a function which just cleans pdf text, adding:

        # to deal with continuations of words
        text = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", text)
        
    """
    # deal with whitespace around hyphens
    temp_line = re.sub(r"\s*[-]\s*", "-", line)
    STR_REPLACE_DICT = {
      "’"  : "'",
      'ﬂ': 'fl',
      'ﬁ': 'fi',
      'ﬃ': 'ffi',
      'Ɵ': 'ti',
      '1ì': 'li',
      '1ï': 'li',
      'ﬀ': 'ff',
      'ƞ': 'tf',
      'Batle': 'Battle',
      'Kiten': 'Kitten',
      'Guter': 'Gutter',
      'Heliod, Sun Crowned': 'Heliod, Sun-Crowned' 
    }
    
    for key, value in STR_REPLACE_DICT.items():    
        temp_line = temp_line.replace(key, value)

    # deal with training whitespaces
    temp_line = temp_line.strip()
    return temp_line