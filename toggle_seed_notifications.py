"""
Интерактивный скрипт для управления уведомлениями в seeds.json.
Просто запустите: python toggle_seed_notifications.py
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional


BASE_DIR = Path(__file__).resolve().parent
SEEDS_PATH = BASE_DIR / "seeds.json"


def clear_screen():
    """Очищает экран."""
    os.system('cls' if os.name == 'nt' else 'clear')


def load_seeds() -> List[Dict[str, Any]]:
    """Загружает семена из файла."""
    with open(SEEDS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_seeds(seeds: List[Dict[str, Any]]) -> None:
    """Сохраняет семена в файл."""
    with open(SEEDS_PATH, "w", encoding="utf-8") as f:
        json.dump(seeds, f, ensure_ascii=False, indent=4)
        f.write("\n")


def display_seeds(seeds: List[Dict[str, Any]]) -> None:
    """Отображает список семян с их статусами."""
    print("\n" + "=" * 70)
    print(f"{'№':<4} {'Название':<30} {'Цена':<20} {'Уведомления':<15}")
    print("=" * 70)
    
    for i, seed in enumerate(seeds, start=1):
        name = seed.get("name", "")
        price = seed.get("price") if seed.get("price") else "N/A"
        notification = seed.get("notification", False)
        status = "✓ ВКЛ" if notification else "✗ ВЫКЛ"
        
        print(f"{i:<4} {name:<30} {str(price):<20} {status:<15}")
    
    print("=" * 70)


def get_statistics(seeds: List[Dict[str, Any]]) -> Dict[str, int]:
    """Возвращает статистику по уведомлениям."""
    total = len(seeds)
    enabled = sum(1 for seed in seeds if seed.get("notification", False))
    disabled = total - enabled
    return {"total": total, "enabled": enabled, "disabled": disabled}


def toggle_seed(seeds: List[Dict[str, Any]], index: int) -> bool:
    """Переключает статус уведомления для семени по индексу."""
    if 1 <= index <= len(seeds):
        seed = seeds[index - 1]
        seed["notification"] = not bool(seed.get("notification", False))
        return True
    return False


def toggle_all(seeds: List[Dict[str, Any]], enable: Optional[bool] = None) -> int:
    """Переключает статус для всех семян."""
    changed = 0
    for seed in seeds:
        if enable is None:
            # Переключить все
            seed["notification"] = not bool(seed.get("notification", False))
            changed += 1
        else:
            # Включить или выключить все
            if seed.get("notification", False) != enable:
                seed["notification"] = enable
                changed += 1
    return changed


def select_seed(seeds: List[Dict[str, Any]]) -> Optional[int]:
    """Просит пользователя выбрать семя."""
    try:
        choice = input("\nВведите номер семени для изменения (или 0 для отмены): ").strip()
        index = int(choice)
        if index == 0:
            return None
        if 1 <= index <= len(seeds):
            return index
        else:
            print(f"Ошибка: номер должен быть от 1 до {len(seeds)}")
            return None
    except ValueError:
        print("Ошибка: введите число")
        return None


def main_menu(seeds: List[Dict[str, Any]]) -> None:
    """Главное меню программы."""
    while True:
        clear_screen()
        
        stats = get_statistics(seeds)
        print("\n" + "=" * 70)
        print("           УПРАВЛЕНИЕ УВЕДОМЛЕНИЯМИ ДЛЯ СЕМЯН")
        print("=" * 70)
        print(f"Всего семян: {stats['total']} | Включено: {stats['enabled']} | Выключено: {stats['disabled']}")
        print("=" * 70)
        
        display_seeds(seeds)
        
        print("\n" + "-" * 70)
        print("ВЫБЕРИТЕ ДЕЙСТВИЕ:")
        print("-" * 70)
        print("1. Изменить уведомления для конкретного семени")
        print("2. Включить все уведомления")
        print("3. Выключить все уведомления")
        print("4. Переключить все уведомления")
        print("5. Выход")
        print("-" * 70)
        
        choice = input("\nВаш выбор (1-5): ").strip()
        
        if choice == "1":
            clear_screen()
            display_seeds(seeds)
            index = select_seed(seeds)
            if index:
                seed = seeds[index - 1]
                old_status = "ВКЛ" if seed.get("notification", False) else "ВЫКЛ"
                toggle_seed(seeds, index)
                new_status = "ВКЛ" if seed.get("notification", False) else "ВЫКЛ"
                save_seeds(seeds)
                print(f"\n✓ Уведомления для '{seed.get('name')}' изменены: {old_status} → {new_status}")
                input("\nНажмите Enter для продолжения...")
        
        elif choice == "2":
            changed = toggle_all(seeds, enable=True)
            save_seeds(seeds)
            print(f"\n✓ Все уведомления включены (изменено: {changed})")
            input("\nНажмите Enter для продолжения...")
        
        elif choice == "3":
            changed = toggle_all(seeds, enable=False)
            save_seeds(seeds)
            print(f"\n✓ Все уведомления выключены (изменено: {changed})")
            input("\nНажмите Enter для продолжения...")
        
        elif choice == "4":
            toggle_all(seeds, enable=None)
            save_seeds(seeds)
            print(f"\n✓ Все уведомления переключены")
            input("\nНажмите Enter для продолжения...")
        
        elif choice == "5":
            print("\nДо свидания!")
            break
        
        else:
            print("\n✗ Неверный выбор. Попробуйте снова.")
            input("Нажмите Enter для продолжения...")


def main() -> None:
    """Основная функция."""
    if not SEEDS_PATH.exists():
        print(f"✗ Ошибка: файл не найден: {SEEDS_PATH}")
        return
    
    try:
        seeds = load_seeds()
        if not seeds:
            print("✗ Файл seeds.json пуст")
            return
        
        main_menu(seeds)
    
    except KeyboardInterrupt:
        print("\n\n✗ Программа прервана пользователем.")
    except Exception as e:
        print(f"\n✗ Ошибка: {e}")


if __name__ == "__main__":
    main()
