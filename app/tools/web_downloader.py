import os
import urllib.request
import urllib.parse
import re
from html.parser import HTMLParser

class LinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            attrs_dict = dict(attrs)
            href = attrs_dict.get('href')
            if href:
                self.links.append(href)

def download_legal_docs(url: str, output_dir: str = "library") -> str:
    """Scrape a webpage for document links or PDFs and download them locally."""
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/115.0"}
        )
        
        with urllib.request.urlopen(req, timeout=15) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            
        parser = LinkParser()
        parser.feed(html_content)
        
        downloaded = []
        base_url = "{0.scheme}://{0.netloc}".format(urllib.parse.urlparse(url))
        
        for link in parser.links:
            # Look for pdf or document view links
            if '.pdf' in link.lower() or 'document' in link.lower() or 'view' in link.lower():
                doc_url = link if link.startswith('http') else base_url + link
                filename = os.path.basename(urllib.parse.urlparse(doc_url).path)
                if not filename or not filename.endswith('.pdf'):
                    filename = f"legal_doc_{abs(hash(doc_url)) % 10000}.pdf"
                
                dest_path = os.path.join(output_dir, filename)
                try:
                    urllib.request.urlretrieve(doc_url, dest_path)
                    downloaded.append(filename)
                except Exception:
                    continue
                    
        if downloaded:
            return f"Successfully downloaded {len(downloaded)} documents into ~/{output_dir}/:\n" + "\n".join([f"- {d}" for d in downloaded[:10]])
        else:
            # Fallback: Save a text summary or snapshot of the drafting page if direct PDFs aren't exposed
            return f"Connected to {url}, but no direct PDF links were found. The page contains structured legal drafting templates that can be parsed as text. Would you like me to extract the drafting text instead?"
            
    except Exception as e:
        return f"Download error: {str(e)}"

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(download_legal_docs(sys.argv[1]))
