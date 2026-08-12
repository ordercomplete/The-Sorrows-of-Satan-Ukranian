"""
Простий EasyOCR — без обробки, тільки розпізнавання.
Мови: російська + українська.
Вивід: побуквенний дослівний текст.
"""

import easyocr
import sys
from pathlib import Path


def main():
    if len(sys.argv) < 2:
        print("Використання: python recognize_simple.py <шлях_до_зображення>")
        print("Приклад: python recognize_simple.py input/002-003_pages.jpg")
        sys.exit(1)

    image_path = Path(sys.argv[1])
    if not image_path.exists():
        print(f"Файл не знайдено: {image_path}")
        sys.exit(1)

    output_dir = Path(__file__).resolve().parent.parent.parent / "output" / "recognized"
    output_dir.mkdir(parents=True, exist_ok=True)

    base_name = image_path.stem
    output_file = output_dir / f"{base_name}_easyocr.txt"

    print(f"Завантаження моделі EasyOCR (ru + uk)...")
    # Додаємо українську — рукописний текст може містити українські літери
    reader = easyocr.Reader(lang_list=['ru', 'uk'], gpu=False)

    print(f"\nРозпізнавання: {image_path}")
    # paragraph=True — зберігає рядки
    # text_threshold=0.65 — вищий поріг щоб відсіяти шум
    # beamWidth=10 — ширший пучок для кращого розпізнавання рукопису
    # decoder='beamsearch' — пучковий пошук для складнішого тексту
    result = reader.readtext(
        str(image_path),
        detail=0,
        paragraph=True,
        text_threshold=0.65,
        beamWidth=10,
        decoder='beamsearch',
    )

    text = "\n".join(result)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(text)

    print(f"\n✅ Результат збережено: {output_file}")
    print(f"\n--- Текст ---\n{text}\n--- Кінець ---")


if __name__ == "__main__":
    main()
