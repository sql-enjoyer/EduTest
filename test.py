import requests
from bs4 import BeautifulSoup
import random

# URL страницы с задачами
url = 'https://neofamily.ru/russkiy-yazyk/task-bank/' + str(random.randint(64, 93))
print(url)
# Заголовки для имитации запроса от браузера
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

# Отправляем GET-запрос на страницу
response = requests.get(url, headers=headers)

# Проверяем, что запрос успешен
if response.status_code == 200:
    # Парсим HTML-код страницы
    soup = BeautifulSoup(response.text, 'html.parser')
    
    blocks = soup.find_all('div', class_='detail-text_detailText__YRcv_ [&_*]:!bg-transparent [&_*]:!text-main')
    paragraphs = blocks[0].find_all('p')

    print(paragraphs[1])

else:
    print(f'Ошибка при загрузке страницы: {response.status_code}')