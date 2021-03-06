import requests
from bs4 import BeautifulSoup
import datetime
from time import sleep
import re

from selenium import webdriver
from selenium.webdriver.chrome.options import Options


class Manhwa:

    def __init__(self, title, url, current_chapter, rating=0, last_checked=datetime.datetime.today()):
        self.release_data = {}

        self.title = title
        self.url = url
        self.chapters_read = current_chapter
        self.last_read = last_checked

        self.rating = rating

        # assumes that the data supplied is the latest
        self.latest_chapter = current_chapter
        self.last_released = last_checked
        self.last_checked = datetime.datetime.today()

        # provides user feedback
        print(f"'{self.title}' ENTRY CREATED")

    def unread(self):
        """Returns the number of unread chapters"""

        return self.latest_chapter - self.chapters_read

    def set_current_chapter(self, current_chapter=None):
        """Sets the highest read chapter.

        Input:
            current_chapter = The last chapter that was read. Will default to the highest known chapter.
        """

        if current_chapter is None:
            self.chapters_read = self.latest_chapter
        else:
            self.chapters_read = current_chapter

        self.last_read = datetime.datetime.today()

    def show(self):
        print(f'{self.title} [RATED: {int(self.rating)}]'
              f'\nCURRENT CHAPTER : {self.chapters_read}'
              f' | LATEST CHAPTER : {self.latest_chapter}'
              f' | UNREAD: {self.unread()}'
              f'\nLINK : {self.url}')


class AsuraScans(Manhwa):
    time_between_requests = 1

    def get_soup(self):
        """Returns a beautiful soup object of the webpage containing the manhwa data"""

        # pseudo rate limiting.
        sleep(self.time_between_requests)

        # spoofs the header to avoid complications with captchas
        header = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/74.0.3729.169 Safari/537.36",
        }

        page = requests.get(self.url, headers=header)
        return BeautifulSoup(page.text, 'html.parser')

    def update(self):
        """Updates latest_chapter and last_released."""
        old_latest_chapter = self.latest_chapter

        soup = self.get_soup()

        # gets the latest chapter number
        unprocessed_chapter_string = soup.find(class_='chapternum').text
        self.latest_chapter = int(unprocessed_chapter_string.split()[1])

        # gets the date the latest chapter was released
        unprocessed_date = soup.find(class_='chapterdate').text
        try:
            self.last_released = datetime.datetime.strptime(unprocessed_date, '%B %d, %Y')
        except ValueError:
            self.last_released = datetime.datetime.today()

        self.last_checked = datetime.datetime.today()
        self.release_data[self.latest_chapter] = self.last_released
        print(f"{self.title} - {self.latest_chapter - old_latest_chapter} CHAPTERS FOUND")


class ReaperScans(Manhwa):
    time_between_requests = 1

    def get_soup(self):
        """Returns a beautiful soup object of the webpage containing the manhwa data"""

        # pseudo rate limiting. Could implement a more elegant solution
        sleep(self.time_between_requests)

        page = requests.get(self.url)
        return BeautifulSoup(page.text, 'html.parser')

    def update(self):
        """Updates latest_chapter and last_released."""
        old_latest_chapter = self.latest_chapter

        soup = self.get_soup()

        unprocessed_data = list(soup.find(class_='wp-manga-chapter').a.stripped_strings)

        # gets the latest chapter number
        unprocessed_chapter_string = unprocessed_data[0]
        self.latest_chapter = int(unprocessed_chapter_string.split()[1])

        # gets the date the latest chapter was released
        unprocessed_date = unprocessed_data[1]
        try:
            self.last_released = datetime.datetime.strptime(unprocessed_date, '%b %d, %Y')
        except ValueError:
            self.last_released = datetime.datetime.today()

        self.last_checked = datetime.datetime.today()
        self.release_data[self.latest_chapter] = self.last_released
        print(f"{self.title} - {self.latest_chapter - old_latest_chapter} CHAPTERS FOUND")


class LineWebtoon(Manhwa):
    time_between_requests = 0.5

    def get_soup(self):
        """Returns a beautiful soup object of the webpage containing the manhwa data"""

        # pseudo rate limiting.
        sleep(self.time_between_requests)

        # convert url to rss equivalent
        rss = self.url.replace('/list?', '/rss?')

        page = requests.get(rss)
        return BeautifulSoup(page.text, 'html.parser')

    def update(self):
        """Updates latest_chapter and last_released."""
        old_latest_chapter = self.latest_chapter

        soup = self.get_soup()

        # gets the date the latest chapter was released
        unprocessed_date = soup.pubdate.string
        self.last_released = datetime.datetime.strptime(unprocessed_date, '%A, %d %b %Y %H:%M:%S %Z')

        # gets the latest chapter number

        # get HTML out of the description tag
        soup = BeautifulSoup(soup.findAll('description')[1].text, 'html.parser')

        # get link pertaining to latest chapter
        latest_chapter_url = soup.a.get('href')

        # extract chapter number from end of link
        self.latest_chapter = int(latest_chapter_url.split('=')[-1])

        self.last_checked = datetime.datetime.today()
        self.release_data[self.latest_chapter] = self.last_released
        print(f"{self.title} - {self.latest_chapter - old_latest_chapter} CHAPTERS FOUND")


def create_browser():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')

    browser = webdriver.Chrome(options=options)
    return browser


class MangaPlus(Manhwa):
    time_between_requests = 1

    def get_soup(self):
        """Returns a beautiful soup object of the webpage containing the manhwa data"""
        sleep(self.time_between_requests)

        browser = create_browser()
        browser.get(self.url)
        page_html = browser.page_source
        browser.close()

        return BeautifulSoup(page_html, 'html.parser')

    def update(self):
        """Updates latest_chapter and last_released."""
        old_latest_chapter = self.latest_chapter
        soup = self.get_soup()

        # get latest chapter number
        unprocessed_chapter_number = soup.findAll(class_=re.compile(r'ChapterListItem-module_name_.{5}'))[-1]
        self.latest_chapter = int(unprocessed_chapter_number.text[1:])

        # get release date
        unprocessed_date = soup.findAll(class_=re.compile(r'ChapterListItem-module_date_.{5}'))[-1].text
        self.last_released = datetime.datetime.strptime(unprocessed_date, '%d %b %Y')

        self.last_checked = datetime.datetime.today()
        self.release_data[self.latest_chapter] = self.last_released
        print(f"{self.title} - {self.latest_chapter - old_latest_chapter} CHAPTERS FOUND")

def update_class(data):
    class_name = data.__class__.__name__

    # set it to the updated class type
    params = [data.title, data.url, data.chapters_read, data.rating, data.last_checked]
    if class_name == 'AsuraScans':
        new_data = AsuraScans(*params)
    elif class_name == 'ReaperScans':
        new_data = ReaperScans(*params)
    elif class_name == 'MangaPlus':
        new_data = MangaPlus(*params)
    elif class_name == 'LineWebtoon':
        new_data = LineWebtoon(*params)

    # fill in remaining information
    new_data.last_read = data.last_read
    new_data.last_released = data.last_released
    new_data.latest_chapter = data.latest_chapter
    new_data.release_data = data.release_data

    return new_data