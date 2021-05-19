import os
import argparse
from itertools import count
import urllib3
import json
from urllib.parse import urljoin, urlsplit, unquote
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename


def get_command_line_args():
    parser = argparse.ArgumentParser()
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
                        default=702,
                        type=int,
                        help='Укажите до какой страницы скачивать информацию по книгам')
    parser.add_argument('--skip_imgs',
                        action='store_true',
                        help='Укажите аргумент если не надо скачивать картинки')
    parser.add_argument('--skip_txt',
                        action='store_true',
                        help='Укажите аргумент если не надо скачивать книги')
    return parser.parse_args()


def check_for_redirect(response):
    if response.url == 'https://tululu.org/':
        raise requests.exceptions.URLRequired(response.url)


def create_json_file(filename):
    with open(filename, 'w') as file:
        file.write('[]')


def save_book_description(book_description, filename):
    with open(filename, 'r+', encoding='utf-8') as file:
        books_description = json.load(file)
        books_description.append(book_description)
        file.seek(0)
        json.dump(books_description, file, ensure_ascii=False, indent=4)


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
    book_title, book_author = soup.select_one('h1').text.split('::')
    book_img_src = soup.select_one('div.bookimage img')['src']
    book_comments = [book_comment.text for book_comment in soup
                     .select('div.texts span')]
    book_genres = [book_genre.text for book_genre in soup
                   .select('span.d_book a')]

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


def get_book_hrefs(response):
    soup = BeautifulSoup(response.text, 'lxml')
    book_hrefs = [book_card.select_one('a')['href'] for book_card in soup
                  .select('table.d_book')]
    return book_hrefs


def main():
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    command_line_args = get_command_line_args()

    dest_folder_filepath = Path(command_line_args.dest_folder)
    dest_folder_filepath.mkdir(exist_ok=True)

    txt_filepath = Path(os.path.join(dest_folder_filepath, command_line_args.book))
    txt_filepath.mkdir(exist_ok=True)

    images_filepath = Path(os.path.join(dest_folder_filepath, command_line_args.image))
    images_filepath.mkdir(exist_ok=True)

    books_description_filename = command_line_args.json_path + '.json'
    if not os.path.exists(books_description_filename):
        create_json_file(books_description_filename)

    site_url = 'https://tululu.org/'
    book_txt_url = 'https://tululu.org/txt.php'

    for books_page_number in range(command_line_args.start_page, command_line_args.end_page):
        books_page_url = f'https://tululu.org/l55/{books_page_number}'

        print(f'Номер страницы {books_page_number}')

        books_page = get_response(books_page_url)
        book_hrefs = get_book_hrefs(books_page)

        for book_href in book_hrefs:
            try:
                book_id = book_href.replace('b', '').replace('/', '')
                book_url = urljoin(site_url, book_href)
                book_page = get_response(book_url)
                book_description = parse_book_page(book_page)

                book_title = book_description['title']
                book_img_src = book_description.pop('book_img_src')

                if not command_line_args.skip_txt:
                    book_txt_payload = {'id': book_id}
                    book_filename = f'{book_id}.{book_title}.txt'
                    book_filepath = download_txt(
                        book_txt_url,
                        book_txt_payload,
                        book_filename,
                        txt_filepath
                    )
                    book_description['book_path'] = book_filepath

                if not command_line_args.skip_imgs:
                    book_img_url = urljoin(book_url, book_img_src)
                    img_filename = f"{unquote(urlsplit(book_img_url).path.split('/')[-1])}"
                    img_filepath = download_image(
                        book_img_url,
                        img_filename,
                        images_filepath
                    )
                    book_description['img_src'] = img_filepath

                save_book_description(book_description, books_description_filename)

                print(f'Ссылка на книгу {book_url}')
            except requests.exceptions.URLRequired as redirect_error:
                print(f'{book_url} -> переадресация на {redirect_error}')
            except requests.exceptions.HTTPError as http_error:
                print(f'Ответ пришел с ошибкой -> {http_error}')


if __name__ == '__main__':
    main()
