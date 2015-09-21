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


def load_data_file(*args):
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


def store_data_file(data, keys, *args):

    if not data:
        return True

    file_path = os.path.join(*args)
    file_dir = os.path.dirname(file_path)

    try:
        os.makedirs(file_dir, 0700)
    except OSError:
        os.chmod(file_dir, 0700)

    dataout = yaml.dump(data, default_flow_style=False, explicit_start=True)

    success = False
    try:
        if keys is not None and len(keys) > 0:
            dataout = str(gpg.encrypt(dataout, keys))
        f = open(file_path, 'w')
        f.write(dataout)
        f.close()
        success = True
    except:
        pass

    return success


def gen_data_dir(href):
    parse_result = urlparse(href)

    hostname = re.sub('^www[^.]*\.', '', parse_result.hostname).lower()
    path = re.sub('index\.[^.]+$', '', parse_result.path).lower()

    return os.path.join(uzbl_forms_dir, hostname, *path.split('/'))


def load_page_data(href, *args):
    return load_data_file(gen_data_dir(href), *args)


def store_page_data(data, keys, href, *args):
    return store_data_file(data, keys, gen_data_dir(href), *args)


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


def notify_user(message):
    dialog = gtk.MessageDialog(
        None,
        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
        gtk.MESSAGE_INFO,
        gtk.BUTTONS_OK,
        message)

    dialog.run()


def get_form_data_list():
    response = send_javascript(
        'JSON.stringify(uzbl.formfiller.getFormDataList())')
    _, json_retval = response.split('\n', 1)
    retval = yaml.load(json_retval)
    if not isinstance(retval, list):
        retval = []
    return retval


def get_href_list():
    response = send_javascript('JSON.stringify(uzbl.formfiller.getHrefList())')
    _, json_retval = response.split('\n', 1)
    retval = yaml.load(json_retval)
    if not isinstance(retval, list):
        retval = []
    return retval


def update_forms(form_data_dict):
    send_javascript(
        'uzbl.formfiller.load({})'.format(json.dumps(form_data_dict)))
    return 0


def load_action():

    for href in get_href_list():
        page_data = load_page_data(href, 'data.yml.asc')
        for
    #data = load_data(filepath)
    #window_data = data.get(window_urlpath, None)
    return update_forms(window_data)


def store_action(keys):

    for dumped_form_data in get_form_data_list():
        form_name = dumped_form_data.get('name', '__noname__')
        form_href = dumped_form_data.get('href', 'noproto://undefined')
        form_data_list = [
            {'href': form_href,
             'elements': dumped_form_data.get('elements', [])}]
        page_data = load_page_data(form_href, 'data.yml.asc')
        page_data[form_name] = form_data_list
        store_page_data(page_data, keys, form_href, 'data.yml.asc')

        page_metadata = load_page_data(form_href, 'meta.yml')
        form_metadata = page_metadata.get(form_name, {})
        form_metadata.setdefault('autoloadIdx', -1)
        form_metadata['elements'] = list(set(e.get('name', None)
                                             for f in form_data_list
                                             for e in f.get('elements')))
        page_metadata[form_name] = form_metadata
        store_page_data(page_metadata, None, form_href, 'meta.yml')

    notify_user('Form data saved!')

    return 0


def main(argv=None):

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
