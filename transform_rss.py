import requests
import xml.etree.ElementTree as ET

# RSS feed URL
RSS_URL = "https://events.howard.edu/calendar.xml"
OUTPUT_FILE = "transformed_feed.xml"

# Fetch RSS feed
response = requests.get(RSS_URL)
response.raise_for_status()
xml_content = response.content

# Register namespace for media
ET.register_namespace("media", "http://search.yahoo.com/mrss/")
namespaces = {"media": "http://search.yahoo.com/mrss/"}

# Parse XML
root = ET.fromstring(xml_content)

# Locate channel and items
channel = root.find("channel")
items = channel.findall("item")[:10]

# Remove all existing items
for old_item in channel.findall("item"):
    channel.remove(old_item)

# Transform and reinsert 10 items
for item in items:
    description = item.find("description")
    media = item.find("media:content", namespaces)

    if media is not None and description is not None:
        img_url = media.attrib.get("url", "")
        original_cdata = description.text or ""
        new_cdata = f'<![CDATA[<div><img src="{img_url}" style="width: 100%;" /></div>{original_cdata}]]>'
        description.text = new_cdata

    channel.append(item)

# Save transformed feed
tree = ET.ElementTree(root)
tree.write(OUTPUT_FILE, encoding="utf-8", xml_declaration=True)
print(f"Transformed feed saved to {OUTPUT_FILE}")
