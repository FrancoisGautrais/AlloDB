import os
import inspect
import sys
from importlib import import_module
from inspect import getmembers, isfunction

class _CommandsLoader:

    def __init__(self):
        self.commands={}
        self.load()

    def load(self):
        filename = inspect.getframeinfo(inspect.currentframe()).filename
        path = os.path.dirname(os.path.abspath(filename))
        path += "/functions/"
        for x in os.listdir(path):
            if x[0]!="_" and (x[-3:].lower()==".py" or x[-4:].lower()==".pyc"):
                mod="functions."+x.split(".")[0]
                imported_module = import_module(mod)
                functions_list = [o for o in getmembers(imported_module) if isfunction(o[1])]
                for k in functions_list:
                    if k[0].startswith("fct_"):
                        self.commands[k[0][4:]]=k[1]

    def call(self, row, name, args):
        x=None
        if not name in self.commands:
            sys.stderr.write("Command '"+str(name)+"' not found\n")
        x=self.commands[name](row.header.root, row, args)
        return x
_instance=None

def call(shell, name, args=[]):
    global _instance
    if _instance==None: _instance=_CommandsLoader()
    return _instance.call(shell, name, args)
    #return None

