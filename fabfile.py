import os
import re
from glob import glob
import random
import string
from StringIO import StringIO

from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.project import rsync_project

VIRTUALENV_ROOT = "~/virtualenv"
PROJECT_NAME = "pikapika-saber"
REMOTE_PYTHON_EXEC = "python2.7"

SITE_PACKAGES_GLOB = "$VIRTUAL_ENV/lib/python*/site-packages"
PTH_NAME_FORMAT = "_fab_{}.pth"

PROJECT_DIR = "{}/{}".format(VIRTUALENV_ROOT, PROJECT_NAME)
GIT_REPO = "{}/repo.git".format(PROJECT_DIR)
STAGE_CURRENT = "{}/stage_current".format(PROJECT_DIR)
STAGE_OLD = "{}/stage_old".format(PROJECT_DIR)
STAGE_ROOT = "{}/stage".format(PROJECT_DIR)

NEW_INSTANCE_ID = "".join(
    [random.choice(string.ascii_lowercase) for x in range(8)]
)
EXTRA_INIT_SCRIPT = """
export INSTANCE_ID="-{}"
export DJANGO_SETTINGS_MODULE="pikapika.settings_production"
""".format(
    NEW_INSTANCE_ID,
)

HOSTS = {
    "hostgator": {
        "reload_app_script": """
            cp fcgi.sh ~/public/{}/index.fcgi
            killall -q -s SIGHUP python$INSTANCE_ID || true
        """.format(PROJECT_NAME),
        "skip_packages": (
            "MySQL-python",
            "PIL",
        ),
        "system_site_packages": True,
        "extra_setting_files": {
            "~/public/{}/".format(PROJECT_NAME): (
                ".htaccess", "env.sh",
            ),
        },
    },
}

if not env.hosts:
    env.hosts = list(HOSTS.keys())

env.use_ssh_config = True

def _validate_local():
    if not os.environ.has_key("VIRTUAL_ENV"):
        abort("Virtualenv is not initialized!")

def _activate_env(working_dir=PROJECT_DIR):
    return prefix(". {}/bin/activate && cd {}".format(PROJECT_DIR, working_dir))

def _get_host_setting(key, default=None):
    return HOSTS.get(env.host_string, {}).get(key)

def destroy_env():
    if confirm("Do your really want to destroy the project on server?", 
               default=False):

        with cd(VIRTUALENV_ROOT):
            run("rm -rf " + PROJECT_NAME)

def init_env():
    run("mkdir -p " + VIRTUALENV_ROOT)
    with cd(VIRTUALENV_ROOT):
        with settings(hide("warnings"), warn_only=True, ):
            if run("test -d " + PROJECT_NAME).succeeded:
                abort("Project already exists on the server")

        run("wget -O virtualenv.py --no-check-certificate https://raw.github.com/pypa/virtualenv/master/virtualenv.py")
        system_site_packages = _get_host_setting("system_site_packages")
        run("{} virtualenv.py {} {}".format(
            REMOTE_PYTHON_EXEC, 
            "--system-site-packages" if system_site_packages else "",
            PROJECT_NAME,
        ))

    with _activate_env():
        run('cat >> bin/activate <<EOF\n{}\nEOF'.format(EXTRA_INIT_SCRIPT))
        run("ln -s {0}/bin/python {0}/bin/python$INSTANCE_ID".format(
            PROJECT_DIR))

    init_repo()

def init_repo():
    run("mkdir -p {}".format(GIT_REPO))
    run("mkdir -p {}".format(STAGE_CURRENT))

    with cd(GIT_REPO):
        run("git init --bare")

    with cd(STAGE_CURRENT):
        run("git clone {} .".format(GIT_REPO))
        
        # On hostgator this defaults to false!
        run("git config core.symlinks true")

