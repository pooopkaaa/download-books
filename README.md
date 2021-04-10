# Скрипт для cкачивания книг

Скрипт для cкачивания книг с сайта [tululu.org](https://tululu.org/).

## Установка

- Для работы скрипта у вас должен быть установлен [Python3](https://www.python.org/downloads/) (не младше версии 3.6.0)
- Скачайте код
- Установите зависимости для работы скрипта

```bash
pip install -r requirements.txt
```

## Запуск

Запустите скрипт командой с параметрами по-умолчанию:

- `--start_id 1` - скачивает книги с `1` страницы
- `--end_id 10` - скачивает книги по `10` страницу
- `--book books/` - книги скачиваются в папку `books/`
- `--image image/` - обложки скачиваются в папку `image/`

```bash
python main.py
```

## Пример работы

- Для скачивая книг в интервале страниц от 10 до 20. Сохранять книги в папку `job/`, а обложки `img/`

```bash
python main.py --start_id 10 --end_id 20 --book job/ --image img/
```

- Для скачивая книг с использованием кратких аргументов

```bash
python main.py -s 10 -e 20 -b job/ -i img/
```
