import requests
from bs4 import BeautifulSoup
import pypdf
import os

def scrape_url(url: str) -> str:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        text = soup.get_text()
        # Break into lines and remove leading/trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text[:10000] # Limit content
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return ""

def extract_text_from_pdf(file_path: str) -> str:
    try:
        text = ""
        with open(file_path, 'rb') as file:
            reader = pypdf.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
        return ""

def process_inputs(file_paths: list, urls: list) -> str:
    combined_text = ""
    
    for file_path in file_paths:
        if file_path.lower().endswith('.pdf'):
            combined_text += f"\n--- Content from {os.path.basename(file_path)} ---\n"
            combined_text += extract_text_from_pdf(file_path)
        elif file_path.lower().endswith(('.txt', '.md')):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    combined_text += f"\n--- Content from {os.path.basename(file_path)} ---\n"
                    combined_text += f.read()
            except:
                pass

    for url in urls:
        combined_text += f"\n--- Content from {url} ---\n"
        combined_text += scrape_url(url)
        
    return combined_text
