# Масиви символів для англійської та української розкладок (включаючи Shift-символи)
EN_LAYOUT = "qwertyuiop[]asdfghjkl;'zxcvbnm,./QWERTYUIOP{}ASDFGHJKL:\"ZXCVBNM<>?"
UK_LAYOUT = "йцукенгшщзхїфівапролджєячсмитьбю.ЙЦУКЕНГШЩЗХЇФІВАПРОЛДЖЄЯЧСМИТЬБЮ,"

# Створення таблиць трансляції для швидкої заміни
EN_TO_UK_MAP = str.maketrans(EN_LAYOUT, UK_LAYOUT)
UK_TO_EN_MAP = str.maketrans(UK_LAYOUT, EN_LAYOUT)

def decode_text(text: str, to_ukrainian: bool = True) -> str:
    """
    Декодує текст, набраний не в тій розкладці.
    :param text: Рядок тексту для конвертації
    :param to_ukrainian: True для EN -> UK (за замовчуванням), False для UK -> EN
    """
    if to_ukrainian:
        return text.translate(EN_TO_UK_MAP)
    return text.translate(UK_TO_EN_MAP)

# --- Приклади використання ---
if __name__ == "__main__":
    # 1. Конвертація з англійської на українську (EN -> UK)
    mistake_en = "yfdgfrb, ghbdtn! Rjve gjnhj,ty gfqnjy-crhbgn?"
    fixed_uk = decode_text(mistake_en, to_ukrainian=True)
    print(f"Оригінал (EN): {mistake_en}")
    print(f"Виправлено (UK): {fixed_uk}\n")

    # 2. Конвертація з української на англійську (UK -> EN)
    mistake_uk = "іьшіед"
    fixed_en = decode_text(mistake_uk, to_ukrainian=False)
    print(f"Оригінал (UK): {mistake_uk}")
    print(f"Виправлено (EN): {fixed_en}")
