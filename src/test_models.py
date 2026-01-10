#!/usr/bin/env python3
import sys
import os
import asyncio
import signal
from dotenv import load_dotenv

# --- WINDOWS COMPATIBILITY PATCHES (NUCLEAR OPTION) ---
# Этот блок должен быть в КАЖДОМ файле, где импортируется crewai на Windows
if sys.platform.startswith('win'):
    # 1. Asyncio Fix
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    # 2. Signal Fix (Глушим всё)
    unix_signals = [
        'SIGABRT', 'SIGALRM', 'SIGBUS', 'SIGCHLD', 'SIGCONT', 'SIGFPE', 'SIGHUP', 
        'SIGILL', 'SIGINT', 'SIGIO', 'SIGIOT', 'SIGKILL', 'SIGPIPE', 'SIGPOLL', 
        'SIGPROF', 'SIGPWR', 'SIGQUIT', 'SIGSEGV', 'SIGSTOP', 'SIGSYS', 'SIGTERM', 
        'SIGTRAP', 'SIGTSTP', 'SIGTTIN', 'SIGTTOU', 'SIGURG', 'SIGUSR1', 'SIGUSR2', 
        'SIGVTALRM', 'SIGWINCH', 'SIGXCPU', 'SIGXFSZ'
    ]
    for name in unix_signals:
        if not hasattr(signal, name):
            try: setattr(signal, name, getattr(signal, 'SIGTERM', 1))
            except AttributeError: setattr(signal, name, 1)

# Импорт CrewAI строго ПОСЛЕ патча
from crewai import LLM

load_dotenv()

def test_model(provider_name, model_name, api_key_env):
    print(f"\n🧪 Тестируем: {provider_name} ({model_name})...")
    
    key = os.getenv(api_key_env)
    if not key:
        print(f"❌ ОШИБКА: Нет ключа {api_key_env} в .env")
        return

    try:
        # Инициализация LLM
        llm = LLM(model=model_name, api_key=key)
        # Простой вызов
        response = llm.call("Скажи 'Работает' и назови свою модель.")
        print(f"✅ УСПЕХ: {response}")
    except Exception as e:
        print(f"❌ ОШИБКА подключения к {provider_name}: {e}")

if __name__ == "__main__":
    print("=== ПРОВЕРКА МОДЕЛЕЙ (MULTI-LLM CHECK) ===")
    
    # 1. Google Gemini (Researcher)
    test_model("Google", "gemini/gemini-2.5-flash", "GEMINI_API_KEY")
    
    # 2. Groq (Skeptic/Coder)
    # Используем llama-3.3-70b-versatile, она стабильнее
    test_model("Groq", "groq/llama-3.3-70b-versatile", "GROQ_API_KEY")
    
    # 3. OpenAI (Boss)
    test_model("OpenAI", "gpt-5.1", "OPENAI_API_KEY")


    # 4. DeepSeek (coder)
    test_model("DeepSeek", "deepseek/deepseek-coder", "DEEPSEEK_API_KEY")

