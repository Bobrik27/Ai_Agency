import sys
import signal
import os

# WINDOWS PATCH
if sys.platform.startswith('win'):
    unix_signals = ['SIGABRT', 'SIGALRM', 'SIGBUS', 'SIGCHLD', 'SIGCONT', 'SIGFPE', 'SIGHUP', 'SIGILL', 'SIGINT', 'SIGIO', 'SIGIOT', 'SIGKILL', 'SIGPIPE', 'SIGPOLL', 'SIGPROF', 'SIGPWR', 'SIGQUIT', 'SIGSEGV', 'SIGSTOP', 'SIGSYS', 'SIGTERM', 'SIGTRAP', 'SIGTSTP', 'SIGTTIN', 'SIGTTOU', 'SIGURG', 'SIGUSR1', 'SIGUSR2', 'SIGVTALRM', 'SIGWINCH', 'SIGXCPU', 'SIGXFSZ']
    for name in unix_signals:
        if not hasattr(signal, name):
            try: setattr(signal, name, signal.SIGTERM)
            except AttributeError: setattr(signal, name, 1)

from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

# ПУТИ
current_dir = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(current_dir, "configs")
OUTPUT_DIR = os.path.join(current_dir, "output")
AGENCY_ROOT = os.path.dirname(os.path.dirname(current_dir))
ENV_PATH = os.path.join(AGENCY_ROOT, ".env")

os.makedirs(OUTPUT_DIR, exist_ok=True)
load_dotenv(dotenv_path=ENV_PATH)

# ИНСТРУМЕНТЫ
search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()

# МОДЕЛИ
# 1. Groq (Разведчик - быстро и бесплатно ищет)
llm_scout = LLM(
    model="openai/llama-3.3-70b-versatile",
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY")
)

# 2. DeepSeek (Аналитик - думает над данными)
llm_analyst = LLM(
    model="openai/deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 3. GPT-4o (Босс - сводит всё в стратегию)
llm_boss = LLM(
    model="openai/gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY")
)

# ЧТЕНИЕ ПРОМПТОВ
def load_prompt(name):
    try:
        with open(os.path.join(CONFIG_DIR, name), 'r', encoding='utf-8') as f:
            return f.read()
    except: return "You are an expert agent."

# АГЕНТЫ
agent_scout = Agent(
    role="Web Scout",
    goal="Найти и извлечь данные с сайтов конкурентов",
    backstory=load_prompt("role_scout.md"),
    llm=llm_scout,
    tools=[search_tool, scrape_tool], # Даем доступ в интернет
    verbose=True,
    allow_delegation=False
)

agent_analyst = Agent(
    role="Deep Analyst",
    goal="Проанализировать данные и найти инсайты",
    backstory=load_prompt("role_analyst.md"),
    llm=llm_analyst,
    verbose=True
)

agent_strategist = Agent(
    role="Chief Strategy Officer",
    goal="Создать глобальную стратегию развития",
    backstory=load_prompt("role_strategist.md"),
    llm=llm_boss,
    verbose=True
)

# ВХОДНЫЕ ДАННЫЕ
TARGET_SITE = "https://www.aerodrom-gelion.ru/" # <--- СЮДА ВСТАВИТЬ САЙТ КЛИЕНТА
COUNTRIES = ["Germany", "USA", "Austria"]

tasks = []

# ГЕНЕРАЦИЯ ЗАДАЧ (ДИНАМИЧЕСКИ)
# Для каждой страны создаем задачу поиска
for country in COUNTRIES:
    task_search = Task(
        description=f"Найти топ-3 лучших сайта частных аэроклубов в стране: {country}. "
                    f"Используй Google Search. Затем используй ScrapeWebsiteTool, чтобы прочитать главные страницы этих 3 сайтов. "
                    f"Собери тексты, заголовки и предложения.",
        expected_output=f"Подробный отчет с контентом 3 сайтов ({country}).",
        agent=agent_scout
    )
    tasks.append(task_search)

# Задача анализа (ждет выполнения всех поисков)
task_analysis = Task(
    description=f"Изучи отчеты Разведчика по всем странам. "
                f"Также проанализируй сайт нашего клиента: {TARGET_SITE} (если он доступен, если нет - используй общие данные). "
                f"Выдели 10 лучших идей (Best Practices) и 5 ошибок конкурентов.",
    expected_output="Глубокий аналитический отчет (Markdown).",
    agent=agent_analyst,
    context=tasks # Передаем результаты всех поисков
)

# Задача стратегии
task_strategy = Task(
    description="На основе Аналитического отчета составь 'Стратегию Развития 2025'. "
                "Включи: Дизайн-код, Маркетинг-микс, Структуру сайта, Roadmap внедрения.",
    expected_output="Финальный документ 'STRATEGY_2025.md'",
    agent=agent_strategist,
    context=[task_analysis],
    output_file=os.path.join(OUTPUT_DIR, "STRATEGY_2025.md")
)

# СОБИРАЕМ КОМАНДУ
crew = Crew(
    agents=[agent_scout, agent_analyst, agent_strategist],
    tasks=[*tasks, task_analysis, task_strategy], # Распаковываем список задач поиска + анализ + стратегия
    verbose=True
)

if __name__ == "__main__":
    print("🚀 НАЧИНАЕМ ГЛОБАЛЬНОЕ ИССЛЕДОВАНИЕ...")
    crew.kickoff()
    print("✅ ГОТОВО! Стратегия в папке output.")