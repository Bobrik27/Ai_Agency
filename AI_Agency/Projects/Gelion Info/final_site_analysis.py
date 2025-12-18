import os
import requests
from bs4 import BeautifulSoup
import sys

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
        
        # Обработка кодировки
        response.encoding = 'utf-8'
        content = response.text
        
        # Парсим содержимое
        soup = BeautifulSoup(content, 'html.parser')
        
        # Получаем заголовок страницы
        title = soup.find('title')
        if title:
            print(f"Заголовок страницы: {title.text.strip()}")
        
        # Получаем мета-описание
        description = soup.find('meta', attrs={'name': 'description'})
        if description:
            print(f"Описание страницы: {description.get('content', '')}")
        
        # Выводим первые 50 символов содержимого
        print(f"\nПервые 500 символов содержимого:")
        print(content[:500])
        
        # Проверяем наличие определенных элементов на странице
        h1_tags = soup.find_all('h1')
        if h1_tags:
            print(f"\nНайдено заголовков H1: {len(h1_tags)}")
            for i, h1 in enumerate(h1_tags, 1):
                print(f" H1 #{i}: {h1.text.strip()}")
        
        # Ищем все ссылки
        links = soup.find_all('a', href=True)
        print(f"\nНайдено ссылок: {len(links)}")
        for i, link in enumerate(links[:5], 1):  # Показываем первые 5 ссылок
            print(f" Ссылка #{i}: {link['href']} - {link.text.strip()}")
        
        # Ищем все изображения
        images = soup.find_all('img')
        print(f"\nНайдено изображений: {len(images)}")
        
        # Ищем все параграфы
        paragraphs = soup.find_all('p')
        print(f"Найдено параграфов: {len(paragraphs)}")
        
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