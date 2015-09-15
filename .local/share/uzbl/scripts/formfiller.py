#!/usr/bin/env python
# FIXME:
#   - socket length
#   - configuration file
#   - match uri?
import os
import sys
from urlparse import urlparse

from xdg.BaseDirectory import xdg_data_home

import gnupg
import yaml


uzbl_forms_dir = os.path.join(xdg_data_home, 'uzbl', 'forms')
gpg = gnupg.GPG()


def load_data():
    pass


def store_data():
    pass


def send_javascript(script):
    import socket
    response = ''
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(os.environ.get('UZBL_SOCKET', None))
        s.sendall(script + '\n')
        response = s.recv(16384)
        s.close()
    except:
        pass

    _, json = response.split('\n', 1)

    return json.loads(json)

def dump_window_form_data():
        s.sendall('js uzbl.formfiller.dump();\n')
    pass


def update_window_form_data():
    pass


def main(argv=None):

    # get data from uzbl window

    dump_data = yaml.load(json_dump_data)

    # parse uri for information needed to load/update/save site data
    uri = os.getenv('UZBL_URI', 'noproto://undefined')
    urlparse_result = urlparse(uri)
    hostname = urlparse_result.hostname
    path = urlparse_result.path
    if path is None or path == '':
        path = '/'

    # update site data
    data = {}
    try:
        formfile = open(os.path.join(uzbl_forms_dir, hostname + '.yml.asc'),
                        'r')
        data = yaml.load(str(gpg.decrypt_file(formfile)))
    except:
        pass
    data[path] = dump_data

    # save site form data
    yaml_data = yaml.dump(data, width=79, indent=2, default_flow_style=False,
                          explicit_start=True)
    encrypted_data = str(gpg.encrypt(yaml_data, 'mark@stillwell.me'))

    try:
        os.makedirs(uzbl_forms_dir, 0700)
    except OSError:
        os.chmod(uzbl_forms_dir, 0700)

    try:
        formfile = open(os.path.join(uzbl_forms_dir, hostname + '.yml.asc'),
                        'w')
        formfile.write(encrypted_data)
        formfile.close()
    except:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
