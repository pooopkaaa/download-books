import os
import urllib3
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


def check_for_redirect(response):
    if response.url == 'https://tululu.org/':
        raise requests.exceptions.URLRequired(response.url)


def get_response(url, payload=[]):
    response = requests.get(url, params=payload, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    return response


def get_book_url(response):
    site_url = 'https://tululu.org/'
    soup = BeautifulSoup(response.text, 'lxml')
    book_card = soup.find('table', class_='d_book')
    book_url = urljoin(site_url, book_card.find('a')['href'])
    return book_url


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    response = get_response('https://tululu.org/l55/')
    book_url = get_book_url(response)
    print(book_url)


if __name__ == '__main__':
    main()
