from fabric.api import env as _env

VIRTUALENV_ROOT = "~/virtualenv"
PROJECT_NAME = "pikapika" if _env.get("live", None) else "pikapika-saber"
REMOTE_PYTHON_EXEC = "python2.7"
MAIN_PACKAGE = "pikapika"
