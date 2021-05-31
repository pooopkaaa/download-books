from more_itertools import chunked
from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server, shell

import json
import os


def on_reload():
    book_descriptions_filename = 'descriptions.json'
    template_filename = 'template.html'
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html'])
    )
    template = env.get_template(template_filename)

    with open('descriptions.json', 'r', encoding='utf-8') as file:
        json_book_descriptions = file.read()
    book_descriptions = json.loads(json_book_descriptions)

    chunked_for_row_book_descriptions = list(chunked(book_descriptions, 2))
    chunked_for_page_book_descriptions = list(chunked(chunked_for_row_book_descriptions, 10))
    pages_amount = len(chunked_for_page_book_descriptions)
    print(pages_amount)
    for page, chunked_for_page_book_description in enumerate(chunked_for_page_book_descriptions, start=1):
        rendered_page = template.render(
            chunked_for_page_book_description=chunked_for_page_book_description,
            pages_amount=pages_amount, 
            current_page=page)
        filename = os.path.join('pages', f'index{page}.html')
        with open(filename, 'w', encoding="utf8") as file:
            file.write(rendered_page)

    server = Server()
    server.watch('*.rst', shell('make html', cwd='docs'))
    server.serve()


def main():
    on_reload()


if __name__ == '__main__':
    main()
