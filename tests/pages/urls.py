import os
from selenium import webdriver

class Urls:
    
    LOGIN_URL = f"{os.getenv('AUTH_URL')}/login"
    REGISTER_URL = f"{os.getenv('AUTH_URL')}/register"
    FRONTEND_URL = f"{os.getenv('FRONTEND_URL')}/main"
    GATEWAY_URL = os.getenv('GATEWAY_URL')
        
