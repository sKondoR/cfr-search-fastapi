import re
from typing import Union

def extract_link_id(href: str) -> Union[str, None]:
    """
    Извлекает ID из ссылки на соревнование.
    
    Args:
        href: URL-адрес ссылки
        
    Returns:
        ID ссылки или None, если не удалось извлечь
    """
    if not href:
        return None
    
    if href.startswith("/competitions/") and href.endswith("/"):
        href = href[14:-1]  # Убираем "/competitions/" (14 символов) и "/"
    
    return href

def extract_year_from_link(href: str) -> str:
    """
    Извлекает год из ссылки.
    
    Args:
        href: URL-адрес ссылки
        
    Returns:
        Год в формате YYYY или пустая строка, если не удалось извлечь
    """
    if not href:
        return ""
    
    # Добавляем отладку для отладки
    print(f"DEBUG: extract_year_from_link called with href: {href}")
    
    # Ищем первые 2 цифры в ссылке
    year_match = re.search(r"\d{2}", href)
    if year_match:
        year_str = year_match.group(0)
        print(f"DEBUG: Found year_str: {year_str}")
        # Проверяем, что это валидный год (2000-2099)
        year_num = int(year_str)
        if 0 <= year_num <= 99:
            result = f"20{year_str}"
            print(f"DEBUG: Returning year: {result}")
            return result
    print("DEBUG: No valid year found")
    return ""

# Добавляем отладку для отладки
