#!/usr/bin/env python
# FIXME:
#   - socket length
#   - configuration file
#   - notify user
import os
import sys

import gnupg
import yaml

gpg = gnupg.GPG()


def load_data(filepath):
    data = {}
    try:
        data = yaml.load(str(gpg.decrypt_file(open(filepath, 'r'))))
    except:
        pass
    return data


def store_data(filepath, data):

    if not data:
        return True

    success = False
    try:
        yaml_data = yaml.dump(data, width=79, indent=2,
                              default_flow_style=False, explicit_start=True)
        encrypted_data = str(gpg.encrypt(yaml_data, 'mark@stillwell.me'))
        f = open(filepath, 'w')
        f.write(encrypted_data)
        f.close()
        success = True
    except:
        pass

    return success


def send_javascript(script):
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


def load_action(filepath, window_urlpath):
    pass


def store_action(filepath, window_urlpath):

    # load data from file
    data = load_data(filepath)

    # get data from uzbl window
    window_form_data = dump_window_form_data()

    # update site data
    if window_form_data is not None:
        data[window_urlpath] = window_form_data

    # save site form data and return result
    return store_data(filepath, data)


def main(argv=None):
    from urlparse import urlparse
    from xdg.BaseDirectory import xdg_data_home

    uzbl_forms_dir = os.path.join(xdg_data_home, 'uzbl', 'forms')

    # ensure that forms directory exists and has secure permissions
    try:
        os.makedirs(uzbl_forms_dir, 0700)
    except OSError:
        os.chmod(uzbl_forms_dir, 0700)

    # parse uri for information needed to load/update/save site data
    window_uri = os.getenv('UZBL_URI', 'noproto://undefined')
    urlparse_result = urlparse(window_uri)
    window_hostname = urlparse_result.hostname
    window_urlpath = urlparse_result.path
    if window_urlpath is None or window_urlpath == '':
        window_urlpath = '/'

    # generate file path for current uzbl window
    filepath = os.path.join(uzbl_forms_dir, window_hostname + '.yml.asc')

    store_action(filepath, window_urlpath)

    return 0


if __name__ == "__main__":
    sys.exit(main())
