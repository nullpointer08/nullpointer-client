'''
Command line utility which installs all the requirements (APT and pip)
Use the -c (or --configure) switch to also configure after installation
of requirements.

Requires superuser priviledges
'''

import os
import subprocess
import sys
import configure
from optparse import OptionParser

APT_REQS = (
    'python-pip',
    'matchbox-window-manager',
    'uzbl',
    'xinit',
    'supervisor'
)

PIP_REQS = (
    'sh==1.11',
    'requests'
)

DEVNULL = open(os.devnull, 'wb')
HOME = '/home/pi'
START_PATH = os.path.dirname(os.path.realpath(__file__))
XINIT_SHELL_SCRIPT = os.path.join(START_PATH, '.xinitrc')
START_PYTHON_SCRIPT_NAME = 'start_client.py'

SUPERVISORD_CONF = """\
[unix_http_server]
file={0}   ; (the path to the socket file)
chmod=0700                       ; sockef file mode (default 0700)

[supervisord]
logfile=/var/log/supervisor/supervisord.log ; (main log file;default $CWD/supervisord.log)
pidfile=/var/run/supervisord.pid ; (supervisord pidfile;default supervisord.pid)
childlogdir=/var/log/supervisor            ; ('AUTO' child log dir, default $TEMP)
user=pi

[rpcinterface:supervisor]
supervisor.rpcinterface_factory = supervisor.rpcinterface:make_main_rpcinterface

[supervisorctl]
serverurl=unix://{0} ; use a unix:// URL  for a unix socket

[include]
files = /etc/supervisor/conf.d/*.conf
""".format(os.path.join(START_PATH, 'supervisor.sock'))

SUPERVISOR_PROG_CONF = """\
[program:nullpointer]
autorestart=true
autostart=true
command=python {start_script}
directory={work_dir}
environment=DISPLAY=":0", HOME="{home}"
startsecs=10
user=pi

[program:xinit]
autorestart=true
autostart=true
command=xinit {xinit}
user=pi
""".format(
    home=HOME,
    start_script=os.path.join(START_PATH, START_PYTHON_SCRIPT_NAME),
    work_dir=START_PATH,
    xinit=XINIT_SHELL_SCRIPT)

def install_apt_req(apt_req):
    retval = subprocess.call(
        ['apt-get', 'install', apt_req, '-y'],
        stdout=DEVNULL,
        stderr=DEVNULL
    )
    return retval == 0


def is_apt_pkg_installed(apt_req):
    retval = subprocess.call(
        ['dpkg', '-s', apt_req],
        stdout=DEVNULL,
        stderr=DEVNULL
    )
    return retval == 0


def install_pip_req(pip_req):
    retval = subprocess.call(
        ['pip', 'install', pip_req],
        stdout=DEVNULL,
        stderr=DEVNULL
    )
    return retval == 0


def is_pip_req_installed(req):
    return req in sys.modules

def install_reqs(reqs, is_installed_func, install_func):
    pkg_count = 0
    for req in reqs:
        if is_installed_func(req):
            status = 'Already installed'
        else:
            install_ok = install_func(req)
            if not install_ok:
                status = 'Installation failed'
            else:
                status = 'Installation successful'
        pkg_count += 1
        print '%s/%s) %s: %s' % (pkg_count, len(reqs), req, status)

def configure_supervisor():
    with open('/etc/supervisor/supervisord.conf', 'w') as config:
        config.write(SUPERVISORD_CONF)

    with open('/etc/supervisor/conf.d/nullpointer.conf', 'w') as config:
        config.write(SUPERVISOR_PROG_CONF)

def create_xinit_shell_script():
    startup_script = open(os.path.join(START_PATH, XINIT_SHELL_SCRIPT), 'w')
    startup_script.write('#!/bin/bash\n')
    startup_script.write('xset -dpms\n')
    startup_script.write('xset s off\n')
    startup_script.write('xset s noblank\n')
    startup_script.write('matchbox-window-manager -use_titlebar no -use_cursor no')
    startup_script.close()
    os.chmod(XINIT_SHELL_SCRIPT, 0555)
    print 'Wrote xinit script to %s' % START_PATH


def install():
    print 'Installing APT packages...'
    install_reqs(APT_REQS, is_apt_pkg_installed, install_apt_req)
    print '\nInstalling python packages...'
    install_reqs(PIP_REQS, is_pip_req_installed, install_pip_req)
    print '\nCreating startup shell script'
    create_xinit_shell_script()
    print '\nAdding client to startup programs'
    configure_supervisor()

if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option(
        '-c',
        '--configure',
        dest='configure',
        action='store_true',
        default=False,
        help='Configure client properties after installation'
    )
    (options, args) = parser.parse_args()

    install()
    configure.create_properties_with_default_values()
    if options.configure:
        configure.set_properties_from_user_input()
    DEVNULL.close()
