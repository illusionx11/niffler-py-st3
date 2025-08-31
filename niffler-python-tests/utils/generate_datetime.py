from datetime import datetime, timedelta, timezone
import random

def generate_random_datetime() -> str:
    """
    Генерирует случайную дату и время в формате 'YYYY-MM-DDThh:mm:ss.000Z' до текущей даты.
    
    Returns:
        str: Случайная дата и время в формате, например, '2024-06-01T00:00:00.000Z'.
    """
    # Текущая дата и время в UTC
    now = datetime.now(timezone.utc)
    
    # Начальная дата (например, 1 января 2000 года)
    start_date = datetime(2000, 1, 1, tzinfo=timezone.utc)
    
    # Вычисляем разницу в днях
    delta_days = (now - start_date).days
    
    # Генерируем случайное количество дней от start_date
    random_days = random.randint(0, delta_days)
    
    # Генерируем случайное время (секунды в сутках)
    random_seconds = random.randint(0, 86400)  # 86400 секунд = 24 часа
    
    # Создаем случайный datetime
    random_dt = start_date + timedelta(days=random_days, seconds=random_seconds)
    
    # Форматируем в нужный формат
    return random_dt.strftime("%Y-%m-%dT%H:%M:%S.000Z")

def format_date(date: str) -> str:
    """
    Форматирует дату в формате '2025-08-31T00:00:00.000Z' в формат 'Aug 31, 2025'.
    """
    return datetime.fromisoformat(date).strftime("%b %d, %Y")