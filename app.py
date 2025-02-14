from flask import Flask, render_template, request, redirect, url_for, session
from task import Task
import random
import os

app = Flask(__name__)
app.secret_key = os.urandom(24).hex()

TASKS = [
    {'id': 1, 'text': 'Решите уравнение: 2x + 5 = 17', 'answer': '6'},
    {'id': 2, 'text': 'Найдите корни уравнения: x² - 5x + 6 = 0', 'answer': '2;3'},
    {'id': 3, 'text': 'Вычислите: √(25 + 144)', 'answer': '13'},
    {'id': 4, 'text': 'Вычислите: √(25 + 144)', 'answer': '13'},
    {'id': 5, 'text': 'Решите уравнение: 2x + 5 = 17', 'answer': '6'},
    {'id': 6, 'text': 'Найдите корни уравнения: x² - 5x + 6 = 0', 'answer': '2;3'},
    {'id': 7, 'text': 'Вычислите: √(25 + 144)', 'answer': '13'},
    {'id': 8, 'text': 'Вычислите: √(25 + 144)', 'answer': '13'}
]


def get_random_task():
    task_data = random.choice(TASKS)
    return Task(task_data['id'], task_data['text'], task_data['answer'])

@app.route('/')
def index():
    session.clear()  # Очищаем сессию при возврате на главную
    return render_template('index.html')

@app.route('/test_math', methods=['GET', 'POST'])
def test_math():
    if request.method == 'POST':
        user_answer = request.form['answer'].strip()
        task_data = session.get('current_task')
        
        if task_data and user_answer == task_data['answer']:
            session['message'] = '   Верно! Так держать!'
            session['color'] = 'green'
        else:
            session['message'] = f'   Неверно! Правильный ответ: {task_data["answer"]}'
            session['color'] = 'red'
        
        return redirect(url_for('test_math'))
    
    if 'current_task' not in session:
        return redirect(url_for('next_task'))
    
    task_data = session['current_task']
    task = Task(task_data['id'], task_data['text'], task_data['answer'])
    
    return render_template(
        'test_math.html',
        task=task,
        message=session.pop('message', None),
        color=session.pop('color', None)
    )

@app.route('/next_task')
def next_task():
    new_task = get_random_task()
    session['current_task'] = {
        'id': new_task.get_id(),
        'text': new_task.get_text(),
        'answer': new_task.get_answer()
    }
    return redirect(url_for('test_math'))

if __name__ == '__main__':
    app.run(debug=True)
