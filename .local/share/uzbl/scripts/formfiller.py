#!/usr/bin/env python
# FIXME:
#   - support multiple data for same form
#   - support linking paths as well as sites
#   - support hinting that data is available
#   - support password generation
#   - actually forms from other frames should be associated with the src url...
#     get from javascript instead of UZBL_URI?
#   - capture available values from select box
#   - possible db format: index.yml with encrypted entries
#       - index contains entries with url regex list, form name, field names,
#         optionally encryption targets, and form uuid, uuid.yml.asc contains
#         encrypted info for a single form
#   - check for https when loading
#   - autoload
import gtk
import json
import os
import re
import socket
import sys
import yaml

from argparse import ArgumentParser
from gnupg import GPG
from urlparse import urlparse
from xdg.BaseDirectory import xdg_data_home

gpg = GPG()
uzbl_forms_dir = os.path.join(xdg_data_home, 'uzbl', 'formdata')

# if someone with more experience working with python sockets knows a better
# way to do this, email me some code or put in a github pull request.
RECV_BUFSIZE = 1024*1024


def load_data(name):
    filepath = os.path.join(uzbl_forms_dir, name + '.yml.asc')
    data = {}

    try:
        data = yaml.load(str(gpg.decrypt_file(open(filepath, 'r'))))
    except:
        pass
    return data


def store_data(data, name, keys):
    filepath = os.path_join(uzbl_forms_dir, name + '.yml.asc')

    if not data:
        return True

    success = False
    try:
        f = open(filepath, 'w')
        f.write(str(gpg.encrypt(yaml.dump(data,
                                          default_flow_style=False,
                                          explicit_start=True), keys)))
        f.close()
        success = True
    except:
        pass

    return success


def send_javascript(script):
    response = ''
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(os.environ.get('UZBL_SOCKET', None))
        s.sendall('js {};\n'.format(script))
        response = s.recv(RECV_BUFSIZE)
        s.close()
    except:
        pass

    return response


def dump_window_form_data_list():
    response = send_javascript('JSON.stringify(uzbl.formfiller.dump())')
    _, json_retval = response.split('\n', 1)
    return yaml.load(json_retval)


def update_window_form_data(data):
    send_javascript('uzbl.formfiller.load({})'.format(json.dumps(data)))
    return 0


def notify_user(message):
    #send_javascript('alert("{}")'.format(message))
    dialog = gtk.MessageDialog(
        None,
        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
        gtk.MESSAGE_INFO,
        gtk.BUTTONS_OK,
        message)

    dialog.run()


def load_action():
    #data = load_data(filepath)
    #window_data = data.get(window_urlpath, None)
    #return update_window_form_data(window_data)
    pass


def store_action(keys):

    for form_data in dump_window_form_data_list():
        # for now, remove www. from start of hostname and index.* from end of
        # path name. Will re-examine this decision if it causes problems later.
        # alternatively, may want regex to filter www04, securewww, etc...
        hostname = re.sub('^www[^.]*\.', '', form_data['hostname'])
        pathname = re.sub('index\.[^.]+$', '', form_data['pathname'])
        form_data_dir = os.path.join(uzbl_forms_dir, 
                                     hostname, 
                                     *pathname.split('/'))



    retval = 0

    # save site form data and return result
    #retval = store_data(data, keys)

    #if retval:
    #    notify_user('Form data saved!')

    return retval


def main(argv=None):

    # ensure that forms directory exists and has secure permissions
    try:
        os.makedirs(uzbl_forms_dir, 0700)
    except OSError:
        os.chmod(uzbl_forms_dir, 0700)

    parser = ArgumentParser(description='form filler for uzbl')
    parser.add_argument('action', help='action to perform',
                        choices=['load', 'store'])
    parser.add_argument('-r', '--recipient', action='append',
                        help='gpg recipient, repeat for multiple, '
                             'required to store')

    args = parser.parse_args()

    retval = True
    if args.action == 'load':
        retval = load_action()
    elif args.action == 'store':
        if args.recipient is None or len(args.recipient) < 1:
            print "at least one recipient required to store!"
        retval = store_action(args.recipient)

    return retval


if __name__ == "__main__":
    sys.exit(main())
