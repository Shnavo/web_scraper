from typing import TypedDict
from urllib.parse import urlsplit, urljoin

from bs4 import BeautifulSoup, Tag
import requests


class PageData(TypedDict):
    url: str
    heading: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]


def normalize_url(url: str) -> str:
    parsed = urlsplit(url)
    edited = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    edited = edited.rstrip("/")
    return edited.lower()


def get_heading_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    h_tag = soup.find("h1") or soup.find("h2")
    return h_tag.get_text(strip=True) if isinstance(h_tag, Tag) else ""


def get_first_paragraph_from_html(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")

    main_part = soup.find("main")
    if isinstance(main_part, Tag):
        p_tag = main_part.find("p")
    else:
        p_tag = soup.find("p")

    return p_tag.get_text(strip=True) if isinstance(p_tag, Tag) else ""


def get_urls_from_html(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    urls = []
    links = soup.find_all("a")

    for link in links:
        if not isinstance(link, Tag):
            continue
        href = link.get("href")
        if isinstance(href, str) and href:
            try:
                absolute = urljoin(base_url, href)
                urls.append(absolute)
            except Exception as e:
                print(f"{str(e)}: {href}")

    return urls


def get_images_from_html(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "html.parser")
    image_urls = []
    images = soup.find_all("img")

    for img in images:
        if not isinstance(img, Tag):
            continue
        src = img.get("src")
        if isinstance(src, str) and src:
            try:
                absolute = urljoin(base_url, src)
                image_urls.append(absolute)
            except Exception as e:
                print(f"{str(e)}: {src}")

    return image_urls


def extract_page_data(html: str, page_url: str) -> PageData:
    return {
        "url": page_url,
        "heading": get_heading_from_html(html),
        "first_paragraph": get_first_paragraph_from_html(html),
        "outgoing_links": get_urls_from_html(html, page_url),
        "image_urls": get_images_from_html(html, page_url),
    }


def get_html(url: str) -> str:
    try:
        resp = requests.get(url, headers={"User-Agent": "Crawler/1.0"})
    except Exception as e:
        raise Exception(f"network error while fetching {url}: {e}")

    if resp.status_code > 399:
        raise Exception(f"Client error response: {resp.status_code} {resp.reason}")

    if "text/html" not in resp.headers["content-type"]:
        raise Exception(f"Incorrect type of response: {resp.headers["content-type"]}")

    return resp.text


def crawl_page(
    base_url: str,
    current_url: str | None = None,
    page_data: dict[str, PageData] | None = None,
) -> dict[str, PageData]:

    if current_url == None:
        current_url = base_url
    if page_data == None:
        page_data = {}

    p_base = urlsplit(base_url)
    p_current = urlsplit(current_url)
    if p_base.netloc != p_current.netloc:
        return page_data

    norm_url = normalize_url(current_url)

    if norm_url in page_data:
        return page_data

    print(f"crawling {current_url}")
    html = get_html(norm_url)
    if html is None:
        return page_data

    data = extract_page_data(html, current_url)
    page_data[norm_url] = data

    if data["outgoing_links"] != []:
        for next_url in data["outgoing_links"]:
            if "email-protection" in next_url or next_url.endswith("jpg"):
                continue
            page_data = crawl_page(base_url, next_url, page_data)

    return page_data
