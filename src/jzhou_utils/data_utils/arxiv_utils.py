import urllib.request
import xml.etree.ElementTree as ET
import re
import os

# ==========================================
# PASTE YOUR URL(S) AND TARGET FOLDER HERE
# ==========================================
# You can provide a single URL string or a list of URL strings.
ARXIV_URLS = [
    "https://arxiv.org/abs/2512.17372",
]

# Set to "." for the current directory, or specify a path like "./papers"
DOWNLOAD_DIR = "."

def to_title_case(title_str):
    """
    Converts a given string to a title-cased format while ignoring minor words.
    
    Unlike Python's built-in .title() method, this function preserves acronyms 
    (e.g., "RNN" remains "RNN") and leaves common grammatical particles and 
    prepositions lowercase unless they appear as the first word of the title.
    
    Args:
        title_str (str): The raw, unformatted paper title.
        
    Returns:
        str: The properly capitalized title string.
    """
    minor_words = {
        'a', 'an', 'the', 'and', 'but', 'or', 'for', 'nor', 'on', 'at', 
        'to', 'from', 'by', 'in', 'of', 'with', 'as', 'is', 'are'
    }
    words = title_str.split()
    if not words:
        return ""
    
    result = []
    for i, word in enumerate(words):
        bare_word = re.sub(r'[^a-zA-Z]', '', word).lower()
        if i != 0 and bare_word in minor_words:
            result.append(word.lower())
        else:
            result.append(word[0].upper() + word[1:] if word else "")
            
    return ' '.join(result)

def extract_arxiv_id(url):
    """
    Extracts the unique arXiv identifier from a given URL.
    
    This uses regex to find the standard arXiv ID format, meaning it correctly 
    handles both /abs/ and /pdf/ links, as well as versioned identifiers (e.g., v1, v2).
    
    Args:
        url (str): The full arXiv URL.
        
    Returns:
        str | None: The extracted arXiv ID (e.g., "2512.17372"), or None if no 
        valid ID pattern could be matched.
    """
    match = re.search(r'(\d{4}\.\d{4,5}(?:v\d+)?)', url)
    return match.group(1) if match else None

def get_metadata(arxiv_id):
    """
    Queries the official arXiv API to fetch and parse metadata for a specific paper.
    
    Extracts the title (cleaning up internal line breaks), determines the primary 
    author's last name, appends "et al." if there are co-authors, and retrieves 
    the publication year.
    
    Args:
        arxiv_id (str): The unique arXiv identifier to query.
        
    Returns:
        dict | None: A dictionary containing 'title', 'author_str', and 'year', 
        or None if the API request fails or metadata is missing.
    """
    api_url = f'http://export.arxiv.org/api/query?id_list={arxiv_id}'
    
    try:
        with urllib.request.urlopen(api_url) as response:
            xml_data = response.read()
    except Exception as e:
        print(f"❌ Error fetching metadata for {arxiv_id}: {e}")
        return None

    root = ET.fromstring(xml_data)
    ns = {'atom': 'http://www.w3.org/2005/Atom'}
    entry = root.find('atom:entry', ns)

    if entry is None:
        print(f"❌ Error: No metadata found for arXiv ID {arxiv_id}.")
        return None

    # 1. Extract and Format Title
    title_raw = entry.find('atom:title', ns).text
    title_clean = re.sub(r'\s+', ' ', title_raw.strip())
    title = to_title_case(title_clean)

    # 2. Extract Authors and get Last Name
    authors = entry.findall('atom:author/atom:name', ns)
    first_author_full = authors[0].text.strip()
    first_author_last = first_author_full.split()[-1] 
    
    if len(authors) > 1:
        author_str = f"{first_author_last} et al."
    else:
        author_str = first_author_last

    # 3. Extract Published Year
    published = entry.find('atom:published', ns).text
    year = published.split('-')[0]

    return {'title': title, 'author_str': author_str, 'year': year}

def sanitize_filename(filename):
    """
    Strips out characters from a string that are invalid or problematic in standard
    operating system file paths (Windows, macOS, or Linux).
    
    Args:
        filename (str): The raw string intended to be used as a file name.
        
    Returns:
        str: A sanitized string safe for file saving.
    """
    clean = re.sub(r'[\\/*?:"<>|]', "", filename)
    return clean.strip()

def download_arxiv_papers(urls, target_directory="."):
    """
    Downloads one or more arXiv PDFs and saves them with a standardized filename.
    
    The final filename format is: "Title (Year) - Lastname et al..pdf". It automatically 
    caps the filename length to avoid OS limits and skips downloads if the target 
    directory does not exist.
    
    Args:
        urls (str | list): A single arXiv URL string or a list of URL strings.
        target_directory (str, optional): The local folder path where PDFs should 
            be saved. Defaults to "." (the current working directory).
            
    Raises:
        FileNotFoundError: If the specified target_directory does not exist.
    """
    # Allow a single string to be passed instead of forcing a list
    if isinstance(urls, str):
        urls = [urls]
        
    if not urls:
        print("⚠️ Please provide at least one URL.")
        return

    # Strictly check if the directory exists and throw an error if it doesn't
    if not os.path.exists(target_directory):
        raise FileNotFoundError(f"❌ Error: The directory '{target_directory}' does not exist. Please create it or provide a valid path.")

    print(f"📁 Target directory confirmed: {os.path.abspath(target_directory)}\n")

    # Loop through all provided URLs
    for url in urls:
        arxiv_id = extract_arxiv_id(url)
        if not arxiv_id:
            print(f"❌ Error: Could not extract a valid arXiv ID from the URL: {url}\n")
            continue

        print(f"🔍 Processing arXiv ID: {arxiv_id}")
        print("📡 Fetching metadata from arXiv API...")

        metadata = get_metadata(arxiv_id)
        if not metadata:
            print() 
            continue

        # Construct the requested filename format
        base_name = f"{metadata['title']} ({metadata['year']}) - {metadata['author_str']}"
        safe_name = sanitize_filename(base_name)
        filename = safe_name[:240] + ".pdf"
        pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
        
        filepath = os.path.join(target_directory, filename)

        print(f"📄 Filename: {filename}")
        print("⏳ Downloading... ", end="", flush=True)

        try:
            urllib.request.urlretrieve(pdf_url, filepath)
            print("✅ Done!\n")
        except Exception as e:
            print(f"\n❌ Error downloading PDF: {e}\n")