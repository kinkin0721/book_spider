# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import os.path
import requests
from time import sleep
from config import load_config, save_config
from collections import OrderedDict


class BookSite:
    def __init__(self):
        self.headers = dict()

    def get_headers(self):
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        self.headers = {'User-Agent': user_agent}

    def get_chapter_from_webpage(self, chapter):

        trycount = 0
        findchap = False

        while not findchap:
            if trycount > 0:
                print("再接続中" + str(trycount) + "......")
            if trycount > 1:
                return False, "error url: " + chapter + "\n"
                break

            webpage = get_url(chapter, self.headers)
            soup = BeautifulSoup(webpage, 'html.parser')

            for div in soup.find_all('div', id='TextContent'):
                text = arrange_text(str(div.text))
                return True, text

            if not findchap:
                trycount += 1
                print("30秒後に再接続する.......")
                sleep(30)

    def get_book_from_webpage(self, book):
        chapters = dict()

        webpage = get_url(book, self.headers)
        soup = BeautifulSoup(webpage, 'html.parser')

        for div in soup.find_all('div', id='chapterList'):
            for a in div.find_all('a'):
                if a.has_attr('href'):
                    #realurl = "http://www.yooread.com" + a['href']
                    realurl = a['href']

                    if realurl == "#bottom":
                        continue

                    print("ready to access " + realurl)
                    issuccess, strchapter = self.get_chapter_from_webpage(realurl)
                    idx = 0
                    try:
                        idx = int(realurl[:-5].replace(book, ''))
                    except ValueError:
                        pass

                    chapters[idx] = strchapter
                    title = ""
                    if a.has_attr('title'):
                        title = a['title']
                    if issuccess:
                        print(str(idx) + " " + title + " done")
                    else:
                        print(str(idx) + " " + title + " failed")
                    sleep(10)

        return chapters

    def get_books(self):

        books = load_config("./config.json")

        for book in books:
            chapters = sort_chapters(self.get_book_from_webpage(book['url']))

            strbook = ""
            for chapter in chapters:
                strbook += chapters[chapter]
            save_book(book['bookname'], strbook)
            print("「" + book['bookname'] + "」が上手に焼きました")

        print("肉が全部焼きました どうぞ")


def save_book(title, text):
    outfullname = os.path.join(OUTPUTDIR, title + ".txt")
    file = open(outfullname, "wt")
    file.write(text)
    file.close()


def get_url(url, headers, retries=10):
    try:
        res = requests.get(url, headers=headers)
    except Exception as what:
        print(what, url)
        if retries > 0:
            sleep(5)
            return get_url(url, headers, retries-1)
        else:
            print('GET Failed {}'.format(url))
            raise
    return res.content


def sort_chapters(chapters):
    chapters = OrderedDict(sorted(chapters.items()))
    return chapters


def arrange_text(text):
    text = text.replace('chap_top();', '')
    text = text.replace('chap_r2();', '')
    text = text.replace('chap_bg2();', '')
    text = text.replace('chap_r();', '')
    text = text.replace('chap_bg();', '')
    text = text.replace('chap_bb();', '')
    return text

OUTPUTDIR = "./book"
if __name__ == "__main__":
    site = BookSite()
    site.get_books()
