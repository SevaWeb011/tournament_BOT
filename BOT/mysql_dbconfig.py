import os

def read_db_config():
    db = {
        "host" : os.getenv("HOST"),
        "database" : os.getenv("DATABASE"),
        "user" : os.getenv("USER"),
        "password" : os.getenv("PASSWORD")
    }
 
    return db