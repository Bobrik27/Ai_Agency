#!/usr/bin/env python3
import sys
import os
import asyncio
import yaml
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv

# --- 1. WINDOWS PATCH (CRITICAL) ---
# Обязательно для работы CrewAI на Windows
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from crewai import Agent, Task, Crew, Process

# Загрузка переменных окружения
load_dotenv()

# --- 2. ROBUST PATH HANDLING ---
# Определяем пути относительно текущего файла main.py, а не места запуска терминала
BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"

def load_yaml(path: Path) -> Dict[str, Any]:
    """Безопасная загрузка YAML."""
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}

def create_agents(agents_config: Dict[str, Any]) -> Dict[str, Agent]:
    """
    Создает агентов из словаря конфигурации.
    Возвращает словарь {agent_key: AgentObject}, чтобы потом искать их для задач.
    """
    agents_map = {}
    
    # DeepSeek мог вернуть список, если YAML был списком. Обрабатываем оба варианта.
    if isinstance(agents_config, list):
        # Превращаем список в словарь, используя 'name' или индекс как ключ
        iterator = {item.get('role', f'agent_{i}'): item for i, item in enumerate(agents_config)}.items()
    else:
        iterator = agents_config.items()

    for key, config in iterator:
        # Пропускаем пустые конфиги
        if not config: continue
        
        print(f"  [+] Creating Agent: {config.get('role', key)}")
        
        # Создаем агента
        agent = Agent(
            role=config.get('role'),
            goal=config.get('goal'),
            backstory=config.get('backstory'),
            verbose=config.get('verbose', True),
            allow_delegation=config.get('allow_delegation', False),
            # Здесь можно добавить логику выбора LLM (Groq/OpenAI) в зависимости от конфига
            # llm=ChatOpenAI(model_name=config.get('llm_model', 'gpt-4o')) 
        )
        agents_map[key] = agent
        
        # Если в конфиге было имя, добавим ссылку и по имени тоже
        if 'name' in config:
            agents_map[config['name']] = agent

    return agents_map

def create_tasks(tasks_config: Dict[str, Any], agents_map: Dict[str, Agent]) -> List[Task]:
    """Создает задачи и связывает их с агентами."""
    tasks = []
    
    # Обработка списка или словаря
    if isinstance(tasks_config, list):
        iterator = enumerate(tasks_config)
        is_list = True
    else:
        iterator = tasks_config.items()
        is_list = False

    for key, config in iterator:
        task_name = f"Task {key}" if is_list else key
        
        agent_ref = config.get('agent')
        assigned_agent = agents_map.get(agent_ref)

        if not assigned_agent:
            print(f"⚠️  WARNING: Agent '{agent_ref}' not found for task '{task_name}'. Checking keys...")
            # Попытка найти агента по роли, если по ключу не вышло
            for a_key, a_obj in agents_map.items():
                if a_obj.role == agent_ref:
                    assigned_agent = a_obj
                    break
            
            if not assigned_agent:
                raise ValueError(f"CRITICAL: Task '{task_name}' requires agent '{agent_ref}', but it doesn't exist.")

        task = Task(
            description=config.get('description'),
            expected_output=config.get('expected_output'),
            agent=assigned_agent
        )
        tasks.append(task)
        
    return tasks

def select_flow() -> str:
    """Выбор сценария через консоль."""
    if not CONFIG_DIR.exists():
        os.makedirs(CONFIG_DIR)
        print(f"Created config directory at {CONFIG_DIR}. Please populate it.")
        sys.exit(1)

    flows = [d.name for d in CONFIG_DIR.iterdir() if d.is_dir()]
    
    if not flows:
        print(f"No flows found in {CONFIG_DIR}")
        sys.exit(1)

    print("\n=== AI AGENCY LAUNCHER ===")
    for idx, flow in enumerate(flows, 1):
        print(f"[{idx}] {flow}")
    
    while True:
        choice = input("\nSelect Flow ID: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(flows):
            return flows[int(choice) - 1]
        print("Invalid selection.")

def main():
    try:
        # 1. Выбор сценария
        flow_name = select_flow()
        flow_path = CONFIG_DIR / flow_name
        
        print(f"\n🚀 Initializing Flow: {flow_name}")
        
        # 2. Загрузка конфигов
        agents_yaml = load_yaml(flow_path / "agents.yaml")
        tasks_yaml = load_yaml(flow_path / "tasks.yaml")
        
        # 3. Создание сущностей
        agents_map = create_agents(agents_yaml)
        tasks = create_tasks(tasks_yaml, agents_map)
        
        if not tasks:
            print("No tasks defined. Exiting.")
            sys.exit(0)

        # 4. Запуск Crew
        crew = Crew(
            agents=list(agents_map.values()), # Crew берет список агентов
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )
        
        print("\n🔥 Kicking off the Crew...")
        result = crew.kickoff()
        
        print("\n\n########################")
        print("##   FINAL RESULT     ##")
        print("########################\n")
        print(result)

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()