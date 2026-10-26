"""
Тестування TrOCR для рукописного тексту.
Модель: microsoft/trOCR-base-handwritten
"""

import sys
import os
from pathlib import Path

# Додаємо корінь проекту в path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_trocr(image_path: str, output_path: str = None):
    """Розпізнавання тексту через TrOCR."""
    
    print("=" * 60)
    print("TrOCR тестування")
    print("=" * 60)
    print(f"Зображення: {image_path}")
    print(f"Модель: microsoft/trOCR-base-handwritten")
    print(f"Режим: CPU (повільно, але працює)")
    print("-" * 60)
    
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel, GPT2TokenizerFast
    from PIL import Image
    
    # Завантажуємо модель
    print("\n⏳ Завантаження моделі (перший раз — буде довго)...")
    
    # Явно створюємо tokenizer для уникнення проблем з backend detection в transformers 5.x
    print("  ⏳ Завантаження GPT2TokenizerFast...")
    tokenizer = GPT2TokenizerFast.from_pretrained('microsoft/trOCR-base-handwritten')
    print(f"  ✅ Tokenizer завантажений")
    
    # Створюємо image_processor вручну
    from transformers import AutoImageProcessor
    print("  ⏳ Завантаження AutoImageProcessor...")
    image_processor = AutoImageProcessor.from_pretrained('microsoft/trOCR-base-handwritten')
    print(f"  ✅ ImageProcessor завантажений")
    
    # Вручну створюємо TrOCRProcessor з готовими компонентами
    print("  ⏳ Ініціалізація TrOCRProcessor...")
    processor = TrOCRProcessor(image_processor=image_processor, tokenizer=tokenizer)
    model = VisionEncoderDecoderModel.from_pretrained('microsoft/trOCR-base-handwritten')
    
    # Використовуємо CPU
    device = "cpu"
    model.to(device)
    print(f"✅ Модель завантажена. Використовуємо: {device.upper()}")
    
    # Розпізнавання
    print("\n⏳ Розпізнавання тексту...")
    image = Image.open(image_path).convert("RGB")
    
    pixel_values = processor(images=image, return_tensors="pt").pixel_values
    pixel_values = pixel_values.to(device)
    
    # Використовуємо beam search для кращої якості
    generated_ids = model.generate(
        pixel_values=pixel_values,
        max_new_tokens=4096,
        num_beams=5,
        early_stopping=True,
        no_repeat_ngram_size=3,
    )
    generated_text = processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
    
    print("\n" + "=" * 60)
    print("РЕЗУЛЬТАТ:")
    print("=" * 60)
    print(generated_text)
    print("=" * 60)
    
    # Зберігаємо результат
    if output_path:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(generated_text)
        print(f"\n✅ Результат збережено: {output_path}")
    
    return generated_text


if __name__ == "__main__":
    # Вхідне зображення
    input_dir = project_root / "input"
    output_dir = project_root / "output" / "recognized"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Тестуємо на 002-003_pages.jpg
    image_path = input_dir / "002-003_pages.jpg"
    
    if not image_path.exists():
        print(f"❌ Файл не знайдено: {image_path}")
        sys.exit(1)
    
    output_path = output_dir / "page_002_trocr.txt"
    test_trocr(str(image_path), str(output_path))
