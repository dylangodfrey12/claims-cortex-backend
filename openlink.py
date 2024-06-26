import re
import webbrowser

def open_links(text):
    # Regular expression pattern to find URLs
    url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
    
    # Find all URLs in the text
    urls = re.findall(url_pattern, text)
    
    # Open each URL in a web browser
    for url in urls:
        # Remove the trailing single quote if present
        if url.endswith("'"):
            url = url[:-1]
        webbrowser.open(url)