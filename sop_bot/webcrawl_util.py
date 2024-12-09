import requests
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize
import ssl

ssl._create_default_https_context = ssl._create_unverified_context


# Ensure you download the necessary NLTK resources
nltk.download("punkt_tab")
nltk.download("punkt")
nltk.download("wordnet")
nltk.download("omw-1.4")


def fetch_sitemap(sitemap_url, seen_sitemaps=None):
    """
    Recursively fetch URLs from a sitemap, including nested sitemaps.

    Args:
        sitemap_url (str): URL of the sitemap to process.
        seen_sitemaps (set): Set of already processed sitemaps to avoid duplication.

    Returns:
        list: All URLs found in the sitemap and nested sitemaps.
    """
    if seen_sitemaps is None:
        seen_sitemaps = set()

    urls = []
    try:
        # Prevent duplicate processing
        if sitemap_url in seen_sitemaps:
            return urls

        seen_sitemaps.add(sitemap_url)
        response = requests.get(sitemap_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "xml")

        # Find URLs in the sitemap
        for loc in soup.find_all("loc"):
            loc_text = loc.text.strip()
            if loc_text.endswith(".xml"):
                # If the URL points to another sitemap, process it recursively
                urls.extend(fetch_sitemap(loc_text, seen_sitemaps))
            else:
                urls.append(loc_text)

    except Exception as e:
        print(f"Error processing {sitemap_url}: {e}")

    return urls


# def fetch_sitemap(sitemap_url):
#     """Fetch and parse sitemap.xml."""
#     response = requests.get(sitemap_url)
#     response.raise_for_status()
#     soup = BeautifulSoup(response.content, "xml")
#     return [loc.text for loc in soup.find_all("loc")]


def fetch_page_content(url):
    """Fetch the content of a web page."""
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def chunk_text(text, chunk_size=1000):
    """Chunk the text into smaller parts."""
    sentences = sent_tokenize(text, language="english")
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk) + len(sentence) > chunk_size:
            chunks.append(current_chunk)
            current_chunk = ""
        current_chunk += sentence + " "
    if current_chunk:
        chunks.append(current_chunk)
    return chunks


def get_webcrawl_chunks(sitemap_url: str):
    nltk.download("punkt_tab")
    nltk.download("punkt")
    nltk.download("wordnet")
    nltk.download("omw-1.4")

    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt")

    print("Fetching sitemap...")
    urls = fetch_sitemap(sitemap_url)

    all_chunks = []
    print(f"Found {len(urls)} URLs in sitemap.")
    count = 0
    for url in urls:
        all_chunks.append(url)
        if count > 5:
            break
        # print(f"Fetching content from: {url}")
        # try:
        #     html_content = fetch_page_content(url)
        #     chunks = chunk_text(html_content)
        #     all_chunks.extend(chunks)
        # except Exception as e:
        #     print(f"Failed to fetch content from {url}: {e}")
        count += 1
    # print("Storing chunks to ChromaDB...")
    # # store_to_vectordb(all_chunks)
    # print("Process completed!")
    return all_chunks
