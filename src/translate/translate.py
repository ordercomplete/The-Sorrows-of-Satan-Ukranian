"""
Скрипт для перекладу розпізнаного тексту з російської на українську.
Підтримує кілька методів перекладу.
"""

import os
import json
from pathlib import Path

def translate_with_prompt(text, context="Переклади з російської на українську мову. Збережи формат та структуру тексту."):
    """
    Переклад тексту через API (наприклад, OpenAI, Yandex, Google).
    
    Args:
        text: Текст для перекладу
        context: Контекст для перекладача
    
    Returns:
        Перекладений текст
    """
    # TODO: Реалізувати інтеграцію з API перекладу
    # Поки що повертаємо оригінал
    print(f"[ПЕРЕКЛАД] Текст для перекладу ({len(text)} символів):")
    print("-" * 40)
    print(text)
    print("-" * 40)
    return text  # Поки що повертаємо оригінал

def parallel_text(original_lines, translated_lines):
    """
    Створює паралельний текст (оригінал + переклад).
    
    Args:
        original_lines: Список рядків оригіналу
        translated_lines: Список рядків перекладу
    
    Returns:
        Сформований паралельний текст
    """
    result = []
    for i, (orig, trans) in enumerate(zip(original_lines, translated_lines), 1):
        result.append(f"--- Рядок {i} ---")
        result.append(f"[Оригінал]: {orig}")
        result.append(f"[Переклад]: {trans}")
        result.append("")
    return "\n".join(result)

def save_translation(original_text, translated_text, output_file):
    """
    Зберігає переклад у файл.
    
    Args:
        original_text: Оригінальний текст
        translated_text: Перекладений текст
        output_file: Шлях до файлу виходу
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Переклад\n\n")
        f.write("## Оригінал\n\n")
        f.write(original_text + "\n\n")
        f.write("---\n\n")
        f.write("## Переклад\n\n")
        f.write(translated_text + "\n\n")
    print(f"✓ Переклад збережено: {output_file}")

def process_translation(input_file, output_file=None):
    """
    Обробляє переклад файлу.
    
    Args:
        input_file: Шлях до файлу з розпізнаним текстом
        output_file: Шлях до файлу виходу (опціонально)
    """
    # Читаємо оригінал
    with open(input_file, 'r', encoding='utf-8') as f:
        original_text = f.read()
    
    original_lines = original_text.strip().split('\n')
    
    # TODO: Тут буде виклик API перекладу
    # translated_lines = translate_lines(original_lines)
    translated_lines = original_lines  # Поки що копія
    
    translated_text = '\n'.join(translated_lines)
    
    if not output_file:
        base_name = Path(input_file).stem
        output_file = f"output/translated/{base_name}_translated.txt"
    
    save_translation(original_text, translated_text, output_file)
    
    return translated_text

if __name__ == '__main__':
    project_root = Path(__file__).parent.parent.parent
    recognized_folder = project_root / 'output' / 'recognized'
    
    if recognized_folder.exists():
        txt_files = list(recognized_folder.glob('*.txt'))
        if txt_files:
            for txt_file in txt_files:
                print(f"Обробка: {txt_file}")
                process_translation(str(txt_file))
        else:
            print(f"Не знайдено файлів у {recognized_folder}")
    else:
        print(f"Папка не існує: {recognized_folder}")
