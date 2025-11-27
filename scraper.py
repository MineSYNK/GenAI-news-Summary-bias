from newspaper import Article

def scrape_article(url):
    """
    Scrapes the article content from the given URL.
    
    Args:
        url (str): The URL of the news article.
        
    Returns:
        str: The text content of the article, or None if an error occurs.
    """

    try:
        from newspaper import Config
        
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        config = Config()
        config.browser_user_agent = user_agent
        config.request_timeout = 10
        
        article = Article(url, config=config)
        article.download()
        article.parse()
        return article.text, article.top_image, list(article.images)
    except Exception as e:
        print(f"Newspaper3k failed: {e}. Trying fallback...")
        return scrape_with_bs4(url)

def scrape_with_bs4(url):
    """Fallback scraper using BeautifulSoup."""
    try:
        import requests
        from bs4 import BeautifulSoup
        import urllib3
        
        # Suppress SSL warnings
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        # Disable SSL verification
        response = requests.get(url, headers=headers, timeout=10, verify=False)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract Text
        paragraphs = soup.find_all('p')
        text = "\n\n".join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 20])
        
        # Extract Top Image (OG Image)
        top_image = None
        og_image = soup.find('meta', property='og:image')
        if og_image:
            top_image = og_image.get('content')
            
        # Extract All Images
        images = []
        for img in soup.find_all('img'):
            src = img.get('src')
            if src:
                if src.startswith('//'):
                    src = 'https:' + src
                elif src.startswith('/'):
                    # Need base URL, simple hack for now or ignore relative
                    pass 
                elif src.startswith('http'):
                    images.append(src)
        
        if not text:
            return None
            
        return text, top_image, images
        
    except Exception as e:
        print(f"BS4 fallback failed: {e}")
        return None
