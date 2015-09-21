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
from xdg.BaseDirectory import xdg_data_home

gpg = GPG()
uzbl_forms_dir = os.path.join(xdg_data_home, 'uzbl', 'formdata')

# if someone with more experience working with python sockets knows a better
# way to do this, email me some code or put in a github pull request.
RECV_BUFSIZE = 1024*1024


def load_data(*args):
    filepath = os.path.join(*args)
    data = {}

    try:
        if filepath[-4:] in ['.asc', '.gpg']:
            data = yaml.load(str(gpg.decrypt_file(open(filepath, 'r'))))
        else:
            data = yaml.load(open(filepath, 'r'))
    except IOError:
        pass
    return data


def store_data(data, keys, *args):
    filepath = os.path.join(*args)

    if not data:
        return True

    dataout = yaml.dump(data, default_flow_style=False, explicit_start=True)
    success = False
    try:
        if keys is not None and len(keys) > 0:
            dataout = str(gpg.encrypt(dataout, keys))
        f = open(filepath, 'w')
        f.write(dataout)
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


def get_window_href_list():
    response = send_javascript('JSON.stringify(uzbl.formfiller.getHrefList())')
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

    for dumped_form_data in dump_window_form_data_list():
        # for now, remove www. from start of hostname and index.* from end of
        # path name. Will re-examine this decision if it causes problems later.
        # alternatively, may want regex to filter www04, securewww, etc...
        formname = dumped_form_data.get('name', '__noname__')
        hostname = re.sub('^www[^.]*\.', '',
                          dumped_form_data['hostname']).lower()
        pathname = re.sub('index\.[^.]+$', '',
                          dumped_form_data['pathname']).lower()
        page_data_dir = os.path.join(uzbl_forms_dir,
                                     hostname,
                                     *pathname.split('/'))
        try:
            os.makedirs(page_data_dir, 0700)
        except OSError:
            os.chmod(page_data_dir, 0700)

        page_data = load_data(page_data_dir, 'data.yml.asc')
        form_data_list = page_data.get(formname, [])
        form_data_list = [{'href': dumped_form_data.get('href', None),
                           'elements': dumped_form_data.get('elements', [])}]
        page_data[formname] = form_data_list
        store_data(page_data, keys, page_data_dir, 'data.yml.asc')

        page_metadata = load_data(page_data_dir, 'meta.yml')
        form_metadata = page_metadata.get(formname, {})
        form_metadata.setdefault('autoloadIdx', -1)
        form_metadata['elements'] = list(set(e.get('name', None)
                                             for f in form_data_list
                                             for e in f.get('elements')))
        page_metadata[formname] = form_metadata
        store_data(page_metadata, None, page_data_dir, 'meta.yml')

    notify_user('Form data saved!')

    return 0


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
