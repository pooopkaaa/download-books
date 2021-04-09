import requests
import urllib3
from pathlib import Path

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def check_for_redirect(response):
    if response.url == 'https://tululu.org/':
        raise requests.exceptions.HTTPError(response.url)


def main():
    directory_books_name = "books"
    books_amount = 10
    Path(directory_books_name).mkdir(exist_ok=True)

    for book_id in range(1, books_amount + 1):
        url = f'https://tululu.org/txt.php?id={book_id}'
        response = requests.get(url, verify=False)

        try:
            check_for_redirect(response)
            with open(f'{directory_books_name}/id{book_id}.txt', 'wb') as file:
                file.write(response.content)
        except requests.exceptions.HTTPError as redirect_error:
            print(f'Url: {url} -> не содержит файла.
                  Происходит переадресация на {redirect_error}')


if __name__ == '__main__':
    main()
