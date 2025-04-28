from pydantic import BaseModel

class ServerEnvs(BaseModel):
    frontend_url: str
    gateway_url: str
    auth_url: str
    spends_db_url: str
    
class ClientEnvs(BaseModel):
    test_username: str
    test_password: str