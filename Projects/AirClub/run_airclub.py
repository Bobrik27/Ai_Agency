import sys
import signal
import os
import asyncio

# ==============================================================================
# 1. WINDOWS FIX (Критично для 2025 года)
# ==============================================================================
if sys.platform.startswith('win'):
    unix_signals = ['SIGABRT', 'SIGALRM', 'SIGBUS', 'SIGCHLD', 'SIGCONT', 'SIGFPE', 'SIGHUP', 'SIGILL', 'SIGINT', 'SIGIO', 'SIGIOT', 'SIGKILL', 'SIGPIPE', 'SIGPOLL', 'SIGPROF', 'SIGPWR', 'SIGQUIT', 'SIGSEGV', 'SIGSTOP', 'SIGSYS', 'SIGTERM', 'SIGTRAP', 'SIGTSTP', 'SIGTTIN', 'SIGTTOU', 'SIGURG', 'SIGUSR1', 'SIGUSR2', 'SIGVTALRM', 'SIGWINCH', 'SIGXCPU', 'SIGXFSZ']
    for name in unix_signals:
        if not hasattr(signal, name):
            try: setattr(signal, name, signal.SIGTERM)
            except AttributeError: setattr(signal, name, 1)

from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

# ==============================================================================
# 2. НАСТРОЙКА ПУТЕЙ
# ==============================================================================
current_dir = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(current_dir, "configs")
OUTPUT_DIR = os.path.join(current_dir, "output")
AGENCY_ROOT = os.path.dirname(os.path.dirname(current_dir)) 
BRAIN_DIR = os.path.join(AGENCY_ROOT, "Agency_Brain")
ENV_PATH = os.path.join(AGENCY_ROOT, ".env")

# Создаем папки, если их нет
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

# Загрузка ключей
if os.path.exists(ENV_PATH):
    load_dotenv(dotenv_path=ENV_PATH)
    print("✅ Ключи загружены из .env")
else:
    print("⚠️ Файл .env не найден! Проверь пути.")

# Функция чтения промптов
def load_agent_prompt(filename):
    path = os.path.join(CONFIG_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        # Создаем заглушку, чтобы код не падал при первом старте
        return f"Ты профессиональный агент. Твоя роль: {filename.replace('.md', '')}."

print(f"--- ЗАПУСК ПРОЕКТА: AIRCLUB ---")

# ==============================================================================
# 3. ПОДКЛЮЧЕНИЕ МОДЕЛЕЙ (LLM)
# ==============================================================================
# 1. Gemini (Аналитик)
llm_gemini = LLM(
    model="gemini/gemini-1.5-flash", # Используем 1.5 как стабильную версию
    api_key=os.getenv("GEMINI_API_KEY")
)

# 2. Groq (Скорость/Креатив)
llm_groq = LLM(
    model="openai/llama-3.3-70b-versatile",
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

# 3. GPT-4o (Босс/Качество)
llm_gpt4 = LLM(
    model="openai/gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY")
)

# 4. DeepSeek (Кодер/Технарь)
llm_deepseek = LLM(
    model="openai/deepseek-chat", 
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com" # Убрал /v1, так надежнее для оф. API
)

# ==============================================================================
# 4. АГЕНТЫ
# ==============================================================================

agent_skeptic = Agent(
    role='Business Analyst (Skeptic)',
    goal='Найти риски и слабые места',
    backstory=load_agent_prompt("role_skeptic.md"),
    llm=llm_gemini,
    verbose=True
)

agent_innovator = Agent(
    role='Creative Director',
    goal='Придумать уникальные фишки',
    backstory=load_agent_prompt("role_innovator.md"),
    llm=llm_groq, 
    verbose=True
)

agent_boss = Agent(
    role='Project Manager',
    goal='Синтезировать отчет и принять решение',
    backstory=load_agent_prompt("role_boss.md"),
    llm=llm_gpt4,
    verbose=True
)

# Добавляем DeepSeek в команду
agent_coder = Agent(
    role="Senior Tech Lead",
    goal="Составить технический стек на основе концепции",
    backstory=load_agent_prompt("role_tech_lead.md"),
    llm=llm_deepseek,
    verbose=True
)

# ==============================================================================
# 5. ЗАДАЧИ
# ==============================================================================
topic = "Сайт для элитного частного Аэроклуба"

# Задача 1: Анализ рисков (Параллельно)
task_skeptic = Task(
    description=f"Тема: {topic}. Проанализируй нишу и напиши 3 главных бизнес-риска.",
    expected_output="Краткий отчет о рисках (Markdown).",
    agent=agent_skeptic,
    async_execution=True, 
    output_file=os.path.join(OUTPUT_DIR, "1_risks.md")
)

# Задача 2: Креатив (Параллельно)
task_innovator = Task(
    description=f"Тема: {topic}. Придумай 3 'Вау-фичи' для сайта, чтобы удивить миллионеров.",
    expected_output="Краткий список идей (Markdown).",
    agent=agent_innovator,
    async_execution=True,
    output_file=os.path.join(OUTPUT_DIR, "2_ideas.md")
)

# Задача 3: Концепция (Ждет первых двух)
task_boss = Task(
    description="Изучи риски и идеи. Напиши утвержденную Концепцию Проекта.",
    expected_output="Финальная концепция сайта.",
    agent=agent_boss,
    context=[task_skeptic, task_innovator], # Босс ждет их
    output_file=os.path.join(OUTPUT_DIR, "3_concept.md")
)

# Задача 4: Техническое задание (Делает DeepSeek после Босса)
task_coder = Task(
    description="На основе утвержденной Концепции составь стек технологий (Frontend/Backend) и структуру БД.",
    expected_output="Технический стек и архитектура.",
    agent=agent_coder,
    context=[task_boss], # Кодер ждет Босса
    output_file=os.path.join(OUTPUT_DIR, "4_tech_stack.md")
)

# ==============================================================================
# 6. ЗАПУСК
# ==============================================================================
crew = Crew(
    agents=[agent_skeptic, agent_innovator, agent_boss, agent_coder], # Все в сборе
    tasks=[task_skeptic, task_innovator, task_boss, task_coder],      # Порядок важен
    verbose=True,
    process=Process.hierarchical, # Можно sequential (по умолчанию) или hierarchical
    manager_llm=llm_gpt4          # Нужен только если process=Process.hierarchical
)

# Для простого последовательного запуска лучше убрать process=Process.hierarchical
# Давай используем простой Sequential для начала, чтобы меньше багов
crew = Crew(
    agents=[agent_skeptic, agent_innovator, agent_boss, agent_coder],
    tasks=[task_skeptic, task_innovator, task_boss, task_coder],
    verbose=True
)

if __name__ == "__main__":
    crew.kickoff()
    print(f"\n✅ Готово! Проверь папку: {OUTPUT_DIR}")