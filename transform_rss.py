import xml.etree.ElementTree as ET
import requests

# Register namespace for media
ET.register_namespace("media", "http://search.yahoo.com/mrss/")

# Input and output files
INPUT_FEED = "calendar.xml"
OUTPUT_FEED = "transformed_feed.xml"

# Download the RSS feed (optional: you can skip this if file is local)
url = "https://events.howard.edu/calendar.xml?card_size=small&experience=&hide_recurring=1"
with requests.get(url) as r:
    with open(INPUT_FEED, "wb") as f:
        f.write(r.content)

# Parse the feed
tree = ET.parse(INPUT_FEED)
root = tree.getroot()

# XML namespaces
ns = {"media": "http://search.yahoo.com/mrss/"}

# Create a new root
new_root = ET.Element("rss", version="2.0")
new_channel = ET.SubElement(new_root, "channel")

# Copy channel-level elements except items
for child in root.find("channel"):
    if child.tag != "item":
        new_channel.append(child)

# Process each item
for item in root.findall("channel/item"):
    new_item = ET.SubElement(new_channel, "item")

    # Copy title and other basic fields
    for tag in ["title", "link", "pubDate", "guid"]:
        el = item.find(tag)
        if el is not None:
            new_el = ET.SubElement(new_item, tag)
            new_el.text = el.text

    # Handle description with CDATA
    desc = item.find("description")
    media = item.find("media:content", ns)

    if desc is not None:
        desc_text = desc.text or ""
        if media is not None and "url" in media.attrib:
            img_url = media.attrib["url"]
            new_html = f'<div><img src="{img_url}" style="width: 100%;" /></div>{desc_text}'
            new_desc = ET.SubElement(new_item, "description")
            new_desc.text = ET.CDATA(new_html)
        else:
            new_desc = ET.SubElement(new_item, "description")
            new_desc.text = ET.CDATA(desc_text)

# Write out the transformed feed
tree = ET.ElementTree(new_root)
tree.write(OUTPUT_FEED, encoding="utf-8", xml_declaration=True)
