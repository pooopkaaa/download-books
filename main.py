import urllib3
import os
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin
from urllib.parse import urlsplit

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_resonse(url):
    response = requests.get(url, verify=False)
    check_for_redirect(response)
    return response


def download_image(url, filename, folder='images/'):
    Path(folder).mkdir(exist_ok=True)
    filename = sanitize_filename(filename)
    filepath = os.path.join(folder, filename)
    response = get_resonse(url)
    with open(f'{filepath}', 'wb') as file:
        file.write(response.content)
    return filepath
    print(url, filename, folder)


def download_txt(url, filename, folder='books/'):
    Path(folder).mkdir(exist_ok=True)
    filename = sanitize_filename(filename)
    filepath = os.path.join(folder, filename)
    response = get_resonse(url)
    with open(f'{filepath}', 'wb') as file:
        file.write(response.content)
    return filepath


def parse_book_page(response):
    soup = BeautifulSoup(response.text, 'lxml')
    book_title, book_author = [book_characteristic.strip() for book_characteristic in soup.find('h1').text.split('::')]
    book_img_src = soup.find('div', class_='bookimage').img['src']
    book_comments = [book_comment.span.text for book_comment in soup.find_all('div', class_='texts')]
    book_genres = [book_genre.text for book_genre in soup.find('span', class_='d_book').find_all('a')]
    return book_title, book_author, book_img_src, book_comments, book_genres


def check_for_redirect(response):
    if response.url == 'https://tululu.org/':
        raise requests.exceptions.HTTPError(response.url)


def main():
    folder_book_name = "books/"
    folder_img_name = "images/"
    books_amount = 10

    for book_id in range(1, books_amount + 1):
        url = f'https://tululu.org/b{book_id}/'
        try:
            response = get_resonse(url)

            book_url = f'https://tululu.org/txt.php?id={book_id}'
            book_title, book_author, book_img_src, book_comments, book_genres = parse_book_page(response)
            book_filename = f'{book_id}.{book_title}.txt'
            # book_filepath = download_txt(book_url, filename, folder_book_name)

            book_img_url = urljoin(book_url, book_img_src)
            img_filename = f"{urlsplit(book_img_url).path.split('/')[-1]}"
            # img_filepath = download_image(book_img_url, img_filename, folder_img_name)

            print(book_genres)
        except requests.exceptions.HTTPError as redirect_error:
            print(f'Url: {url} -> не содержит файла.\
            Происходит переадресация на {redirect_error}')


if __name__ == '__main__':
    main()
