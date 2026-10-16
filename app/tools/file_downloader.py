import os
import urllib.request
import urllib.parse
from html.parser import HTMLParser

class HyperlinkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == 'a':
            attrs_dict = dict(attrs)
            href = attrs_dict.get('href')
            if href:
                self.links.append(href)

def download_documents_from_url(url: str, output_dir: str = "library") -> str:
    """Download documents or PDFs from a specified URL into the local library directory."""
    try:
        os.makedirs(output_dir, exist_ok=True)
        
        req = urllib.request.Request(
            url, 
            headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:115.0) Gecko/20100101 Firefox/115.0"}
        )
        
        with urllib.request.urlopen(req, timeout=20) as response:
            html_content = response.read().decode('utf-8', errors='ignore')
            
        parser = HyperlinkParser()
        parser.feed(html_content)
        
        base_url = "{0.scheme}://{0.netloc}".format(urllib.parse.urlparse(url))
        downloaded_files = []
        
        for link in parser.links:
            # Check for document indicators or direct extensions
            if any(ext in link.lower() for ext in ['.pdf', '.docx', '.doc', 'download', 'file']):
                target_url = link if link.startswith('http') else base_url + link
                parsed_path = urllib.parse.urlparse(target_url).path
                filename = os.path.basename(parsed_path)
                
                if not filename or '.' not in filename:
                    filename = f"legal_document_{abs(hash(target_url)) % 10000}.pdf"
                
                dest_path = os.path.join(output_dir, filename)
                try:
                    file_req = urllib.request.Request(
                        target_url,
                        headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"}
                    )
                    with urllib.request.urlopen(file_req, timeout=15) as f_res, open(dest_path, 'wb') as f_out:
                        f_out.write(f_res.read())
                    downloaded_files.append(filename)
                except Exception:
                    continue
                    
        if downloaded_files:
            return f"Successfully downloaded {len(downloaded_files)} files into ~/{output_dir}/:\n" + "\n".join([f"- {f}" for f in downloaded_files[:15]])
        else:
            return f"Connected to {url}, but no direct downloadable files were detected. The content layout can be processed as structural text notes."
            
    except Exception as e:
        return f"Download error: {str(e)}"
