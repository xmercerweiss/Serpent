
import sys

from src import game, graphics
from utils import Scanner


APP_CONF = "confs/game.conf"

REND_CONFS = {
    graphics.CLIRenderer: "confs/cli.conf",
    graphics.GUIRenderer: "confs/gui.conf",
}

GUI_FLAGS = {
    "gui",
    "-gui",
    "g",
    "-g",
}

CLI_FLAGS = {
    "cli",
    "-cli",
    "c",
    "-c",
}


def main():
    args = sys.argv
    if len(args) < 2 or args[1].lower() in GUI_FLAGS:
        rend_cls = graphics.GUIRenderer
    elif args[1].lower() in CLI_FLAGS:
        rend_cls = graphics.CLIRenderer
    app_conf = Scanner.scan(APP_CONF)
    rend_conf = Scanner.scan(REND_CONFS[rend_cls])
    
    app = game.Snake(rend_cls, rend_conf, **app_conf)
    app.start()


if __name__ == "__main__":
    main()
