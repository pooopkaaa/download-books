# Своя библиотека

![Screen](https://github.com/pooopkaaa/download-books/blob/main/site/screen.png)

Проект состоит из двух частей:

- Скрипт для cкачивания книг с сайта [tululu.org](https://tululu.org/).
- Cтатичный сайт для удобного просмотра скачанных книг, пример [сайта](https://pooopkaaa.github.io/download-books/site/pages/index.html).

## Установка

- Для работы скрипта у вас должен быть установлен [Python3](https://www.python.org/downloads/) (не младше версии 3.6.0).
- Скачайте код.
- Рекомендуется использовать [virtualenv/env](https://docs.python.org/3/library/venv.html) для изоляции проекта.
- Установите зависимости для работы скрипта

```bash
pip install -r requirements.txt
```

## Запуск

Для скачивания книг необходимо запустить скрипт с переданными необязательными параметрами:

Параметр | Пример 1 | Пример 2 | Описание
------- | -------- | -------- | --------
`--dest_folder`<br>`-d` | `--dest_folder books` | `-d books` | Укажите папку для всех файлов. По умолчанию `books`.
`--book`<br>`-b` | `--book txt` | `-b txt` | Укажите папку для txt файлов. По умолчанию `txt`.
`--image`<br>`-i` | `--image images` | `-i images` | Укажите папку для картинок. По умолчанию `images`.
`--json_path`<br>`-j` | `--json_path descriptions` | `-j descriptions` | Укажите путь к файлу с описанием книг. По умолчанию `descriptions`.
`--start_page`<br>`-s` | `--start_page 1` | `-s 1` | Укажите с какой страницы скачивать информацию по книгам. По умолчанию c `1`.
`--end_page`<br>`-e` | `--end_page 702` | `-e 702` | Укажите до какой страницы скачивать информацию по книгам.
`--skip_imgs` | | | Укажите если не надо скачивать картинки.
`--skip_txt` | | | Укажите аргумент если не надо скачивать книги.

Пример запуска без параметров:

```sh
python parse_tululu_category.py
```

## Рендер страниц для сайта

1. После запуска скрипта:

```sh
python parse_tululu_category.py
```

В корневой директорию создаются:

- Файл с описанием книг. По умолчанию `descriptions.json`.
- Папка с загруженными файлами с сайта [tululu.org](https://tululu.org/). По умолчанию `books`.

Созданый файл и папку необходимо скопировать в директорию вашего сайта.

2. Скопируйте файл и папки из директории [site](https://github.com/pooopkaaa/download-books/tree/main/site) в папку с вашим сайтом:

- `css/`
- `img/`
- `js/`
- `template.html`

3. Запустите скрипт в директории вашего сайта:

```sh
python render_website.py
```

После запуска скрипта в папке `pages/` будут страницы с книгами.

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org).
