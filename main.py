import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def main():
    url = 'https://tululu.org/txt.php?id=3216834234234'
    response = requests.get(url, verify=False)
    with open('book.txt', 'wb') as file:
        file.write(response.content)


if __name__ == '__main__':
    main()
