from fabric.api import env as _env

TARGET_LIVE = _env.get("live", None)

VIRTUALENV_ROOT = "~/virtualenv"
PROJECT_NAME = "pikapika" if TARGET_LIVE else "pikapika-saber"
REMOTE_PYTHON_EXEC = "python2.7"
MAIN_PACKAGE = "pikapika"

print ("Target: " + PROJECT_NAME)
