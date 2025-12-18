import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import sys
import io

# Устанавливаем кодировку для правильного вывода
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Загружаем переменные из .env файла
load_dotenv()

# Настройка прокси
proxies = {
    'http': 'http://Lt1JLh3r:Ceidfu24@156.246.237.183:63020',
    'https': 'http://Lt1JLh3r:Ceidfu24@156.246.237.183:63020'
}

# Заголовки для имитации реального браузера
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

try:
    # Попытка получить доступ к сайту
    print("Попытка доступа к https://www.aerodrom-gelion.ru/...")
    response = requests.get("https://www.aerodrom-gelion.ru/", proxies=proxies, headers=headers, timeout=15)
    
    if response.status_code == 200:
        print(f"[SUCCESS] Сайт доступен! Статус код: {response.status_code}")
        print(f"Длина содержимого: {len(response.text)} символов")
        
        # Парсим содержимое
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Получаем заголовок страницы
        title = soup.find('title')
        if title:
            print(f"Заголовок страницы: {title.text.strip()}")
        
        # Получаем мета-описание
        description = soup.find('meta', attrs={'name': 'description'})
        if description:
            print(f"Описание страницы: {description.get('content', '')[:10]}...")
        
        # Выводим первые 300 символов содержимого
        print(f"\nПервые 300 символов содержимого:")
        content_preview = response.text[:300].encode('utf-8', errors='ignore').decode('utf-8')
        print(content_preview)
        
        # Проверяем наличие определенных элементов на странице
        h1_tags = soup.find_all('h1')
        if h1_tags:
            print(f"\nНайдено заголовков H1: {len(h1_tags)}")
            for i, h1 in enumerate(h1_tags, 1):
                print(f" H1 #{i}: {h1.text.strip()}")
        
        print("\n[SUCCESS] Анализ сайта завершен успешно")
        
    else:
        print(f"[ERROR] Ошибка при доступе к сайту: {response.status_code}")
        
except requests.exceptions.ProxyError as e:
    print(f"[ERROR] Ошибка прокси: {e}")
except requests.exceptions.Timeout as e:
    print(f"[ERROR] Таймаут соединения: {e}")
except requests.exceptions.ConnectionError as e:
    print(f"[ERROR] Ошибка соединения: {e}")
except Exception as e:
    print(f"[ERROR] Произошла ошибка: {str(e)}")