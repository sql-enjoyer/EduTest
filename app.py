from flask import Flask, render_template, request, redirect, url_for, session
from task import Task

import os
from bs4 import BeautifulSoup
import requests
import random

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept-Language': 'ru-RU,ru;q=0.9',
    'Referer': 'https://neofamily.ru/'
}

wrong_messages   = [ "Ответ неверный!",
                    "Неправильно.",
                    "Кто не ошибается, тот не развивается!"
                ]

correct_messages = [ "Ответ верный!",
                    "Правильно!",
                    "Точно! Так держать!",
                    "Верный ответ!",
                    "Отлично!",
                    "Абсолютно верно!"
                ]

def get_random_task():
    """
    Получает случайную задачу с сайта.
    """
    # Костылима
    excluded_numbers = {82, 94, 95, 96, 122}
    number = random.randint(64, 124)
    while number in excluded_numbers:
        number = random.randint(64, 124)

    task_id = str(number)
    url = f'https://neofamily.ru/russkiy-yazyk/task-bank/{task_id}'
    response = requests.get(url, headers=headers)
    # , proxies={"SOCKS4": "http://78.109.139.51:5678"}
    if response.status_code != 200:
        return Task(task_id, f'Ошибка при загрузке страницы: {response.status_code}', None)

    soup = BeautifulSoup(response.text, 'html.parser')
    blocks = soup.find_all('div', class_='detail-text_detailText__YRcv_ [&_*]:!bg-transparent [&_*]:!text-main')

    if not blocks:
        return Task(task_id, 'Не удалось найти условие задачи', None)

    # Парсинг условия задачи
    paragraphs = blocks[0].find_all('p')
    if len(paragraphs) < 2:
        return Task(task_id, 'Не удалось найти текст задачи', None)

    # Первый <p> — условие задачи (без переноса строк)
    condition = ''
    for element in paragraphs[0].contents:
        if element.name == 'strong':
            condition += f"<strong>{element.string}</strong>"
        elif element.string:
            condition += element.string.strip() + " "

    # Второй <p> — текст задачи с сохранением <br>
    task_text = condition + " <br>"
    for element in paragraphs[1].contents:
        if element.name == 'br':
            task_text += "<br>"
        elif element.string:
            task_text += element.string.strip() + " "

    paragraphs = blocks[1].find_all('p')
    task_answer = paragraphs[1].get_text().split()[1]

    return Task(task_id.strip(), task_text.strip(), task_answer.strip())


@app.route('/')
def index():
    """
    Главная страница.
    """
    session.clear()
    return render_template('index.html')


@app.route('/test_russ', methods=['GET', 'POST'])
def test_russ():
    """
    Страница с тестом по математике.
    """
    if request.method == 'POST':
        user_answer = request.form['answer'].strip()
        task_data = session.get('current_task')

        if task_data and sorted(user_answer) == sorted(task_data['answer']):
            session['message'] = random.choice(correct_messages)
            session['color'] = 'green'
        else:
            session['message'] = random.choice(wrong_messages)
            session['color'] = 'red'

        return redirect(url_for('test_russ'))

    if 'current_task' not in session:
        return redirect(url_for('next_task'))

    task_data = session['current_task']
    task = Task(task_data['id'], task_data['text'], task_data['answer'])

    return render_template(
        'test_russ.html',
        task=task,
        message=session.pop('message', None),
        color=session.pop('color', None)
    )


@app.route('/next_task')
def next_task():
    """
    Переход к следующей задаче.
    """
    new_task = get_random_task()
    session['current_task'] = {
        'id': new_task.get_id(),
        'text': new_task.get_text(),
        'answer': new_task.get_answer()
    }
    return redirect(url_for('test_russ'))


if __name__ == '__main__':
    app.run(debug=True)