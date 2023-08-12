from urllib.request import Request, urlopen
import os
import sqlite3
from requests import get
from bs4 import BeautifulSoup
import time

SCRIPT_PATH = os.path.dirname(__file__)
DATABASE_PATH = os.path.join(SCRIPT_PATH, "articles.db")

conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()

# Fetch links
# Only fetch non-existing articles
query_select = (
    "SELECT id, link FROM articles WHERE id NOT IN (SELECT article_id FROM content)"
)
links_db = c.execute(query_select)
links = links_db.fetchall()

# Fetch categories
query_select_cat = "SELECT id, name FROM categories"
categories_db = c.execute(query_select_cat)
tmp_existing_categories = categories_db.fetchall()
existing_categories = {}
for tmp_cat in tmp_existing_categories:
    existing_categories[tmp_cat[1]] = tmp_cat[0]


for eachlink in links:
    link_id = eachlink[0]
    link_url = eachlink[1]

    req = get(link_url)
    result = req.text
    soup = BeautifulSoup(result, "html.parser")

    date_published = soup.find("span", itemprop="datePublished").string
    h1 = soup.find("h1", class_="post-title", itemprop="headline").string

    content = soup.find("div", class_="post-content-column")
    content_paragraphs = ""
    for paragraph in content:
        if paragraph.name == "p" or paragraph.name == "blockquote":
            if paragraph.string is not None:
                content_paragraphs = content_paragraphs + str(paragraph) + "\n"

    # Add content details to db
    query_insert_content = "INSERT INTO content(article_id, title, date_published, content) VALUES(?,?,?,?)"
    c.execute(query_insert_content, (link_id, h1, date_published, content_paragraphs))
    content_id = c.lastrowid

    # Parse and add categories to db
    souped_categories = soup.find("p", class_="in-category")
    categories = []
    for category in souped_categories.find_all("a"):
        if category.string not in existing_categories:
            query_insert_cat = "INSERT INTO categories(name) VALUES(?)"
            c.execute(query_insert_cat, [(category.string)])
            cat_id = c.lastrowid
            query_insert_cat_article = (
                "INSERT INTO content_categories(content_id, category_id) VALUES(?,?)"
            )
            c.execute(query_insert_cat_article, (content_id, cat_id))
        else:
            query_insert_cat_article = (
                "INSERT INTO content_categories(content_id, category_id) VALUES(?,?)"
            )
            c.execute(
                query_insert_cat_article,
                (content_id, existing_categories[category.string]),
            )
    conn.commit()
    time.sleep(3)