def push_settings():
    # Can't use this due to fabric bug #370
    # with cd(STAGE_CURRENT):

    settings_root = os.path.join(
        os.path.dirname(__file__),
        "settings_production",
        PROJECT_NAME,
    )

    put(os.path.join(settings_root, "settings_production.py"),
        STAGE_CURRENT + "/pikapika/",)

    extra_files = _get_host_setting("extra_setting_files", {})
    for target_dir, files in extra_files.items():
        for file_name in files:
            put(os.path.join(settings_root, file_name), target_dir)

def push_repo():
    local("git push ssh://{}/{}/ production".format(env.host_string, GIT_REPO))

def push():
    push_repo()

    # Backup current environment
    run("test -d {0} && rm -rf {0} || true".format(STAGE_OLD))

    # Hostgator complains about symbolic links if we use -a only
    run("cp -a --copy-contents -L {} {}".format(STAGE_CURRENT, STAGE_OLD))

    # To prevent downtime
    run("ln -sfn {} {}".format(STAGE_OLD, STAGE_ROOT))

    with _activate_env(STAGE_CURRENT):
        run("git fetch")
        run("git checkout production")
        run("git merge --ff-only origin/production")

    install_requirements()
    setup_submodules()
    push_settings()

    run("ln -sfn {} {}".format(STAGE_CURRENT, STAGE_ROOT))
    with _activate_env(STAGE_CURRENT):
        # Workaround for hostgator, fix missing symbolic links
        run("git checkout .")

        run("mkdir -p static")
        run("python manage.py collectstatic --clear --noinput")

def reset_stage():
    with _activate_env(STAGE_CURRENT):
        run("git reset --hard")
        run("git checkout -- .")

def push_working_tree():
    reset_stage()
    diff = local("git diff production", capture=True) + "\n--\n"
    temp_file = "/tmp/{}".format(
        ''.join(random.sample(string.ascii_letters, 32))
    )
    put(StringIO(diff), temp_file)
    try:
        with _activate_env(STAGE_CURRENT):
            run("cat -n {}".format(temp_file))
            run("git apply {}".format(temp_file))

    finally:
        run("rm {}".format(temp_file))
        
    reload_app()

def promote():
    local("git checkout production")
    local("git merge --ff-only master")
    local("git checkout master")

def migrate_db():
    with _activate_env(STAGE_CURRENT):
        run("python manage.py migrate --all")

def init_db():
    with _activate_env(STAGE_CURRENT):
        run("python manage.py syncdb --noinput")

    migrate_db()

def backup_db():
    with _activate_env(STAGE_CURRENT):
        run("python manage.py backupdb")

def reload_app():
    script = _get_host_setting("reload_app_script")
    if script:
        with _activate_env(STAGE_CURRENT):
            for line in [x.strip() for x in script.splitlines()]:
                if not line:
                    continue

                run(line)

def load_fixtures():
    with _activate_env(STAGE_CURRENT):
        run("python manage.py loaddata fixtures/*.json")

def install_requirements():
    skip_packages = _get_host_setting("skip_packages")
    with open("requirements.txt", "r") as f:
        for line in f:
            if not any([x for x in skip_packages if line.startswith(x)]):
                with _activate_env(STAGE_CURRENT):
                    run("pip install " + line.strip())

def setup_submodules():
    with _activate_env(STAGE_CURRENT):
        run("git submodule update --init")

        run("rm {}/{} || true".format(
            SITE_PACKAGES_GLOB, 
            PTH_NAME_FORMAT.format("*"),
        ))

        for name in os.listdir("submodules"):
            if os.path.isfile("submodules/{}/setup.py".format(name)):
                run("echo {}/submodules/{}/ > `echo {}`/{}".format(
                    STAGE_ROOT,
                    name,
                    SITE_PACKAGES_GLOB,
                    PTH_NAME_FORMAT.format(name),
                ))


def deploy_init():
    _validate_local()
    init_env()
    push()
    init_db()
    reload_app()

def deploy():
    _validate_local()
    promote()
    push()
    migrate_db()
    reload_app()

