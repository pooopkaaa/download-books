import os
import argparse
import urllib3
import json
import logging
from urllib.parse import urljoin, urlsplit, unquote
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def get_command_line_args():
    parser = argparse.ArgumentParser(
        description='Скрипт для cкачивания книг с сайта tululu.org.'
    )
    parser.add_argument('-d',
                        '--dest_folder',
                        default='books/',
                        type=str,
                        help='Укажите папку для всех файлов')
    parser.add_argument('-b',
                        '--book',
                        default='txt/',
                        type=str,
                        help='Укажите папку для txt файлов')
    parser.add_argument('-i',
                        '--image',
                        default='images/',
                        type=str,
                        help='Укажите папку для картинок')
    parser.add_argument('-j',
                        '--json_path',
                        default='descriptions',
                        type=str,
                        help='Укажите путь к файлу с описанием книг')
    parser.add_argument('-s',
                        '--start_page',
                        default=1,
                        type=int,
                        help='Укажите с какой страницы скачивать информацию по книгам')
    parser.add_argument('-e',
                        '--end_page',
                        type=int,
                        help='Укажите до какой страницы скачивать информацию по книгам')
    parser.add_argument('--skip_imgs',
                        action='store_true',
                        help='Укажите аргумент если не надо скачивать картинки')
    parser.add_argument('--skip_txt',
                        action='store_true',
                        help='Укажите аргумент если не надо скачивать книги')
    return parser.parse_args()


def get_directories(command_line_args):
    dest_folder_filepath = Path(command_line_args.dest_folder)
    dest_folder_filepath.mkdir(exist_ok=True)

    txt_filepath = Path(os.path.join(dest_folder_filepath, command_line_args.book))
    txt_filepath.mkdir(exist_ok=True)

    images_filepath = Path(os.path.join(dest_folder_filepath, command_line_args.image))
    images_filepath.mkdir(exist_ok=True)

    return txt_filepath, images_filepath


def get_books_pages_amount():
    url = 'https://tululu.org/l55/'
    response = get_response(url)
    soup = BeautifulSoup(response.text, 'lxml')
    books_pages_amount = soup.select('div#content p.center a')[-1].text
    return int(books_pages_amount)


def check_for_redirect(response):
    if response.url == 'https://tululu.org/':
        raise requests.exceptions.URLRequired(response.url)


def save_books_descriptions(book_descriptions, filename):
    with open(filename, 'w+', encoding='utf-8') as file:
        json.dump(book_descriptions, file, ensure_ascii=False, indent=4)


def download_txt(url, book_id, book_title, folder):
    payload = {'id': book_id}
    filename = sanitize_filename(f'{book_id}.{book_title}.txt')
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
    book_title, book_author = soup.select_one('h1').text.split('::')
    book_img_src = soup.select_one('div.bookimage img')['src']
    book_comments = [
        book_comment.text
        for book_comment in soup.select('div.texts span')
    ]
    book_genres = [
        book_genre.text
        for book_genre in soup.select('span.d_book a')
    ]

    return {'title': book_title.strip(),
            'author': book_author.strip(),
            'book_img_src': book_img_src,
            'comments': book_comments,
            'genres': book_genres}


def get_response(url, payload=[]):
    response = requests.get(url, params=payload, verify=False)
    response.raise_for_status()
    check_for_redirect(response)
    return response


def get_books_page(books_page_number):
    url = f'https://tululu.org/l55/{books_page_number}'
    return get_response(url)


def get_books_hrefs_on_page(response):
    soup = BeautifulSoup(response.text, 'lxml')
    book_hrefs = [
        book_card.select_one('a')['href']
        for book_card in soup.select('table.d_book')
    ]
    return book_hrefs


def fetch_book(book_href, txt_filepath, images_filepath, skip_text_bool, skip_imgs_bool):
    site_url = 'https://tululu.org/'
    book_txt_url = 'https://tululu.org/txt.php'
    book_id = book_href.replace('b', '').replace('/', '')
    book_url = urljoin(site_url, book_href)
    book_page = get_response(book_url)
    book_description = parse_book_page(book_page)
    book_title = book_description['title']
    book_img_src = book_description.pop('book_img_src')

    if not skip_text_bool:
        book_filepath = download_txt(
            book_txt_url,
            book_id,
            book_title,
            txt_filepath
        )
        book_description['book_path'] = book_filepath

    if not skip_imgs_bool:
        book_img_url = urljoin(book_url, book_img_src)
        img_filename = f"{unquote(urlsplit(book_img_url).path.split('/')[-1])}"
        img_filepath = download_image(
            book_img_url,
            img_filename,
            images_filepath
        )
        book_description['img_src'] = img_filepath

    return book_description


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    command_line_args = get_command_line_args()
    input_books_end_page = command_line_args.end_page
    books_max_page = get_books_pages_amount()

    if not input_books_end_page or input_books_end_page > books_max_page:
        logging.error(f'Количество страниц с книгами всего: {books_max_page}')
        exit()

    txt_filepath, images_filepath = get_directories(command_line_args)
    books_descriptions_filename = command_line_args.json_path + '.json'

    books_hrefs = []
    for books_page_number in range(command_line_args.start_page, input_books_end_page + 1):
        try:
            books_page = get_books_page(books_page_number)
            books_hrefs.extend(get_books_hrefs_on_page(books_page))
        except requests.exceptions.HTTPError as http_error:
            logging.error(f'Ответ пришел с ошибкой -> {http_error}')
            continue

    books_descriptions = []
    for book_href in books_hrefs:
        try:
            book_description = fetch_book(
                book_href,
                txt_filepath,
                images_filepath,
                command_line_args.skip_txt,
                command_line_args.skip_imgs
            )
            books_descriptions.append(book_description)
        except requests.exceptions.URLRequired as redirect_error:
            logging.warning(f'Переадресация на {redirect_error}')
            continue
        except requests.exceptions.HTTPError as http_error:
            logging.error(f'Ответ пришел с ошибкой -> {http_error}')
            continue

    save_books_descriptions(books_descriptions, books_descriptions_filename)


if __name__ == '__main__':
    main()
