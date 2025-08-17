"""Парсер SOAP ответов для niffler-userdata сервиса"""

import xml.etree.ElementTree as ET
import logging
from typing import List, Dict, Optional

def parse_soap_response(response_text: str) -> ET.Element:
    """Базовый парсер SOAP ответа"""
    try:
        root = ET.fromstring(response_text)
        return root
    except ET.ParseError as e:
        logging.error(f"Ошибка парсинга XML: {e}")
        logging.error(f"XML ответ: {response_text}")
        raise

def check_current_user_result_operation(response_text: str) -> Dict:
    """Парсинг ответа currentUser"""
    root = parse_soap_response(response_text)
    
    # Найти элемент user в ответе
    user_element = root.find(".//{niffler-userdata}user")
    
    if user_element is None:
        logging.warning(f"Элемент user не найден в ответе: {response_text}")
        return {}
    
    user_data = {}
    for child in user_element:
        tag_name = child.tag.replace("{niffler-userdata}", "")
        user_data[tag_name] = child.text
    
    if 'photoSmall' in user_data:
        user_data['photo_small'] = user_data.pop('photoSmall')
    
    if 'fullName' in user_data:
        user_data['full_name'] = user_data.pop('fullName')
    
    logging.info(f"Распарсен пользователь: {user_data}")
    return user_data

def check_users_result_operation(response_text: str) -> List[Dict]:
    """Парсинг ответа со списком пользователей (allUsers, friends)"""
    root = parse_soap_response(response_text)
    
    # Найти все элементы user в ответе
    user_elements = root.findall(".//{niffler-userdata}user")
    
    users = []
    for user_element in user_elements:
        user_data = {}
        for child in user_element:
            tag_name = child.tag.replace("{niffler-userdata}", "")
            user_data[tag_name] = child.text
        
        # Преобразуем photoSmall в photo_small для соответствия модели
        if 'photoSmall' in user_data:
            user_data['photo_small'] = user_data.pop('photoSmall')
        
        # Преобразуем fullName в full_name для соответствия модели  
        if 'fullName' in user_data:
            user_data['full_name'] = user_data.pop('fullName')
        
        users.append(user_data)
    
    logging.info(f"Распарсено пользователей: {len(users)}")
    return users

def check_users_page_result_operation(response_text: str) -> Dict:
    """Парсинг ответа с пагинацией (allUsersPage, friendsPage)"""
    root = parse_soap_response(response_text)
    
    # Парсим пользователей
    users = check_users_result_operation(response_text)
    
    # Ищем элементы пагинации
    def find_text(tag_name):
        element = root.find(f".//{{niffler-userdata}}{tag_name}")
        return int(element.text) if element is not None and element.text else 0
    
    page_data = {
        'users': users,
        'size': find_text('size'),
        'number': find_text('number'), 
        'totalElements': find_text('totalElements'),
        'totalPages': find_text('totalPages')
    }
    
    logging.info(f"Распарсена страница: размер={page_data['size']}, номер={page_data['number']}")
    return page_data

def check_soap_fault(response_text: str) -> Optional[str]:
    """Проверка на SOAP fault"""
    root = parse_soap_response(response_text)
    fault_element = root.find(".//{http://schemas.xmlsoap.org/soap/envelope/}Fault")
    
    if fault_element is not None:
        fault_string = fault_element.find("faultstring")
        if fault_string is not None:
            return fault_string.text
        return "Unknown SOAP fault"
    
    return None