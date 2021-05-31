import json

from jinja2 import Environment, FileSystemLoader, select_autoescape
from livereload import Server, shell


def on_reload():
    server = Server()
    server.watch('*.rst', shell('make html', cwd='docs'))
    server.serve()


def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as file:
        json_book_descriptions = file.read()
    return json.loads(json_book_descriptions)


def get_render_page(template, book_descriptions):
    rendered_page = template.render(
        book_descriptions=book_descriptions)

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


def main():
    book_descriptions_filename = 'descriptions.json'
    template_filename = 'template.html'
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html'])
    )
    template = env.get_template(template_filename)
    book_descriptions = read_file(book_descriptions_filename)
    get_render_page(template, book_descriptions)
    on_reload()


if __name__ == '__main__':
    main()
