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

wrong_messages = ["Ответ неверный!", "Неправильно.", "Кто не ошибается, тот не развивается!"]
correct_messages = ["Ответ верный!", "Правильно!", "Точно!", "Верный ответ!", "Отлично!", "Абсолютно верно!"]

def get_random_task(subject):
    """
    Получает случайную задачу для указанного предмета с сохранением форматирования
    """
    subject_config = {
        'russ': {
            'base_url': 'https://neofamily.ru/russkiy-yazyk/task-bank/',
            'excluded': {82, 94, 95, 96, 122},
            'min': 64,
            'max': 124
        },
        'liter': {
            'base_url': 'https://neofamily.ru/literatura/task-bank/',
            'excluded': {26, 36, 37, 38},
            'min': 22,
            'max': 55
        },
        'math': {
            'base_url': 'https://neofamily.ru/matematika-baza/task-bank/',
            'excluded': set(),
            'min': 4354,
            'max': 4363
        },
        'hist': {
            'base_url': 'https://neofamily.ru/istoriya/task-bank/',
            'excluded': {3273},
            'min': 3272,
            'max': 3279
        }
    }

    config = subject_config.get(subject)
    if not config:
        raise ValueError("Недопустимый предмет")

    while True:
        number = random.randint(config['min'], config['max'])
        if number not in config['excluded']:
            break

    url = f"{config['base_url']}{number}"
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        return Task(str(number), f'Ошибка: {response.status_code}', None)

    soup = BeautifulSoup(response.text, 'html.parser')
    blocks = soup.find_all('div', class_='detail-text_detailText__YRcv_')

    if not blocks or len(blocks) < 2:
        return Task(str(number), 'Не удалось найти условие задачи', None)

    try:
        condition_block = blocks[0]
        for element in condition_block.find_all('button'):
            element.decompose()
            
        task_html = []
        for p in condition_block.find_all('p'):
            p_html = p.decode_contents().strip()
            p_html = p_html.replace('\n', '<br>')
            task_html.append(f'<p>{p_html}</p>')
            
        task_text = ''.join(task_html)
        
        answer_blocks = blocks[1].find_all('p')
        if len(answer_blocks) < 2:
            return Task(str(number), 'Ошибка: Неправильная структура блока ответа', None)
            
        answer = answer_blocks[1].get_text().split()
        if len(answer) < 2:
            return Task(str(number), 'Ошибка: Не найден ответ', None)
            
        answer = answer[1].strip()

    except Exception as e:
        return Task(str(number), f'Ошибка парсинга: {str(e)}', None)

    return Task(str(number), task_text.strip(), answer)

def handle_test(subject, template):
    """
    Общая логика обработки тестов.
    """
    session_key = f'current_task_{subject}'
    
    if request.method == 'POST':
        user_answer = request.form['answer'].strip().lower().replace(' ', '')
        task_data = session.get(session_key)

        if task_data:
            correct_answer = task_data['answer'].lower().replace(' ', '')
            if subject == "russ" and sorted(user_answer) == sorted(correct_answer):
                session['message'] = random.choice(correct_messages)
                session['color'] = 'green'
            elif user_answer == correct_answer:
                session['message'] = random.choice(correct_messages)
                session['color'] = 'green'
            else:
                session['message'] = random.choice(wrong_messages)
                session['color'] = 'red'
        else:
            session['message'] = "Ошибка: задача не найдена"
            session['color'] = 'red'
            
        return redirect(url_for(f'test_{subject}'))

    if session_key not in session:
        return redirect(url_for('next_task', subject=subject))

    task_data = session[session_key]
    return render_template(
        template,
        task=Task(task_data['id'], task_data['text'], task_data['answer']),
        message=session.pop('message', None),
        color=session.pop('color', None)
    )

@app.route('/')
def index():
    session.clear()
    return render_template('index.html')

@app.route('/test_russ', methods=['GET', 'POST'])
def test_russ():
    return handle_test('russ', 'test_russ.html')

@app.route('/test_liter', methods=['GET', 'POST'])
def test_liter():
    return handle_test('liter', 'test_liter.html')

@app.route('/test_math', methods=['GET', 'POST'])
def test_math():
    return handle_test('math', 'test_math.html')

@app.route('/test_hist', methods=['GET', 'POST'])
def test_hist():
    return handle_test('hist', 'test_hist.html')

@app.route('/next_task/<subject>')
def next_task(subject):
    new_task = get_random_task(subject)
    session[f'current_task_{subject}'] = {
        'id': new_task.id,
        'text': new_task.text,
        'answer': new_task.answer
    }
    return redirect(url_for(f'test_{subject}'))

if __name__ == '__main__':
    app.run(debug=False)