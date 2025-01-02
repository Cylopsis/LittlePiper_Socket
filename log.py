import sys
from datetime import datetime
ISATTY = sys.stdout.isatty()
def make_color(code):
    def color_func(s):
        if not ISATTY:
            return s
        tpl = '\x1b[{}m{}\x1b[0m'
        return tpl.format(code, s)
    return color_func
red = make_color(31)
green = make_color(32)
yellow = make_color(33)
blue = make_color(34)
magenta = make_color(35)
cyan = make_color(36)

bold = make_color(1)
underline = make_color(4)
class Logger:
    red = red
    green = green
    yellow = yellow
    blue = blue
    magenta = magenta
    cyan = cyan
    bold = bold
    underline = underline
    SILENT = 0
    ERROR  = 1
    WARNING = 2
    INFO = 3
    SUCCESS = 3
    DEBUG = 4
    def __init__(self, level=3):
        self.level = level

    def set_level(self, level:int):
        if level in [Logger.SILENT, Logger.ERROR, Logger.WARNING, Logger.INFO, Logger.SUCCESS, Logger.DEBUG]:
            self.level = level
        else:
            raise ValueError(f'''Invalid log level: {level}
    SILENT = {Logger.SILENT}
    ERROR  = {Logger.ERROR}
    WARNING = {Logger.WARNING}
    INFO = {Logger.INFO}
    SUCCESS = {Logger.SUCCESS}
    DEBUG = {Logger.DEBUG}
''')

    def log(self, levelStr, msg, enumLevel=None):
        if enumLevel <= self.level:
            print(f'[{levelStr}] {cyan(datetime.now())} | {msg}')

    def error(self, msg):
        self.log(red('ERROR'), msg, enumLevel=Logger.ERROR)

    def warning(self, msg):
        self.log(yellow('WARNING'), msg, enumLevel=Logger.WARNING)

    def info(self, msg):
        self.log('INFO', msg, enumLevel=Logger.INFO)

    def success(self, msg):
        self.log(green('SUCCESS'), msg, enumLevel=Logger.SUCCESS)

    def debug(self, msg):
        self.log(blue('DEBUG'),msg,enumLevel=Logger.DEBUG)


def error(info:str):
    print(red(f'[ ERROR ] {datetime.now()} |'),info)
def info(msg:str):
    print(f'[ INFO  ] {datetime.now()} |',msg)
def success(msg:str):
    print(green(f'[SUCCESS] {datetime.now()} |'),msg)
def warning(msg:str):
    print(yellow(f'[WARNING] {datetime.now()} |'),msg)

if __name__ == '__main__':
    logger = Logger()
    logger.error('This is an error message')
    logger.warning('This is a warning message')
    logger.info('This is an info message')
    logger.success('This is a success message')