import requests
from lxml import etree as ET
from datetime import datetime
import urllib.parse
import re

# 1. Define the source RSS feed
FEED_URL = "https://events.howard.edu/calendar.xml"

# 2. Download the feed
response = requests.get(FEED_URL)
response.raise_for_status()
xml_content = response.content

# 3. Parse the XML into a tree structure
parser = ET.XMLParser(recover=True)
root = ET.fromstring(xml_content, parser=parser)

ns = {"media": "http://search.yahoo.com/mrss/"}

channel = root.find("channel")
if channel is None:
    raise SystemExit("channel element not found in feed")

all_items = channel.findall("item")
print(f"Found {len(all_items)} items in source feed")

# Keep only first 10 items
for extra in all_items[10:]:
    channel.remove(extra)

kept_items = channel.findall("item")
print(f"Kept {len(kept_items)} items after trimming")

for item in kept_items:
    # --- Strip date from title (supports 3-letter or full month) ---
    title_elem = item.find("title")
    if title_elem is not None and title_elem.text:
        # Matches "Sep 15, 2025:" or "September 15, 2025:"
        title_elem.text = re.sub(
            r'^(?:[A-Za-z]{3,9}) \d{1,2}, \d{4}:\s*', '', title_elem.text
        )

    # --- Process pubDate ---
    pub_date = item.find("pubDate")
    pub_date_text = ""
    if pub_date is not None and pub_date.text:
        try:
            dt = datetime.strptime(pub_date.text, "%a, %d %b %Y %H:%M:%S %z")
            pub_date_text = dt.strftime("%a, %d %b %Y")
            pub_date.text = pub_date_text
        except ValueError:
            pub_date_text = pub_date.text

    # --- Process description and media ---
    media = item.find("media:content", namespaces=ns)
    desc = item.find("description")

    if media is not None and desc is not None:
        img_url = media.attrib.get("url")
        if img_url:
            original_html = desc.text or ""

            # Decode URL-encoded characters to remove '+' etc.
            decoded_html = urllib.parse.unquote(original_html)

            # Build new HTML with pubDate under image
            new_html = (
                f'<div>'
                f'  <img src="{img_url}" style="width: 100%;" />'
                f'  <div style="font-size: 0.9em; color: #555;"><strong>{pub_date_text}</strong></div>'
                f'  <div>{decoded_html}</div>'
                f'</div>'
            )

            desc.clear()
            desc.text = ET.CDATA(new_html)

# 8. Save the transformed feed
tree = ET.ElementTree(root)
tree.write("transformed_feed.xml", encoding="utf-8", xml_declaration=True, pretty_print=True)
print("Wrote transformed_feed.xml")
