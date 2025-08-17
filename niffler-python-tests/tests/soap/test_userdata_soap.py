import pytest
import allure
import random
from faker import Faker
from utils.allure_data import Epic, Feature, Story
from clients.soap_client import SoapClient
from models.soap import PageInfo, SoapUser
from models.enums import FriendshipStatus, Currency
from models.user import UserData
from marks import TestData
from databases.userdata_db import UserdataDb

pytestmark = [pytest.mark.allure_label(label_type="epic", value=Epic.app_name)]

@pytest.mark.usefixtures(
    "soap_client", 
    "mock_users", 
    "mock_friends",
    "mock_friends_actions",
    "soap_user",
    "cleanup"
)
@pytest.mark.soap
@pytest.mark.user_management
@allure.feature(Feature.userdata)
class TestSoapUsers:
    """Тесты SOAP API с использованием XML запросов"""
    
    def map_pagination_error(self, page_info: PageInfo) -> str | None:
        if page_info.page < 0:
            return "Page index must not be less than zero"
        if page_info.size < 1:
            return "Page size must not be less than one"
        return None
    
    @allure.story(Story.user_management)
    def test_get_user_info_with_existing_username(self, soap_client: SoapClient, soap_user: str):
        """Тест получения существующего пользователя через SOAP"""
        user_data, status_code = soap_client.get_current_user(username=soap_user)
        
        with allure.step('Проверка корректности ответа'):
            assert user_data['username'] == soap_user
            assert user_data['id'], f"У пользователя {soap_user} нет id"
            assert user_data.get('currency'), f"У пользователя {soap_user} нет currency"

    @allure.story(Story.user_management)
    def test_get_user_that_doesnt_exist(self, soap_client: SoapClient, soap_user: str):
        """Тест получения пользователя, которого нет в базе"""
        
        username = "a_user_that_has_never_existed"
        user_data, status_code = soap_client.get_current_user(username=username)
        
        with allure.step('Проверка корректности ответа'):
            assert user_data is not None, f"Пользователь {username} должен быть"
            assert user_data.get('id') is None, f"У пользователя {username} не должно быть id"
            assert user_data.get('username') == username, f"Имя пользователя в ответе должно быть {username}"
            assert user_data.get('currency') == Currency.RUB, f"У пользователя {username} должен быть currency {Currency.RUB}"
            assert user_data.get('friendshipStatus') == FriendshipStatus.VOID, \
                f"У пользователя {username} должен быть friendshipStatus {FriendshipStatus.VOID}"
    
    @allure.story(Story.user_management)
    def test_get_all_users(self, soap_client: SoapClient, soap_user: str, mock_users: list[UserData]):
        """Тест получения списка всех пользователей через SOAP"""
        users, status_code = soap_client.get_all_users(username=soap_user)

        with allure.step('Проверка корректности ответа'):
            assert isinstance(users, list)
            assert len(users) > 0
            for mock_user in mock_users:
                soap_user = next((user for user in users if user.get('username') == mock_user.username), None)
                assert soap_user is not None, f"Пользователь {mock_user.username} должен быть в списке"
                assert soap_user.get('id') is not None, f"У пользователя {mock_user.username} должен быть id"
                assert soap_user.get('currency') == Currency.RUB, \
                    f"У пользователя {mock_user.username} должен быть currency {Currency.RUB}"

    @TestData.page_info([
        PageInfo(page=1, size=3),
        PageInfo(page=2, size=4),
        PageInfo(page=1, size=6),
        PageInfo(page=4, size=2)
    ])
    @allure.story(Story.user_management)
    def test_get_all_users_pagination(self, soap_client: SoapClient, soap_user: str, page_info: PageInfo, mock_users: list[UserData]):
        """Тест получения пользователей с пагинацией через SOAP"""
        page_result, status_code = soap_client.get_all_users_page(
            username=soap_user,
            page_info=page_info
        )
        
        with allure.step('Проверка структуры ответа с пагинацией'):
            assert isinstance(page_result['users'], list)
            assert len(page_result['users']) == page_info.size
            assert page_result['size'] == page_info.size
            assert page_result['number'] == page_info.page
            
    @TestData.page_info([
        PageInfo(page=4, size=100),
        PageInfo(page=100, size=100),
        PageInfo(page=1000, size=1)
    ])
    @allure.story(Story.user_management)
    def test_get_all_users_page_out_of_range(self, soap_client: SoapClient, soap_user: str, page_info: PageInfo):
        """Тест получения пользователей с пагинацией через SOAP с некорректными параметрами"""
        page_result, status_code = soap_client.get_all_users_page(
            username=soap_user,
            page_info=page_info
        )

        with allure.step('Проверка структуры ответа с пагинацией'):
            assert isinstance(page_result['users'], list)
            assert len(page_result['users']) == 0
            assert page_result['size'] == page_info.size
            assert page_result['number'] == page_info.page
            
    @TestData.page_info([
        PageInfo(page=-1, size=1),
        PageInfo(page=1, size=-1),
        PageInfo(page=1, size=0),
        PageInfo(page=-1, size=-1)
    ])
    @allure.story(Story.user_management)
    def test_get_all_users_page_invalid_parameters(self, soap_client: SoapClient, soap_user: str, page_info: PageInfo):
        """Тест получения пользователей с пагинацией через SOAP с некорректными параметрами"""
        
        page_result, status_code = soap_client.get_all_users_page(
            username=soap_user,
            page_info=page_info
        )
        error_text = self.map_pagination_error(page_info)
        
        with allure.step('Проверка корректности ответа'):
            assert status_code == 500
            assert page_result == error_text
            
    @allure.story(Story.user_management)
    @pytest.mark.xfail(reason="full name не обновляется на бэкенде")
    def test_update_user_currency_and_full_name(
        self, 
        faker: Faker,
        userdata_db: UserdataDb,
        soap_user: str,
        soap_client: SoapClient
    ):
        """Тест обновления пользователя через SOAP"""

        user_data = userdata_db.get_user_by_name(soap_user)
        user_id = user_data.id
        user_currency = user_data.currency
        new_currency = random.choice([c for c in Currency.ALL if c != user_currency])
        
        full_name = f"{faker.first_name()} {faker.last_name()}"
        update_data = SoapUser(
            id=str(user_id),
            username=soap_user,
            currency=new_currency,
            full_name=full_name
        )
        
        soap_client.update_user(update_data)
        updated_user = userdata_db.get_user_by_name(soap_user)
        with allure.step('Проверка корректности обновления'):
            assert updated_user.id == user_id
            assert updated_user.username == soap_user
            assert updated_user.currency == new_currency
            assert updated_user.full_name == full_name
    
    @pytest.mark.friends_management
    @allure.story(Story.friends_management)
    def test_get_friends(self, soap_client: SoapClient, mock_friends: list[UserData], soap_friends_user: str):
        """Тест получения списка друзей через SOAP"""
        friends, status_code = soap_client.get_friends(username=soap_friends_user)
        with allure.step('Проверка корректности ответа'):
            assert isinstance(friends, list)
            for mock_friend in mock_friends:
                friend = next((f for f in friends if f.get('username') == mock_friend.username), None)
                assert friend is not None, f"Друг {mock_friend.username} должен быть в списке"
                assert friend.get('friendshipStatus') == FriendshipStatus.FRIEND
    
    @TestData.page_info([
        PageInfo(page=1, size=5),
        PageInfo(page=2, size=3),
        PageInfo(page=4, size=2)
    ])
    @pytest.mark.friends_management
    @allure.story(Story.friends_management)
    def test_get_friends_page(
        self, 
        soap_client: SoapClient,
        soap_friends_user: str,
        mock_friends: list[UserData],
        page_info: PageInfo, 
    ):
        """Тест получения друзей с пагинацией через SOAP"""
        page_result, status_code = soap_client.get_friends_page(
            username=soap_friends_user,
            page_info=page_info
        )
        
        with allure.step('Проверка структуры ответа с пагинацией'):
            assert isinstance(page_result['users'], list)
            assert len(page_result['users']) == page_info.size
            assert page_result['size'] == page_info.size
            assert page_result['number'] == page_info.page
            
            mock_usernames = [friend.username for friend in mock_friends]
            for user in page_result['users']:
                assert user.get('username') in mock_usernames, \
                    f"Друг {user.get('username')} должен быть в списке друзей"
                assert user.get('friendshipStatus') == FriendshipStatus.FRIEND
            
    @TestData.page_info([
        PageInfo(page=4, size=100),
        PageInfo(page=100, size=100),
        PageInfo(page=1000, size=1)
    ])
    @pytest.mark.friends_management
    @allure.story(Story.friends_management)
    def test_get_friends_page_out_of_range(
        self, 
        soap_client: SoapClient,
        soap_friends_user: str,
        page_info: PageInfo
    ):
        """Тест получения друзей с пагинацией через SOAP"""        
        page_result, status_code = soap_client.get_friends_page(
            username=soap_friends_user,
            page_info=page_info
        )
        
        with allure.step('Проверка структуры ответа с пагинацией'):
            assert isinstance(page_result['users'], list)
            assert len(page_result['users']) == 0
            assert page_result['size'] == page_info.size
            assert page_result['number'] == page_info.page
            
    @TestData.page_info([
        PageInfo(page=-1, size=1),
        PageInfo(page=1, size=-1),
        PageInfo(page=1, size=0),
        PageInfo(page=-1, size=-1)
    ])
    @pytest.mark.friends_management
    @allure.story(Story.friends_management)
    def test_get_friends_page_invalid_parameters(
        self, 
        soap_client: SoapClient,
        soap_friends_user: str,
        page_info: PageInfo
    ):
        """Тест получения друзей с пагинацией через SOAP с некорректными параметрами"""
        page_result, status_code = soap_client.get_friends_page(
            username=soap_friends_user,
            page_info=page_info
        )
        error_text = self.map_pagination_error(page_info)
        
        with allure.step('Проверка корректности ответа'):
            assert status_code == 500
            assert page_result == error_text
    
    @pytest.mark.friends_management
    @allure.story(Story.friends_management)
    def test_send_friend_invitation(
        self, 
        soap_client: SoapClient,
        soap_actions_user: str,
        mock_friends_actions: list[UserData]
    ):
        """Тест отправки приглашения в друзья через SOAP"""
        target_username = mock_friends_actions[-1].username
        
        invitation_data, status_code = soap_client.send_friend_invitation(
            username=soap_actions_user,
            friend_to_be_requested=target_username
        )
        
        with allure.step('Проверка корректности ответа'):
            assert invitation_data is not None
            assert invitation_data.get('username') == target_username
            assert invitation_data.get('friendshipStatus') == FriendshipStatus.INVITE_SENT
    
    @pytest.mark.friends_management      
    @allure.story(Story.friends_management)
    def test_accept_friend_invitation(
        self, 
        soap_client: SoapClient,
        soap_actions_user: str,
        mock_friends_actions: list[UserData]
    ):
        """Тест принятия приглашения в друзья через SOAP"""
        target_username = mock_friends_actions[-2].username
        
        soap_client.send_friend_invitation(
            username=soap_actions_user,
            friend_to_be_requested=target_username
        )
        
        accept_data, status_code = soap_client.accept_friend_invitation(
            username=target_username,
            friend_to_be_added=soap_actions_user
        )
        
        with allure.step('Проверка корректности ответа'):
            assert accept_data is not None
            assert accept_data.get('username') == soap_actions_user
            assert accept_data.get('friendshipStatus') == FriendshipStatus.FRIEND
    
    @pytest.mark.friends_management
    @allure.story(Story.friends_management)
    def test_decline_friend_invitation(
        self, 
        soap_client: SoapClient,
        soap_actions_user: str,
        mock_friends_actions: list[UserData]
    ):
        """Тест отклонения приглашения в друзья через SOAP"""
        target_username = mock_friends_actions[-3].username
        
        invitation_data, status_code = soap_client.send_friend_invitation(
            username=soap_actions_user,
            friend_to_be_requested=target_username
        )
        
        decline_data, status_code = soap_client.decline_friend_invitation(
            username=target_username,
            invitation_to_be_declined=soap_actions_user
        )
        
        with allure.step('Проверка корректности ответа'):
            assert decline_data is not None
            assert decline_data.get('username') == soap_actions_user
            assert decline_data.get('friendshipStatus') == FriendshipStatus.VOID
    
    @pytest.mark.friends_management
    @allure.story(Story.friends_management)
    def test_remove_friend(
        self, 
        soap_client: SoapClient,
        soap_actions_user: str,
        mock_friends_actions: list[UserData]
    ):
        """Тест удаления из друзей через SOAP"""
        target_username = mock_friends_actions[0].username
        soap_client.remove_friend(username=soap_actions_user, friend_to_be_removed=target_username)
        friends, status_code = soap_client.get_friends(username=soap_actions_user)
        
        with allure.step('Проверка корректности ответа'):
            assert target_username not in [u.get('username') for u in friends]