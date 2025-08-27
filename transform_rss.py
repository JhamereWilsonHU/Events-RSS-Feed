import requests
from lxml import etree as ET

# 1. Define the source RSS feed
FEED_URL = "https://events.howard.edu/calendar.xml"

# 2. Download the feed
response = requests.get(FEED_URL)
response.raise_for_status()  # stop if download fails
xml_content = response.content

# 3. Parse the XML into a tree structure
parser = ET.XMLParser(recover=True)  # recover=True makes it tolerant of bad XML
root = ET.fromstring(xml_content, parser=parser)

ns = {"media": "http://search.yahoo.com/mrss/"}

channel = root.find("channel")
if channel is None:
    raise SystemExit("channel element not found in feed")

all_items = channel.findall("item")
print(f"Found {len(all_items)} items in source feed")  # diagnostic

for extra in all_items[10:]:
    channel.remove(extra)

kept_items = channel.findall("item")
print(f"Kept {len(kept_items)} items after trimming")  # diagnostic

# ...existing item-processing code...
items = kept_items  # use the trimmed list

for item in items:
    media = item.find("media:content", namespaces=ns)   # locate media:content
    desc = item.find("description")                     # locate description

    if media is not None and desc is not None:
        img_url = media.attrib.get("url")  # get the image URL
        if img_url:
            original_html = desc.text or ""
            new_html = (
                f'<div><img src="{img_url}" style="width: 100%;" />'
                f'<div>{original_html}</div></div>'
            )

            desc.clear()
            desc.text = ET.CDATA(new_html)

# 8. Save the transformed feed (use pretty_print so file is readable)
tree = ET.ElementTree(root)
tree.write("transformed_feed.xml", encoding="utf-8", xml_declaration=True, pretty_print=True)
print("Wrote transformed_feed.xml")