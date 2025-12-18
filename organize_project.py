import os
import shutil
from pathlib import Path

# Определяем корень (там где лежит этот скрипт)
ROOT = Path(__file__).parent.absolute()
INNER_ROOT = ROOT / "AI_Agency" # Та самая внутренняя папка
PROJECTS_ROOT = ROOT / "Projects"
GELION_ROOT = PROJECTS_ROOT / "Gelion"

# Создаем новую структуру Gelion
DIRS = ["scripts", "configs", "data", "output"]
for d in DIRS:
    (GELION_ROOT / d).mkdir(parents=True, exist_ok=True)

print(f"📂 Целевая структура создана в {GELION_ROOT}")

# ФУНКЦИЯ ПЕРЕМЕЩЕНИЯ
def move_file(src, dest_folder):
    if src.exists() and src.is_file():
        shutil.move(str(src), str(dest_folder / src.name))
        print(f"✅ Перемещен: {src.name} -> {dest_folder.name}")

# 1. СПАСАЕМ ФАЙЛЫ ИЗ ВНУТРЕННЕЙ AI_Agency (Выносим в корень)
if INNER_ROOT.exists():
    print("--- Распаковка матрешки AI_Agency ---")
    # Переносим .env
    move_file(INNER_ROOT / ".env", ROOT)
    
    # Переносим Agency_Brain
    if (INNER_ROOT / "Agency_Brain").exists():
        target = ROOT / "Agency_Brain"
        if not target.exists():
            shutil.move(str(INNER_ROOT / "Agency_Brain"), str(ROOT))
            print("✅ Agency_Brain вынесен в корень")
        else:
            print("ℹ️ Agency_Brain уже есть в корне (пропуск)")

    # Переносим Projects из внутренней папки во внешнюю
    inner_proj = INNER_ROOT / "Projects"
    if inner_proj.exists():
        for item in inner_proj.iterdir():
            if item.is_dir():
                # Если папка уже есть снаружи, сливаем контент
                dest = PROJECTS_ROOT / item.name
                if not dest.exists():
                    shutil.move(str(item), str(PROJECTS_ROOT))
                    print(f"✅ Папка {item.name} вынесена в Projects")

# 2. СОБИРАЕМ ВСЁ В GELION
print("--- Сборка проекта Gelion ---")

# Список старых папок, откуда забираем файлы
OLD_FOLDERS = [
    PROJECTS_ROOT / "AirClub",
    PROJECTS_ROOT / "AirClub_Strategy",
    PROJECTS_ROOT / "Gelion Info"
]

for folder in OLD_FOLDERS:
    if folder.exists():
        print(f"🧹 Разбираем {folder.name}...")
        # Перебираем все файлы в старой папке
        for item in folder.rglob("*"): # Рекурсивно
            if item.is_file():
                # Логика сортировки
                if item.suffix == ".py":
                    shutil.move(str(item), str(GELION_ROOT / "scripts" / item.name))
                elif item.suffix == ".md":
                    if "role_" in item.name:
                        shutil.move(str(item), str(GELION_ROOT / "configs" / item.name))
                    elif "output" in str(item.parent) or "report" in item.name.lower():
                        shutil.move(str(item), str(GELION_ROOT / "output" / item.name))
                    else:
                        shutil.move(str(item), str(GELION_ROOT / "data" / item.name))
                else:
                    # Остальное кидаем в data
                    shutil.move(str(item), str(GELION_ROOT / "data" / item.name))
        
        # Удаляем пустую старую папку
        try:
            shutil.rmtree(str(folder))
            print(f"🗑 Удалена старая папка {folder.name}")
        except:
            print(f"⚠️ Не удалось удалить {folder.name}, удали вручную")

print("\n🎉 ГОТОВО! Проект структурирован.")
print("Теперь твой рабочий файл: Projects/Gelion/scripts/run_pitch.py (или similar)")