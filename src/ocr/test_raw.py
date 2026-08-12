"""
Тест: OCR без попередньої обробки vs з обробкою.
Порівнюємо якість розпізнавання на оригіналі та обробленому зображенні.
"""

import easyocr
import cv2
import sys
from pathlib import Path

def recognize_raw(image_path, languages=['ru', 'uk']):
    """OCR БЕЗ будь-якої попередньої обробки."""
    print(f"\n{'='*60}")
    print(f"📷 OCR НА ОРИГІНАЛІ (без обробки)")
    print(f"{'='*60}")
    
    reader = easyocr.Reader(languages, gpu=False)
    result = reader.readtext(image_path, detail=1, paragraph=False, contrast_ths=0.5)
    
    texts = [item[1] for item in result]
    print(f"Знайдено {len(texts)} рядків:")
    print('-' * 50)
    for i, t in enumerate(texts, 1):
        print(f"{i:3d}. {t}")
    print('-' * 50)
    
    # Зберігаємо для порівняння
    output_path = Path(__file__).parent.parent.parent / 'output' / 'recognized' / 'page_002_raw.txt'
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in texts:
            f.write(line + '\n')
    print(f"Збережено: {output_path}")
    
    return texts

def recognize_processed(image_path, languages=['ru', 'uk']):
    """OCR З попередньою обробкою."""
    print(f"\n{'='*60}")
    print(f"🖼️  OCR НА ОБРОБЛЕНОМУ (resize → denoise → CLAHE)")
    print(f"{'='*60}")
    
    # Завантажуємо та обробляємо
    img = cv2.imread(image_path)
    h, w = img.shape[:2]
    
    if min(h, w) < 1000:
        new_w, new_h = w * 2, h * 2
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)
    
    # Зберігаємо оброблене
    temp_dir = Path(__file__).parent.parent.parent / 'temp'
    temp_dir.mkdir(exist_ok=True)
    temp_path = str(temp_dir / f"{Path(image_path).stem}_processed2.jpg")
    cv2.imwrite(temp_path, enhanced)
    
    reader = easyocr.Reader(languages, gpu=False)
    result = reader.readtext(temp_path, detail=1, paragraph=False, contrast_ths=0.5)
    
    texts = [item[1] for item in result]
    print(f"Знайдено {len(texts)} рядків:")
    print('-' * 50)
    for i, t in enumerate(texts, 1):
        print(f"{i:3d}. {t}")
    print('-' * 50)
    
    output_path = Path(__file__).parent.parent.parent / 'output' / 'recognized' / 'page_002_processed.txt'
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in texts:
            f.write(line + '\n')
    print(f"Збережено: {output_path}")
    
    return texts

if __name__ == '__main__':
    project_root = Path(__file__).parent.parent.parent
    image_path = project_root / 'input' / '002-003_pages.jpg'
    
    if not image_path.exists():
        print(f"Файл не знайдено: {image_path}")
        sys.exit(1)
    
    # Тестуємо обидва варіанти
    raw_texts = recognize_raw(str(image_path))
    processed_texts = recognize_processed(str(image_path))
    
    print(f"\n{'='*60}")
    print(f"📊 ПІДСУМОК")
    print(f"{'='*60}")
    print(f"Оригінал: {len(raw_texts)} рядків")
    print(f"Оброблене: {len(processed_texts)} рядків")
    print(f"\nПеревірте файли:")
    print(f"  output/recognized/page_002_raw.txt")
    print(f"  output/recognized/page_002_processed.txt")
