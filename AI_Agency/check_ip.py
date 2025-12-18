import os
import requests
from dotenv import load_dotenv

# Загружаем настройки из .env
load_dotenv()

print("--- ПРОВЕРКА ПРОКСИ ---")
try:
    # Спрашиваем у интернета "Какой у меня IP?"
    response = requests.get("https://api.ipify.org?format=json", timeout=10)
    data = response.json()
    
    print(f"Твой реальный IP (Windows): Скрыт") # Мы не узнаем IP Windows через python, если прокси работает
    print(f"IP, который видит мир через Python: {data['ip']}")
    
    if "156.246" in data['ip']:
        print("✅ УСПЕХ! Агенты работают через прокси. Окон нет.")
    else:
        print("❌ ОШИБКА! Python видит твой домашний IP.")
        
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")