import requests
import urllib3
from pathlib import Path

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    directory_books_name = "books"
    books_amount = 10
    Path(directory_books_name).mkdir(exist_ok=True)

    for book_id in range(1, books_amount + 1):
        url = f'https://tululu.org/txt.php?id={book_id}'
        response = requests.get(url, verify=False)
        with open(f'{directory_books_name}/id{book_id}.txt', 'wb') as file:
            file.write(response.content)


if __name__ == '__main__':
    main()
