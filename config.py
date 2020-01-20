import os

DB_FILE="db.json"
USER_DIR="user"

with open("config.cfg") as f:
    exec(f.read())


def user(x): return os.path.join(USER_DIR, x, ".json")

