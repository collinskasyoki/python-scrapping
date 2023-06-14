from urllib.request import Request, urlopen
import os
import sqlite3
from requests import get
from bs4 import BeautifulSoup

SCRIPT_PATH = os.path.dirname(__file__)
DATABASE_PATH = os.path.join(SCRIPT_PATH, "articles.db")

conn = sqlite3.connect(DATABASE_PATH)
c = conn.cursor()

select_query = "SELECT id, link FROM articles"
links_db = c.execute(select_query)
links = links_db.fetchall()

for eachlink in links:
    link_id = eachlink[0]
    link_url = eachlink[1]

    req = get(link_url)
    result = req.text
    soup = BeautifulSoup(result, "html.parser")
    print(result)
    # article = urlopen(link_url)
    # html = article.read().html_bytes.decode("utf-8")
    # print(html)
    break

# article = urlopen("./index.html")
# html = article.read().html_bytes.decode("utf-8")
# print(html)
