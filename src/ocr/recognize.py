"""
Скрипт для розпізнавання тексту на зображеннях за допомогою EasyOCR.
Підтримує російську та українську мови.
"""

import easyocr
import cv2
import numpy as np
import os
import sys
from pathlib import Path

def preprocess_image(image_path):
    """
    Попередня обробка зображення для покращення якості OCR.
    
    Кроки:
    1. Завантаження та конвертація в grayscale
    2. Збільшення розміру (2x) для кращого розпізнавання дрібного тексту
    3. Застосування fastNlMeansDenoising для зменшення шуму
    4. Застосування CLAHE для підвищення контрасту
    5. Повернення grayscale зображення (EasyOCR краще працює з grayscale ніж з бінарними)
    
    Args:
        image_path: Шлях до вхідного зображення
    
    Returns:
        Оброблене зображення як numpy array
    """
    # Завантажуємо зображення
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Не вдалося завантажити зображення: {image_path}")
    
    # Збільшуємо розмір в 2 рази для кращого розпізнавання
    h, w = img.shape[:2]
    if min(h, w) < 1000:  # Збільшуємо тільки якщо зображення маленьке
        new_w, new_h = w * 2, h * 2
        img = cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
    
    # Конвертуємо в grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # fastNlMeansDenoising для зменшення шуму (краще за Gaussian blur)
    denoised = cv2.fastNlMeansDenoising(gray, h=10)
    
    # CLAHE (Contrast Limited Adaptive Histogram Equalization)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)
    
    print(f"  Попередня обробка: {w}x{h} → {enhanced.shape[1]}x{enhanced.shape[0]}")
    print(f"  Методи: resize(2x) → denoise → CLAHE")
    
    return enhanced

def recognize_image(image_path, languages=['ru', 'uk'], detail=1):
    """
    Розпізнає текст на зображенні.
    
    Args:
        image_path: Шлях до зображення
        languages: Мови для розпізнавання (російська, українська)
        detail: Деталізація результату (0 = тільки текст, 1 = з координатами)
    
    Returns:
        Список розпізнаних рядків
    """
    print(f"Завантаження моделі OCR...")
    reader = easyocr.Reader(languages, gpu=False)  # gpu=True якщо є NVIDIA GPU
    
    print(f"Обробка зображення: {image_path}")
    
    # Попередня обробка зображення
    processed_img = preprocess_image(image_path)
    
    # Зберігаємо оброблене зображення в окрему папку temp
    temp_dir = Path(__file__).resolve().parent.parent.parent / 'temp'
    temp_dir.mkdir(exist_ok=True)
    temp_path = str(temp_dir / f"{Path(image_path).stem}_processed.jpg")
    cv2.imwrite(temp_path, processed_img)
    print(f"  Збережено оброблене зображення: {temp_path}")
    
    # Розпізнаємо на обробленому зображенні
    result = reader.readtext(temp_path, detail=detail, paragraph=False, contrast_ths=0.5)
    
    # Не видаляємо — залишаємо для діагностики
    
    if detail == 0:
        return result
    else:
        # Повертаємо тільки текст
        return [item[1] for item in result]

def process_folder(input_folder, output_folder='output/recognized'):
    """
    Обробляє всі зображення в папці.
    
    Args:
        input_folder: Папка з вхідними зображеннями
        output_folder: Папка для збереження результатів
    """
    # Створюємо папку для результатів
    os.makedirs(output_folder, exist_ok=True)
    
    # Отримуємо список зображень
    image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp']
    images = [f for f in os.listdir(input_folder) 
              if any(f.lower().endswith(ext) for ext in image_extensions)]
    
    if not images:
        print(f"Не знайдено зображень у папці: {input_folder}")
        return
    
    print(f"Знайдено {len(images)} зображень для обробки")
    
    # Обробляємо кожне зображення
    for image in images:
        image_path = os.path.join(input_folder, image)
        print(f"\n{'='*60}")
        print(f"Обробка: {image}")
        print(f"{'='*60}")
        
        try:
            text = recognize_image(image_path)
            
            # Зберігаємо результат
            base_name = os.path.splitext(image)[0]
            output_file = os.path.join(output_folder, f"{base_name}_recognized.txt")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                for line in text:
                    f.write(line + '\n')
            
            print(f"✓ Результат збережено: {output_file}")
            print(f"\nРозпізнаний текст ({len(text)} рядків):")
            print('-' * 40)
            for i, line in enumerate(text, 1):
                print(f"{i:3d}. {line}")
            print('-' * 40)
            
        except Exception as e:
            print(f"✗ Помилка обробки {image}: {e}")

if __name__ == '__main__':
    # Визначаємо шляхи
    project_root = Path(__file__).parent.parent.parent
    input_folder = project_root / 'input'
    
    # Якщо є аргументи командного рядка — використовуємо їх
    if len(sys.argv) > 1:
        input_folder = Path(sys.argv[1])
    
    output_folder = project_root / 'output' / 'recognized'
    
    print(f"Вхідна папка: {input_folder}")
    print(f"Папка результатів: {output_folder}")
    
    process_folder(str(input_folder), str(output_folder))
