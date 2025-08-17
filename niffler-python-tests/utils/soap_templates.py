from jinja2 import Environment, select_autoescape, FileSystemLoader
from models.soap import PageInfo, SoapUser

"""SOAP XML шаблоны для niffler-userdata сервиса"""

env = Environment(
    loader=FileSystemLoader('schemas/templates/xml'),
    autoescape=select_autoescape()
)

def current_user_xml(username: str) -> str:
    """XML для получения текущего пользователя"""
    template = env.get_template('current_user.xml')
    return template.render(username=username)

def all_users_xml(username: str, search_query: str = None) -> str:
    """XML для получения всех пользователей"""
    search_part = f"<nif:searchQuery>{{ {search_query} }}</nif:searchQuery>" if search_query else ""
    template = env.get_template('all_users.xml')
    return template.render(username=username, search_part=search_part)

def all_users_page_xml(username: str, page_info: PageInfo, search_query: str = None) -> str:
    """XML для получения пользователей с пагинацией"""
    search_part = f"<nif:searchQuery>{{ {search_query} }}</nif:searchQuery>" if search_query else ""
    sort = f"<nif:sort>{{ {page_info.sort} }}</nif:sort>" if page_info.sort else ""
    template = env.get_template('all_users_page.xml')
    return template.render(
        username=username, 
        page=page_info.page, 
        size=page_info.size, 
        sort=sort,
        search_part=search_part
    )

def friends_xml(username: str, search_query: str = None) -> str:
    """XML для получения друзей"""
    search_part = f"<nif:searchQuery>{{ {search_query} }}</nif:searchQuery>" if search_query else ""
    template = env.get_template('friends.xml')
    return template.render(username=username, search_part=search_part)

def friends_page_xml(username: str, page_info: PageInfo, search_query: str = None) -> str:
    """XML для получения друзей с пагинацией"""
    search_part = f"<nif:searchQuery>{{ {search_query} }}</nif:searchQuery>" if search_query else ""
    sort = f"<nif:sort>{{ {page_info.sort} }}</nif:sort>" if page_info.sort else ""
    template = env.get_template('friends_page.xml')
    return template.render(
        username=username, 
        page=page_info.page, 
        size=page_info.size, 
        sort=sort,
        search_part=search_part
    )

def send_invitation_xml(username: str, friend_to_be_requested: str) -> str:
    """XML для отправки приглашения в друзья"""
    template = env.get_template('send_invitation.xml')
    return template.render(username=username, friend_to_be_requested=friend_to_be_requested)

def accept_invitation_xml(username: str, friend_to_be_added: str) -> str:
    """XML для принятия приглашения в друзья"""
    template = env.get_template('accept_invitation.xml')
    return template.render(username=username, friend_to_be_added=friend_to_be_added)

def decline_invitation_xml(username: str, invitation_to_be_declined: str) -> str:
    """XML для отклонения приглашения в друзья"""
    template = env.get_template('decline_invitation.xml')
    return template.render(username=username, invitation_to_be_declined=invitation_to_be_declined)

def remove_friend_xml(username: str, friend_to_be_removed: str) -> str:
    """XML для удаления из друзей"""
    template = env.get_template('remove_friend.xml')
    return template.render(username=username, friend_to_be_removed=friend_to_be_removed)

def update_user_xml(user_data: SoapUser) -> str:
    """XML для обновления пользователя"""
    first_name = f"<nif:firstname>{{ {user_data.firstname} }}</nif:firstname>" if user_data.firstname else ""
    surname = f"<nif:surname>{{ {user_data.surname} }}</nif:surname>" if user_data.surname else ""
    photo = f"<nif:photo>{{ {user_data.photo} }}</nif:photo>" if user_data.photo else ""
    photo_small = f"<nif:photoSmall>{{ {user_data.photo_small} }}</nif:photoSmall>" if user_data.photo_small else ""
    full_name = f"<nif:fullName>{{ {user_data.full_name} }}</nif:fullName>" if user_data.full_name else ""
    friendship_status = f"<nif:friendshipStatus>{{ {user_data.friendship_status} }}</nif:friendshipStatus>" if user_data.friendship_status else ""
    
    template = env.get_template('update_user.xml')
    return template.render(
        id=user_data.id,
        username=user_data.username,
        currency=user_data.currency,
        firstname=first_name,
        surname=surname,
        photo=photo,
        photo_small=photo_small,
        full_name=full_name,
        friendship_status=friendship_status
    )