#!/usr/bin/env python
# features to add:
#   - autosubmit
#   - password generation
#   - form lookup methods: id, name, index, action, other?
#   - reorg and cleanup...
#   - keyringer?
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
    data = []

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
        s.sendall('js {};\n'.format(script.replace('@', '\@')))
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


def get_form_data_list_page_dict():
    response = send_javascript(
        'JSON.stringify(uzbl.formfiller.getFormDataListPageDict())')
    _, json_retval = response.split('\n', 1)
    retval = yaml.load(json_retval)
    if not isinstance(retval, dict):
        retval = {}
    return retval


def get_href_list():
    response = send_javascript('JSON.stringify(uzbl.formfiller.getHrefList())')
    _, json_retval = response.split('\n', 1)
    retval = yaml.load(json_retval)
    if not isinstance(retval, list):
        retval = []
    return retval


def get_index():
    response = send_javascript('JSON.stringify(uzbl.formfiller.index)')
    _, json_retval = response.split('\n', 1)
    retval = yaml.load(json_retval)
    if not isinstance(retval, int):
        retval = 0
    return retval


def get_incr_index():
    response = send_javascript('JSON.stringify(uzbl.formfiller.index++)')
    _, json_retval = response.split('\n', 1)
    retval = yaml.load(json_retval)
    if not isinstance(retval, int):
        retval = 0
    return retval


def update_forms(form_data_list_page_dict):

    if len(form_data_list_page_dict) < 1:
        return 0

    send_javascript('uzbl.formfiller.updateForms({})'.format(
        json.dumps(form_data_list_page_dict)))
    return 0


def hint_forms(form_data_list_page_dict):

    if len(form_data_list_page_dict) < 1:
        return 0

    send_javascript('uzbl.formfiller.hintForms({})'.format(
        json.dumps(form_data_list_page_dict)))
    return 0


def load_action(index):

    if index < 0:
        index = get_incr_index()

    form_data_list_page_dict = {}
    for href in get_href_list():
        page_data = load_page_data(href, 'data.yml.asc')
        if len(page_data) > 0:
            form_data_list_page_dict[href] = [
                form_data_list for form_data_list in
                page_data[index % len(page_data)]]

    return update_forms(form_data_list_page_dict)


def store_action(index, keys):

    if index < 0:
        index = get_index()

    for href, form_data_list in get_form_data_list_page_dict().items():
        page_data = load_page_data(href, 'data.yml.asc')
        if len(page_data) > 0:
            page_data[index % len(page_data)] = form_data_list
        else:
            page_data = [form_data_list]
        store_page_data(page_data, keys, href, 'data.yml.asc')

        page_metadata = dict(load_page_data(href, 'meta.yml'))
        form_metadata_list = page_metadata.get('forms', [])
        if len(form_metadata_list) < 1:
            for form_data in form_data_list:
                form_metadata = {}
                form_name = form_data.get('name', None)
                if form_name is not None:
                    form_metadata['name'] = form_name
                form_metadata['elements'] = [e.get('name', None) for e in
                                             form_data.get('elements', [])]
                form_metadata_list.append(form_metadata)
        page_metadata['forms'] = form_metadata_list
        store_page_data(page_metadata, None, href, 'meta.yml')

    notify_user('Form data saved!')

    return 0


def auto_action():

    hint_form_data_list_page_dict = {}
    update_form_data_list_page_dict = {}
    for href in get_href_list():
        page_metadata = load_page_data(href, 'meta.yml')
        if len(page_metadata) > 0:
            hint_form_data_list_page_dict[href] = [
                form_data_list for form_data_list in
                page_metadata.get('forms', [])]
        if page_metadata.get('autoload', False):
            get_incr_index()
            page_data = load_page_data(href, 'data.yml.asc')
            if len(page_data) > 0:
                update_form_data_list_page_dict[href] = [
                    form_data_list for form_data_list in
                    page_data[0]]

    hint_forms(hint_form_data_list_page_dict)
    update_forms(update_form_data_list_page_dict)
    return 0


def main(argv=None):

    parser = ArgumentParser(description='form filler for uzbl')
    parser.add_argument('action', help='action to perform',
                        choices=['load', 'store', 'auto'])
    parser.add_argument('-i', '--index', type=int, default=-1,
                        help='data index to set or retrieve')
    parser.add_argument('-r', '--recipient', action='append',
                        help='gpg recipient, repeat for multiple, '
                             'required to store')

    args = parser.parse_args()

    retval = True
    if args.action == 'load':
        retval = load_action(args.index)
    elif args.action == 'store':
        if args.recipient is None or len(args.recipient) < 1:
            print "at least one recipient required to store!"
        retval = store_action(args.index, args.recipient)
    elif args.action == 'auto':
        retval = auto_action()

    return retval


if __name__ == "__main__":
    sys.exit(main())
