import allure
import logging
from typing import List, Optional, Dict
from models.soap import PageInfo, SoapUser
from models.config import ServerEnvs, ClientEnvs
from utils.sessions import SoapSession
from utils.soap_templates import (
    current_user_xml, 
    all_users_xml, 
    all_users_page_xml,
    friends_xml,
    friends_page_xml,
    send_invitation_xml,
    accept_invitation_xml,
    decline_invitation_xml,
    remove_friend_xml,
    update_user_xml
)
from utils.soap_parser import (
    check_current_user_result_operation,
    check_users_result_operation, 
    check_users_page_result_operation,
    check_soap_fault
)

class SoapClient:
    """Raw XML SOAP клиент для работы с сервисом niffler-userdata"""
    
    def __init__(self, server_envs: ServerEnvs, client_envs: ClientEnvs):
        self.server_envs = server_envs
        self.client_envs = client_envs
        self.session = SoapSession(base_url=server_envs.userdata_url)
    
    def _execute_soap_request(self, xml_data: str, operation_name: str) -> tuple[str, int]:
        """Выполнение SOAP запроса с обработкой ошибок"""
        try:
            response = self.session.soap_request(xml_data)
            if operation_name != "removeFriend":
                fault = check_soap_fault(response.text)
                if fault:
                    return fault, response.status_code
        
            return response.text, response.status_code
            
        except Exception as e:
            logging.error(f"Ошибка SOAP операции {operation_name}: {str(e)}", exc_info=True)
            raise
    
    @allure.step("SOAP Получение текущего пользователя")
    def get_current_user(self, username: str) -> tuple[Dict, int]:
        """Получение текущего пользователя по username"""
        xml_data = current_user_xml(username)
        response_text, status_code = self._execute_soap_request(xml_data, "currentUser")
        
        user_data = check_current_user_result_operation(response_text)
        logging.info(f"Получен пользователь: {username}")
        return user_data, status_code
    
    @allure.step("SOAP Обновление пользователя")
    def update_user(self, user_data: SoapUser) -> tuple[Dict, int]:
        """Обновление данных пользователя"""
        xml_data = update_user_xml(user_data)
        response_text, status_code = self._execute_soap_request(xml_data, "updateUser")
        
        updated_user = check_current_user_result_operation(response_text)
        logging.info(f"Пользователь {user_data.username} обновлен")
        return updated_user
    
    @allure.step("SOAP Получение всех пользователей")
    def get_all_users(self, username: str, search_query: Optional[str] = None) -> tuple[List[Dict], int]:
        """Получение списка всех пользователей"""
        xml_data = all_users_xml(username, search_query)
        response_text, status_code = self._execute_soap_request(xml_data, "allUsers")
        
        users = check_users_result_operation(response_text)
        logging.info(f"Получен список пользователей. Найдено: {len(users)}\n{users}")
        return users, status_code
    
    @allure.step("SOAP Получение всех пользователей с пагинацией")
    def get_all_users_page(self, username: str, page_info: PageInfo, search_query: Optional[str] = None) -> tuple[Dict, int]:
        """Получение списка пользователей с пагинацией"""
        xml_data = all_users_page_xml(username, page_info, search_query)
        response_text, status_code = self._execute_soap_request(xml_data, "allUsersPage")
        logging.info(f"Получена страница пользователей. Страница: {page_info.page}, размер: {page_info.size}")
        if status_code == 500:
            return response_text, status_code
        page_data = check_users_page_result_operation(response_text)
        return page_data, status_code
    
    @allure.step("SOAP Получение друзей")
    def get_friends(self, username: str, search_query: Optional[str] = None) -> tuple[List[Dict], int]:
        """Получение списка друзей пользователя"""
        xml_data = friends_xml(username, search_query)
        response_text, status_code = self._execute_soap_request(xml_data, "friends")
        
        friends = check_users_result_operation(response_text)
        logging.info(f"Получен список друзей для {username}. Найдено: {len(friends)}")
        return friends, status_code
    
    @allure.step("SOAP Получение друзей с пагинацией")
    def get_friends_page(self, username: str, page_info: PageInfo, search_query: Optional[str] = None) -> tuple[Dict, int]:
        """Получение списка друзей с пагинацией"""
        xml_data = friends_page_xml(username, page_info, search_query)
        response_text, status_code = self._execute_soap_request(xml_data, "friendsPage")
        logging.info(f"Получена страница друзей для {username}. Страница: {page_info.page}, размер: {page_info.size}")
        if status_code == 500:
            return response_text, status_code
        page_data = check_users_page_result_operation(response_text)
        return page_data, status_code
    
    @allure.step("SOAP Отправка приглашения в друзья")
    def send_friend_invitation(self, username: str, friend_to_be_requested: str) -> tuple[Dict, int]:
        """Отправка приглашения в друзья"""
        xml_data = send_invitation_xml(username, friend_to_be_requested)
        response_text, status_code = self._execute_soap_request(xml_data, "sendInvitation")
        
        result = check_current_user_result_operation(response_text)
        logging.info(f"Отправлено приглашение от {username} для {friend_to_be_requested}")
        return result, status_code
    
    @allure.step("SOAP Принятие приглашения в друзья")
    def accept_friend_invitation(self, username: str, friend_to_be_added: str) -> tuple[Dict, int]:
        """Принятие приглашения в друзья"""
        xml_data = accept_invitation_xml(username, friend_to_be_added)
        response_text, status_code = self._execute_soap_request(xml_data, "acceptInvitation")
        
        result = check_current_user_result_operation(response_text)
        logging.info(f"Принято приглашение от {friend_to_be_added} пользователем {username}")
        return result, status_code
    
    @allure.step("SOAP Отклонение приглашения в друзья")
    def decline_friend_invitation(self, username: str, invitation_to_be_declined: str) -> tuple[Dict, int]:
        """Отклонение приглашения в друзья"""
        xml_data = decline_invitation_xml(username, invitation_to_be_declined)
        response_text, status_code = self._execute_soap_request(xml_data, "declineInvitation")
        
        result = check_current_user_result_operation(response_text)
        logging.info(f"Отклонено приглашение от {invitation_to_be_declined} пользователем {username}")
        return result, status_code
    
    @allure.step("SOAP Удаление из друзей")
    def remove_friend(self, username: str, friend_to_be_removed: str):
        """Удаление пользователя из друзей"""
        xml_data = remove_friend_xml(username, friend_to_be_removed)
        response_text, status_code = self._execute_soap_request(xml_data, "removeFriend")
        
        logging.info(f"Пользователь {friend_to_be_removed} удален из друзей {username}")
    
    def close(self):
        """Закрытие сессии"""
        if hasattr(self.session, 'close'):
            self.session.close()