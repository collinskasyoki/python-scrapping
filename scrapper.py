import os
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

SITEMAP = "https://artofmanliness.com/sitemap_index.xml"
SCRIPT_PATH = os.path.dirname(__file__)
XML_DIR = os.path.join(SCRIPT_PATH, "xmls")
SITEMAP_XML = os.path.join(XML_DIR, "sitemap_index.xml")

if not os.path.exists(SITEMAP_XML):
    res_sitemap = requests.get(SITEMAP)
    with open(SITEMAP_XML, "wb") as xmloutput:
        xmloutput.write(res_sitemap.content)
else:
    # TODO Compare files to see changes (once a week)
    pass

site_tree = ET.parse(SITEMAP_XML)
root = site_tree.getroot()

post_links = []

for sitemap in root:
    sitemap_link = sitemap.find("{http://www.sitemaps.org/schemas/sitemap/0.9}loc").text

    if "post-sitemap" not in sitemap_link:
        continue

    sitemap_modified = sitemap.find(
        "{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod"
    ).text
    post_links.append((sitemap_link, sitemap_modified))

for post_sitemap in post_links:
    parsed = urlparse(post_sitemap[0])
    file_path = os.path.join(XML_DIR, os.path.basename(parsed.path))
    if not os.path.exists(file_path):
        result_post_sitemap = requests.get(post_sitemap[0])
        with open(file_path, "wb") as xmloutput:
            xmloutput.write(result_post_sitemap.content)
    else:
        # TODO Compare files to see changes (once a week)
        pass

# Parse each of the post-sitemap files
sunday_firesides_links = []
post_sitemap_files = os.listdir(XML_DIR)
for post_sitemap_file in post_sitemap_files:
    post_sitemap_tree = ET.parse(os.path.join(XML_DIR, post_sitemap_file))
    post_sitemap_root = post_sitemap_tree.getroot()

    for link in post_sitemap_root:
        article_link = link.find(
            "{http://www.sitemaps.org/schemas/sitemap/0.9}loc"
        ).text

        if "sunday-firesides" not in article_link:
            continue

        article_modified_date = link.find(
            "{http://www.sitemaps.org/schemas/sitemap/0.9}lastmod"
        ).text

        sunday_firesides_links.append((article_link, article_modified_date))

# Delete duplicates
sunday_firesides_links = list(set(sunday_firesides_links))
