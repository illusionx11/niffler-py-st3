import logging
from databases.spends_db import SpendsDb
from databases.auth_db import AuthDb
from databases.userdata_db import UserdataDb
from models.config import ClientEnvs


class StandCleaner:
    
    def __init__(self, spends_db: SpendsDb, auth_db: AuthDb, userdata_db: UserdataDb, client_envs: ClientEnvs):
        self.spends_db = spends_db
        self.auth_db = auth_db
        self.userdata_db = userdata_db
        self.client_envs = client_envs
        
    def clean(self):
        self.spends_db.delete_all_spendings()
        self.spends_db.delete_all_categories()
        self.userdata_db.delete_all_users(exclude=[self.client_envs.test_username])
        self.auth_db.delete_all_users(exclude=[self.client_envs.test_username])