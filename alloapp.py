from allodb import DB
import config
import log

class AlloApp:

    def __init__(self, file):
        self.actor=DB.fromjson(file)

aa = AlloApp(config.DB_FILE)

