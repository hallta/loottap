"""
Input: source.yaml

Structure will include site and URL pattern.
- will load the site
- find url patterns
- ignore urls it's seen before
- send an emaiil of urls it hasn't seen before
"""
import yaml
import re
import urllib.request
import sqlite3
import hashlib
import pprint

con = sqlite3.connect('loottap.db')
cur = con.cursor()

pp = pprint.PrettyPrinter(indent=4)

def load_config(cfg):
    with open(cfg, "r") as stream:
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as e:
            print(e)
            exit(1)

def get_html_from_url(url):
    req = urllib.request.urlopen(url)
    req_b = req.read()
    req_str = req_b.decode("utf-8")
    req.close()

    return req_str


def process_urls(url_list):
    for url_obj in url_list['sites']:
        url = url_obj['url']
        html = get_html_from_url(url)
        title_re = re.compile(url_obj['title'], re.IGNORECASE)
        link_re = re.compile(url_obj['link'], re.IGNORECASE)
        titles = re.findall(title_re, html)
        links = list(map(lambda u: url + u, re.findall(link_re, html)))

        ## should have the same number of titles and links. if not,
        #  then we wont be able to match everything so something
        #  is afoot
        if len(links) != len(titles):
            raise Exception("Something is afoot len(links) != len(url); ")

    return dict(zip(links, titles))


def is_known_url(url):
    rows = cur.execute('select url from urls where url=?', [url]).fetchall()
    return len(rows) > 0


def remember_url(url, raw):
    cur.execute('insert into urls values(?,?)', [url, raw])
    con.commit()


def distribute_changes(urls):
    new_urls = []

    for u in urls:
        url = hashlib.md5(u.encode('utf-8')).hexdigest()

        if is_known_url(url):
            continue
        else:
            remember_url(url, u)
            new_urls.append(u)

    for u in new_urls:
        print(u)


def init_db():
    cur.execute("create table if not exists urls(url, raw)")

def main():
    config = load_config("source.yaml")
    urls = process_urls(config)
    distribute_changes(urls)

if __name__ == "__main__":
    init_db()
    main()