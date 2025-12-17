import sys
import signal
import os

# ==============================================================================
# 1. WINDOWS FIX (ЭТОТ БЛОК ОБЯЗАН БЫТЬ САМЫМ ПЕРВЫМ)
# ==============================================================================
if sys.platform.startswith('win'):
    unix_signals = ['SIGABRT', 'SIGALRM', 'SIGBUS', 'SIGCHLD', 'SIGCONT', 'SIGFPE', 'SIGHUP', 'SIGILL', 'SIGINT', 'SIGIO', 'SIGIOT', 'SIGKILL', 'SIGPIPE', 'SIGPOLL', 'SIGPROF', 'SIGPWR', 'SIGQUIT', 'SIGSEGV', 'SIGSTOP', 'SIGSYS', 'SIGTERM', 'SIGTRAP', 'SIGTSTP', 'SIGTTIN', 'SIGTTOU', 'SIGURG', 'SIGUSR1', 'SIGUSR2', 'SIGVTALRM', 'SIGWINCH', 'SIGXCPU', 'SIGXFSZ']
    for name in unix_signals:
        if not hasattr(signal, name):
            try: setattr(signal, name, signal.SIGTERM)
            except AttributeError: setattr(signal, name, 1)
# ==============================================================================

# Теперь безопасно импортируем CrewAI
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM

# ==============================================================================
# 2. НАСТРОЙКА ПУТЕЙ (УМНАЯ)
# ==============================================================================
# Определяем, где лежит этот скрипт, чтобы найти файлы рядом с ним
current_dir = os.path.dirname(os.path.abspath(__file__))

# Пути относительно скрипта
CONFIG_DIR = os.path.join(current_dir, "configs")
OUTPUT_DIR = os.path.join(current_dir, "output")
# Ищем корень агентства (поднимаемся на 2 уровня вверх: AirClub -> Projects -> AI_Agency)
AGENCY_ROOT = os.path.dirname(os.path.dirname(current_dir)) 
BRAIN_DIR = os.path.join(AGENCY_ROOT, "Agency_Brain")
ENV_PATH = os.path.join(AGENCY_ROOT, ".env")

# Загружаем ключи
if os.path.exists(ENV_PATH):
    load_dotenv(dotenv_path=ENV_PATH)
    print("✅ Ключи загружены")
else:
    # Пытаемся найти .env, если структура папок отличается (например AI_Agency/AI_Agency)
    # Поднимаемся еще на уровень
    load_dotenv(dotenv_path=os.path.join(os.path.dirname(AGENCY_ROOT), ".env"))

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Функция чтения промптов
def load_agent_prompt(filename):
    path = os.path.join(CONFIG_DIR, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return f"ТЫ ЭКСПЕРТ. (Файл {filename} не найден, использую дефолт)"

# Функция чтения правил из Мозга
def load_global_rule(category, filename):
    path = os.path.join(BRAIN_DIR, category, filename)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return ""

print(f"--- ЗАПУСК ПРОЕКТА: AIRCLUB ---")

# ==============================================================================
# 3. ПОДКЛЮЧЕНИЕ МОЗГОВ
# ==============================================================================
llm_gemini = None
llm_groq = None
llm_gpt4 = None

if os.getenv("GEMINI_API_KEY"):
    llm_gemini = LLM(model="gemini/gemini-2.5-flash", api_key=os.getenv("GEMINI_API_KEY"))

if os.getenv("GROQ_API_KEY"):
    llm_groq = LLM(model="openai/llama-3.3-70b-versatile", base_url="https://api.groq.com/openai/v1", api_key=os.getenv("GROQ_API_KEY"))

if os.getenv("OPENAI_API_KEY"):
    llm_gpt4 = LLM(model="openai/gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))

# ==============================================================================
# 4. АГЕНТЫ
# ==============================================================================

# Скептик (Gemini)
agent_skeptic = Agent(
    role='Business Analyst',
    goal='Найти риски',
    backstory=load_agent_prompt("role_skeptic.md"),
    llm=llm_gemini,
    verbose=True
)

# Инноватор (Groq)
agent_innovator = Agent(
    role='Innovator',
    goal='Генерировать идеи',
    backstory=load_agent_prompt("role_innovator.md"),
    llm=llm_groq, 
    verbose=True
)

# Босс (GPT-4o)
agent_boss = Agent(
    role='Manager',
    goal='Принять решение',
    backstory=load_agent_prompt("role_boss.md"),
    llm=llm_gpt4,
    verbose=True
)

# ==============================================================================
# 5. ЗАДАЧИ
# ==============================================================================
topic = "Сайт для частного Аэроклуба"

task_skeptic = Task(
    description=f"{topic}. Напиши 3 главных риска.",
    expected_output="Отчет о рисках.",
    agent=agent_skeptic,
    async_execution=True, 
    output_file=os.path.join(OUTPUT_DIR, "1_risks.md")
)

task_innovator = Task(
    description=f"{topic}. Придумай 3 вау-фичи.",
    expected_output="Отчет об идеях.",
    agent=agent_innovator,
    async_execution=True,
    output_file=os.path.join(OUTPUT_DIR, "2_ideas.md")
)

task_boss = Task(
    description="Объедини отчеты. Напиши Финальную Концепцию.",
    expected_output="Концепция.",
    agent=agent_boss,
    context=[task_skeptic, task_innovator],
    output_file=os.path.join(OUTPUT_DIR, "3_concept.md")
)

# ==============================================================================
# 6. ЗАПУСК
# ==============================================================================
crew = Crew(
    agents=[agent_skeptic, agent_innovator, agent_boss],
    tasks=[task_skeptic, task_innovator, task_boss],
    verbose=True
)

crew.kickoff()
print(f"✅ Готово! Результаты в папке: {OUTPUT_DIR}")