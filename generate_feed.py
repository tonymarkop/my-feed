import os
from datetime import datetime, timezone
from email.utils import format_datetime
from urllib.parse import urljoin
from xml.sax.saxutils import escape

import requests
from bs4 import BeautifulSoup

# ===== غيّر هذي القيم حسب موقعك =====
SITE_URL = "https://example.com/blog"   # رابط الصفحة اللي تسحب منها
ITEM_SELECTOR = "article"               # العنصر اللي يمثل كل مقال/منتج
TITLE_SELECTOR = "h2"                   # العنوان داخل العنصر
LINK_SELECTOR = "a"                     # الرابط داخل العنصر
FEED_TITLE = "فيدي"
FEED_DESC = "فيد تلقائي من الموقع"
# =====================================

resp = requests.get(SITE_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
resp.raise_for_status()
soup = BeautifulSoup(resp.content, "html.parser")

items = []
for el in soup.select(ITEM_SELECTOR)[:30]:
    title_el = el.select_one(TITLE_SELECTOR)
    link_el = el.select_one(LINK_SELECTOR)
    if not title_el or not link_el or not link_el.get("href"):
        continue
    items.append((title_el.get_text(strip=True), urljoin(SITE_URL, link_el["href"])))

print(f"لقيت {len(items)} عنصر")

now = format_datetime(datetime.now(timezone.utc))
parts = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<rss version="2.0"><channel>',
    f"<title>{escape(FEED_TITLE)}</title>",
    f"<link>{escape(SITE_URL)}</link>",
    f"<description>{escape(FEED_DESC)}</description>",
    f"<lastBuildDate>{now}</lastBuildDate>",
]
for title, link in items:
    parts.append(
        f"<item><title>{escape(title)}</title>"
        f"<link>{escape(link)}</link>"
        f"<guid>{escape(link)}</guid>"
        f"<pubDate>{now}</pubDate></item>"
    )
parts.append("</channel></rss>")

os.makedirs("public", exist_ok=True)
with open("public/feed.xml", "w", encoding="utf-8") as f:
    f.write("\n".join(parts))
