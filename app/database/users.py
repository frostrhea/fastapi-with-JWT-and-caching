
# edit this or create your own user database

fake_users_db = {
    "admin": {
        "username": "admin",
        "hashed_password": "<bcrypt-hashed-pw>",
    },
    "test": {
        "username": "test",
        "hashed_password": "$2b$12$cGcgLv.yhY/uRzlEEgIuX.g.nSXSmHaHXSRcI20bI.WwjUuovniTi",
    }
}

def get_user(username: str):
    return fake_users_db.get(username)
