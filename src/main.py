#!/usr/bin/env python3
import sys
import os
import asyncio
import signal
import yaml
import datetime
from pathlib import Path
from typing import Dict, List, Any
from dotenv import load_dotenv

# --- WINDOWS PATCHES ---
if sys.platform.startswith('win'):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    unix_signals = ['SIGABRT', 'SIGALRM', 'SIGBUS', 'SIGCHLD', 'SIGCONT', 'SIGFPE', 'SIGHUP', 'SIGILL', 'SIGINT', 'SIGIO', 'SIGIOT', 'SIGKILL', 'SIGPIPE', 'SIGPOLL', 'SIGPROF', 'SIGPWR', 'SIGQUIT', 'SIGSEGV', 'SIGSTOP', 'SIGSYS', 'SIGTERM', 'SIGTRAP', 'SIGTSTP', 'SIGTTIN', 'SIGTTOU', 'SIGURG', 'SIGUSR1', 'SIGUSR2', 'SIGVTALRM', 'SIGWINCH', 'SIGXCPU', 'SIGXFSZ']
    for name in unix_signals:
        if not hasattr(signal, name):
            try: setattr(signal, name, getattr(signal, 'SIGTERM', 1))
            except AttributeError: setattr(signal, name, 1)

from crewai import Agent, Task, Crew, Process, LLM

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "config"
OUTPUT_DIR = BASE_DIR / "outputs"

def load_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")
    with open(path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}

def get_llm(model_name: str):
    if not model_name: return None
    print(f"    ⚙️ Configuring LLM: {model_name}")
    
    api_key = None
    if "gemini" in model_name: api_key = os.getenv("GEMINI_API_KEY")
    elif "groq" in model_name: api_key = os.getenv("GROQ_API_KEY")
    elif "deepseek" in model_name: api_key = os.getenv("DEEPSEEK_API_KEY")
    elif "gpt" in model_name: api_key = os.getenv("OPENAI_API_KEY")
    
    return LLM(model=model_name, api_key=api_key)

def create_agents(agents_config: Dict[str, Any]) -> Dict[str, Agent]:
    agents_map = {}
    iterator = agents_config.items() if isinstance(agents_config, dict) else {item.get('role', f'a{i}'): item for i, item in enumerate(agents_config)}.items()

    for key, config in iterator:
        if not config: continue
        agent = Agent(
            role=config.get('role'),
            goal=config.get('goal'),
            backstory=config.get('backstory'),
            verbose=config.get('verbose', True),
            allow_delegation=False,
            llm=get_llm(config.get('llm')),
            tools=[]
        )
        agents_map[key] = agent
        if 'name' in config: agents_map[config['name']] = agent
    return agents_map

def create_tasks(tasks_config: Dict[str, Any], agents_map: Dict[str, Agent]) -> List[Task]:
    tasks_objects = []
    tasks_registry = {}
    
    raw_tasks = []
    if isinstance(tasks_config, list):
        for i, item in enumerate(tasks_config): raw_tasks.append((f"task_{i}", item))
    else:
        for key, item in tasks_config.items(): raw_tasks.append((key, item))

    for key, config in raw_tasks:
        agent_ref = config.get('agent')
        assigned_agent = agents_map.get(agent_ref)
        if not assigned_agent:
             for a_obj in agents_map.values():
                if a_obj.role == agent_ref:
                    assigned_agent = a_obj
                    break
        if not assigned_agent:
            print(f"CRITICAL: Agent '{agent_ref}' not found")
            sys.exit(1)

        task = Task(
            name=config.get('name', key),
            description=config.get('description'), # CrewAI сам подставит {variables} при kickoff
            expected_output=config.get('expected_output'),
            agent=assigned_agent,
            async_execution=config.get('async_execution', False)
        )
        tasks_objects.append(task)
        tasks_registry[key] = task
        if config.get('name'): tasks_registry[config.get('name')] = task

    for i, (key, config) in enumerate(raw_tasks):
        context_names = config.get('context', [])
        if context_names:
            context_tasks = [tasks_registry[c] for c in context_names if c in tasks_registry]
            if context_tasks: tasks_objects[i].context = context_tasks

    return tasks_objects

def save_result(flow_name: str, result: str):
    target_dir = OUTPUT_DIR / flow_name
    target_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filepath = target_dir / f"report_{timestamp}.md"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(str(result))
    print(f"\n✅ REPORT SAVED TO: {filepath}")

def select_flow() -> str:
    if not CONFIG_DIR.exists(): os.makedirs(CONFIG_DIR); sys.exit(1)
    flows = [d.name for d in CONFIG_DIR.iterdir() if d.is_dir()]
    print("\n=== AI AGENCY LAUNCHER ===")
    for idx, flow in enumerate(flows, 1): print(f"[{idx}] {flow}")
    while True:
        try:
            choice = input("\nSelect Flow ID: ").strip()
            if choice.isdigit() and 1 <= int(choice) <= len(flows): return flows[int(choice) - 1]
        except KeyboardInterrupt: sys.exit(0)

def get_user_input(flow_name: str) -> Dict[str, str]:
    """Запрашивает входные данные в зависимости от сценария."""
    print(f"\n📝 ВВОД ДАННЫХ ДЛЯ: {flow_name}")
    print("Введи описание бизнеса и проблемы (можно многострочный текст).")
    print("Нажми Enter, затем Ctrl+Z (Windows) или Ctrl+D (Linux) для завершения ввода.\n")
    
    # Чтение многострочного ввода
    lines = []
    try:
        while True:
            line = input()
            lines.append(line)
    except EOFError:
        pass
    
    text = "\n".join(lines)
    
    if not text.strip():
        print("❌ Ошибка: Пустой ввод. Использую тестовые данные.")
        return {"business_description": "Тестовый завод по производству бетона. Теряем заявки."}
        
    return {"business_description": text}

def main():
    try:
        flow_name = select_flow()
        flow_path = CONFIG_DIR / flow_name
        
        print(f"\n🚀 Initializing Flow: {flow_name}")
        agents_yaml = load_yaml(flow_path / "agents.yaml")
        tasks_yaml = load_yaml(flow_path / "tasks.yaml")
        
        agents_map = create_agents(agents_yaml)
        tasks = create_tasks(tasks_yaml, agents_map)
        
        # 1. Получаем данные от пользователя
        inputs = get_user_input(flow_name)
        
        crew = Crew(
            agents=list(agents_map.values()),
            tasks=tasks,
            process=Process.sequential,
            verbose=True
        )
        
        print("\n🔥 Kicking off the Crew...")
        # 2. Передаем данные в inputs (CrewAI сам заменит {business_description} в задачах)
        result = crew.kickoff(inputs=inputs)
        
        save_result(flow_name, result)

    except Exception as e:
        print(f"\n❌ FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()