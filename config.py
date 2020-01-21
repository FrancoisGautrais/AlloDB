import os

DB_FILE="db.json"
USER_DIR="user"
WWW_DIR = "www"

with open("config.cfg") as f:
    exec(f.read())


def user(x): return os.path.join(USER_DIR, x, ".json")


def www(x):
    return os.path.join(WWW_DIR, x)