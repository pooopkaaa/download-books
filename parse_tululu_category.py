import os
import argparse
import urllib3
from urllib.parse import urljoin, urlsplit, unquote
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def get_command_line_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-s',
                        '--start_id',
                        default='1',
                        type=int,
                        help='С какой страницы скачивать')
    parser.add_argument('-e',
                        '--end_id',
                        default='10',
                        type=int,
                        help='По какую страницу скачивать')
    parser.add_argument('-b',
                        '--book',
                        default='books/',
                        type=str,
                        help='Куда сохранять книги')
    parser.add_argument('-i',
                        '--image',
                        default='images/',
                        type=str,
                        help='Куда сохранять обложки')
    return parser.parse_args()


def check_for_redirect(response):
    if response.url == 'https://tululu.org/':
        raise requests.exceptions.URLRequired(response.url)


def download_txt(url, payload, filename, folder):
    filename = sanitize_filename(filename)
    filepath = os.path.join(folder, filename)
    response = get_response(url, payload)
    with open(filepath, 'w', encoding='utf-8') as file:
        file.write(response.text)
    return filepath


def download_image(url, filename, folder):
    filename = sanitize_filename(filename)
    filepath = os.path.join(folder, filename)
    response = get_response(url)
    with open(filepath, 'wb') as file:
        file.write(response.content)
    return filepath


def parse_book_page(response):
    soup = BeautifulSoup(response.text, 'lxml')
    book_title, book_author = soup.find('h1').text.split('::')
    book_img_src = soup.find('div', class_='bookimage').img['src']
    book_comments = [book_comment.span.text for book_comment in soup
                     .find_all('div', class_='texts')]
    book_genres = [book_genre.text for book_genre in soup
                   .find('span', class_='d_book')
                   .find_all('a')]

    return {'book_title': book_title.strip(),
            'book_author': book_author.strip(),
            'book_img_src': book_img_src,
            'book_comments': book_comments,
            'book_genres': book_genres}


def get_response(url, payload=[]):
    response = requests.get(url, params=payload, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    return response


def get_book_hrefs(response):
    soup = BeautifulSoup(response.text, 'lxml')
    book_cards = soup.find_all('table', class_='d_book')
    book_hrefs = [book_card.find('a')['href'] for book_card in book_cards]
    return book_hrefs


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    command_line_args = get_command_line_args()
    Path(command_line_args.book).mkdir(exist_ok=True)
    Path(command_line_args.image).mkdir(exist_ok=True)

    books_page_amount = 10
    site_url = 'https://tululu.org/'
    book_txt_url = 'https://tululu.org/txt.php'

    for books_page_number in range(1, books_page_amount + 1):
        books_page_url = f'https://tululu.org/l55/{books_page_number}'
        
        print(f'Номер страницы {books_page_number}')

        books_page = get_response(books_page_url)
        book_hrefs = get_book_hrefs(books_page)

        for book_href in book_hrefs:
            try:
                book_id = book_href.replace('b', '').replace('/','')
                book_url = urljoin(site_url, book_href)
                book_page = get_response(book_url)
                book_description = parse_book_page(book_page)

                book_title = book_description['book_title']
                book_author = book_description['book_author']
                book_img_src = book_description['book_img_src']
                book_genres = book_description['book_genres']
                book_comments = book_description['book_comments']

                book_txt_payload = {'id': book_id}
                book_filename = f'{book_id}.{book_title}.txt'
                book_filepath = download_txt(book_txt_url,
                                            book_txt_payload,
                                            book_filename,
                                            command_line_args.book)

                book_img_url = urljoin(book_url, book_img_src)
                img_filename = f"{unquote(urlsplit(book_img_url).path.split('/')[-1])}"
                img_filepath = download_image(book_img_url,
                                            img_filename,
                                            command_line_args.image)
                
                print(f'Ссылка на книгу {book_url}')
            except requests.exceptions.URLRequired as redirect_error:
                print(f'{book_url} -> переадресация на {redirect_error}')
            except requests.exceptions.HTTPError as http_error:
                print(f'Ответ пришел с ошибкой -> {http_error}')

if __name__ == '__main__':
    main()
