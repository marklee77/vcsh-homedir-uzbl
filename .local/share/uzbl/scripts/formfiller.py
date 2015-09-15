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


def load_data(filepath):
    pass


def store_data(filepath, data):
    pass


def send_javascript(script):
    import json
    import socket
    retval = None
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(os.environ.get('UZBL_SOCKET', None))
        s.sendall('js ' + script + '\n')
        response = s.recv(16384)
        s.close()
        _, js_retval = response.split('\n', 1)
        retval = yaml.load(js_retval)
    except:
        pass

    return retval


def dump_window_form_data():
    return send_javascript('uzbl.formfiller.dump();')


def update_window_form_data():
    pass


def main(argv=None):

    # get data from uzbl window
    dump_data = dump_window_form_data()

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
