from subprocess import run
import os


TERMINALS = {
    "cinnamon": "gnome-terminal",
    "gnome":    "gnome-terminal",
    "xfce":     "xfce4-terminal",
    "mate":     "mate-terminal",
    "kde":      "konsole",
}

DE_ENV_VAR = "$XDG_CURRENT_DESKTOP"
DEFAULT_DE = "gnome"

DE = os.environ.get(DE_ENV_VAR, DEFAULT_DE).split(":")[-1].lower()

TERMINAL_CMD = TERMINALS[DE]

def execute(cmd):
    args = [TERMINAL_CMD, "-x", *cmd.split()]
    run(args)
