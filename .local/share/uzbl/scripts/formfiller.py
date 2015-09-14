#!/usr/bin/env python
import os
import socket
import sys
from urlparse import urlparse

from xdg.BaseDirectory import xdg_data_home

import gnupg
import yaml


uzbl_forms_dir = os.path.join(xdg_data_home, 'uzbl', 'forms')


def main(argv=None):

    try:
        os.makedirs(uzbl_forms_dir, 0700)
    except OSError:
        os.chmod(uzbl_forms_dir, 0700)

    response = ''
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(os.environ.get('UZBL_SOCKET', None))
        s.sendall('js uzbl.formfiller.dump();\n')
        response = s.recv(16384)
        s.close()
    except:
        pass

    message, json_data = response.split('\n', 1)
    data = yaml.load(json_data)
    yaml_data = yaml.dump(data)

    hostname = urlparse(os.getenv('UZBL_URI', 'http://undefined')).hostname

    gpg = gnupg.GPG()
    encrypted_data = str(gpg.encrypt(yaml_data, 'mark@stillwell.me'))

    try:
        formfile = open(os.path.join(uzbl_forms_dir, hostname + '.asc'), 'w')
        formfile.write(encrypted_data)
        formfile.close()
    except:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
