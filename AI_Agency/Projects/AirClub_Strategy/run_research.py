import sys
import signal
import os

# ==============================================================================
# 1. WINDOWS FIX
# ==============================================================================
if sys.platform.startswith('win'):
    unix_signals = ['SIGABRT', 'SIGALRM', 'SIGBUS', 'SIGCHLD', 'SIGCONT', 'SIGFPE', 'SIGHUP', 'SIGILL', 'SIGINT', 'SIGIO', 'SIGIOT', 'SIGKILL', 'SIGPIPE', 'SIGPOLL', 'SIGPROF', 'SIGPWR', 'SIGQUIT', 'SIGSEGV', 'SIGSTOP', 'SIGSYS', 'SIGTERM', 'SIGTRAP', 'SIGTSTP', 'SIGTTIN', 'SIGTTOU', 'SIGURG', 'SIGUSR1', 'SIGUSR2', 'SIGVTALRM', 'SIGWINCH', 'SIGXCPU', 'SIGXFSZ']
    for name in unix_signals:
        if not hasattr(signal, name):
            try: setattr(signal, name, signal.SIGTERM)
            except AttributeError: setattr(signal, name, 1)

from dotenv import load_dotenv
from crewai import Agent, Task, Crew, LLM
from crewai_tools import SerperDevTool, ScrapeWebsiteTool

# ==============================================================================
# 2. НАСТРОЙКИ
# ==============================================================================
current_dir = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(current_dir, "configs")
OUTPUT_DIR = os.path.join(current_dir, "output")
AGENCY_ROOT = os.path.dirname(os.path.dirname(current_dir)) 
ENV_PATH = os.path.join(AGENCY_ROOT, ".env")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CONFIG_DIR, exist_ok=True)

if os.path.exists(ENV_PATH):
    load_dotenv(dotenv_path=ENV_PATH)
    print("✅ Ключи загружены.")
else:
    print("⚠️ Ошибка: .env не найден!")

# ==============================================================================
# 3. ИНСТРУМЕНТЫ И МОДЕЛИ
# ==============================================================================

search_tool = SerperDevTool()
scrape_tool = ScrapeWebsiteTool()

# 1. Gemini 1.5 Flash (НОВЫЙ РАЗВЕДЧИК - Огромный контекст для сайтов)
llm_gemini = LLM(
    model="gemini/gemini-1.5-flash",
    api_key=os.getenv("GEMINI_API_KEY")
)

# 2. DeepSeek (Аналитик - Умный)
llm_deepseek = LLM(
    model="openai/deepseek-chat",
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# 3. GPT-4o (Босс - Качество)
llm_gpt4 = LLM(
    model="openai/gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY")
)

def load_prompt(name):
    path = os.path.join(CONFIG_DIR, name)
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "You are an expert agent."

# ==============================================================================
# 4. АГЕНТЫ
# ==============================================================================

# Разведчик (ТЕПЕРЬ НА GEMINI)
agent_scout = Agent(
    role="Global Web Scout",
    goal="Найти сайты лучших аэроклубов мира и собрать их контент",
    backstory=load_prompt("role_scout.md"),
    llm=llm_gemini, # <--- СМЕНИЛИ МОДЕЛЬ
    tools=[search_tool, scrape_tool], 
    verbose=True,
    allow_delegation=False
)

agent_analyst = Agent(
    role="Business Analyst (Luxury Aviation)",
    goal="Сравнить наш сайт с конкурентами и найти точки роста",
    backstory=load_prompt("role_analyst.md"),
    llm=llm_deepseek,
    verbose=True
)

agent_strategist = Agent(
    role="Chief Strategy Officer",
    goal="Разработать стратегию трансформации аэроклуба",
    backstory=load_prompt("role_strategist.md"),
    llm=llm_gpt4,
    verbose=True
)

# ==============================================================================
# 5. ЗАДАЧИ
# ==============================================================================

TARGET_SITE = "https://www.aerodrom-gelion.ru/"
# Убрали одну страну (США), чтобы ускорить процесс и сэкономить время, оставили топ-2
COUNTRIES = ["Germany", "Austria"] 

tasks = []

# 1. Задачи на поиск
for country in COUNTRIES:
    t = Task(
        description=f"Найти в Google топ-3 частных аэроклуба в стране: {country}. "
                    f"Используя инструмент ScrapeWebsiteTool, зайди на их сайты. "
                    f"Собери ВСЕ текстовое содержимое главной страницы.",
        expected_output=f"Сырой текст с сайтов клубов в {country}.",
        agent=agent_scout
    )
    tasks.append(t)

# 2. Задача на анализ нашего сайта
task_scrape_ours = Task(
    description=f"Зайди на НАШ сайт {TARGET_SITE}. Прочитай все страницы. "
                f"Опиши текущее позиционирование.",
    expected_output="Отчет по сайту Aerodrom Gelion.",
    agent=agent_scout
)
tasks.append(task_scrape_ours)

# 3. Анализ (DeepSeek)
task_analysis = Task(
    description="Ты получил данные. Проведи Сравнительный Анализ. "
                "1. Чем европейские сайты лучше? "
                "2. Какие конкретно разделы у них есть? "
                "3. Как они продают эмоцию полета?",
    expected_output="Markdown отчет: Бенчмаркинг.",
    agent=agent_analyst,
    context=tasks,
    output_file=os.path.join(OUTPUT_DIR, "1_Global_Benchmark.md")
)

# 4. Стратегия (GPT-4o)
task_strategy = Task(
    description="Разработай 'Стратегию Гелион 2025'. "
                "Нужна структура сайта, маркетинговые фишки и roadmap.",
    expected_output="Финальный документ.",
    agent=agent_strategist,
    context=[task_analysis],
    output_file=os.path.join(OUTPUT_DIR, "2_STRATEGY_GELION.md")
)

# ==============================================================================
# 6. ЗАПУСК
# ==============================================================================
crew = Crew(
    agents=[agent_scout, agent_analyst, agent_strategist],
    tasks=[*tasks, task_analysis, task_strategy], 
    verbose=True
)

if __name__ == "__main__":
    print(f"🚀 ПЕРЕЗАПУСК (GEMINI VERSION) ДЛЯ: {TARGET_SITE}")
    crew.kickoff()
    print(f"\n✅ ГОТОВО! Проверяй папку: {OUTPUT_DIR}")