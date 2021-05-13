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


def get_book_urls(response):
    site_url = 'https://tululu.org/'
    soup = BeautifulSoup(response.text, 'lxml')
    book_cards = soup.find_all('table', class_='d_book')
    book_urls = [urljoin(site_url, book_card.find('a')['href']) for book_card in book_cards]
    return book_urls


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    books_page_amount = 10
    for books_page_number in range(1, books_page_amount + 1):
        books_page_url = f'https://tululu.org/l55/{books_page_number}'
        books_page = get_response(books_page_url)
        book_urls = get_book_urls(books_page)
        for book_url in book_urls:
            print(book_url)


if __name__ == '__main__':
    main()
