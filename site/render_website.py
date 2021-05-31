from more_itertools import chunked
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server, shell

import json
from pathlib import Path
import os


def read_book_descriptions_file(book_descriptions_filename):
    book_descriptions_filename = 'descriptions.json'
    with open(book_descriptions_filename, 'r', encoding='utf-8') as file:
        json_book_descriptions = file.read()
    book_descriptions = json.loads(json_book_descriptions)
    return book_descriptions


def group_book_descriptions(book_descriptions):
    max_columns_count = 2
    max_rows_count = 10
    chunked_row_book_descriptions = list(chunked(book_descriptions, max_columns_count))
    grouped_book_descriptions = list(chunked(chunked_row_book_descriptions, max_rows_count))
    return grouped_book_descriptions


def render_page(grouped_book_descriptions, template):
    pages_amount = len(grouped_book_descriptions)
    for page, grouped_book_description in enumerate(grouped_book_descriptions, start=1):
        rendered_page = template.render(
            grouped_book_description=grouped_book_description,
            pages_amount=pages_amount,
            current_page=page)
        filename = os.path.join('pages', f'index{page}.html')
        with open(filename, 'w', encoding="utf8") as file:
            file.write(rendered_page)


def on_reload():
    filepath_pages = Path('pages')
    filepath_pages.mkdir(exist_ok=True)
    template_filename = 'template.html'
    book_descriptions_filename = 'descriptions.json'

    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html'])
    )
    template = env.get_template(template_filename)

    book_descriptions = read_book_descriptions_file(book_descriptions_filename)
    grouped_book_descriptions = group_book_descriptions(book_descriptions)
    render_page(grouped_book_descriptions, template)


def main():
    server = Server()
    server.watch('template.html', on_reload)
    server.serve()


if __name__ == '__main__':
    main()
