#!/usr/bin/env python
# features to add:
#   - password gen
#   - license, description, docstrings
#   - form lookup methods: id, name, index, action, other?
#   - move hint style to css?
#   - keyringer?
#   - fix fails if no data loaded
import gtk
import json
import os
import re
import socket
import subprocess
import sys
import yaml

from argparse import ArgumentParser
from gnupg import GPG
from urlparse import urlparse
from xdg.BaseDirectory import xdg_data_home

gpg = GPG()
uzbl_site_data_dir = os.path.join(xdg_data_home, 'uzbl', 'site-data')

# if someone with more experience working with python sockets knows a better
# way to do this, email me some code or put in a github pull request.
RECV_BUFSIZE = 1024*1024


def notify_user(message):
    dialog = gtk.MessageDialog(
        None,
        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
        gtk.MESSAGE_INFO,
        gtk.BUTTONS_OK,
        message)

    dialog.run()


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


def store_data_file(data, recipients, *args):

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
        if recipients:
            dataout = str(gpg.encrypt(dataout, recipients))
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

    return os.path.join(uzbl_site_data_dir, hostname, 'forms',
                        *path.split('/'))


def load_page_data(href, *args):
    return load_data_file(gen_data_dir(href), *args)


def store_page_data(data, recipients, href, *args):
    return store_data_file(data, recipients, gen_data_dir(href), *args)


def eval_js(expr, default=None):
    retval = None
    try:
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect(os.environ.get('UZBL_SOCKET', None))
        s.sendall('js JSON.stringify({});\n'.format(expr.replace('@', '\@')))
        response = s.recv(RECV_BUFSIZE)
        s.close()
        retval = yaml.load(response.split('\n', 1)[1])
    except:
        pass

    if not retval:
        retval = default

    return retval


def load_action(index=-1):

    if index < 0:
        index = eval_js('++uzbl.formfiller.index', 0)

    form_data_list_page_dict = {}
    for href in eval_js('uzbl.formfiller.getHrefList()', []):
        page_data = load_page_data(href, 'data.yml.asc')
        if page_data:
            form_data_list_page_dict[href] = [
                form_data_list for form_data_list in
                page_data[index % len(page_data)]]

    if form_data_list_page_dict:
        eval_js('uzbl.formfiller.updateForms({})'.format(
            json.dumps(form_data_list_page_dict)))

    return 0


def store_action(index=-1, recipients=[], append=False):

    if index < 0:
        index = eval_js('uzbl.formfiller.index', -1)

    for href, form_data_list in eval_js(
            'uzbl.formfiller.getFormDataListPageDict()', {}).items():
        page_data = load_page_data(href, 'data.yml.asc')
        if page_data and index > -1 and not append:
            page_data[index % len(page_data)] = form_data_list
        else:
            page_data.append(form_data_list)
            eval_js('uzbl.formfiller.index = {:d}'.format(len(page_data) - 1))
        store_page_data(page_data, recipients, href, 'data.yml.asc')

        page_metadata = dict(load_page_data(href, 'meta.yml'))
        form_metadata_list = page_metadata.get('forms', [])
        if not form_metadata_list:
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


def detach_open(*args):
    # for to background and close stdin, stdout, stderr
    if not os.fork():
        for i in range(3):
            os.close(i)
        subprocess.Popen(args)
        sys.exit(0)


def edit_action():
    terminal = os.getenv('TERMINAL', 'xterm')
    editor = os.getenv('EDITOR', 'vi')

    for href in eval_js('uzbl.formfiller.getHrefList()', []):
        detach_open(terminal, '-e', editor,
                    os.path.join(gen_data_dir(href), 'data.yml.asc'))

    return 0


def auto_action():

    hint_form_data_list_page_dict = {}
    update_form_data_list_page_dict = {}
    for href in eval_js('uzbl.formfiller.getHrefList()', []):
        page_metadata = dict(load_page_data(href, 'meta.yml'))
        if page_metadata:
            hint_form_data_list_page_dict[href] = [
                form_data_list for form_data_list in
                page_metadata.get('forms', [])]
        if page_metadata.get('autoload', False):
            eval_js('uzbl.formfiller.index = 0')
            page_data = load_page_data(href, 'data.yml.asc')
            if page_data:
                update_form_data_list_page_dict[href] = [
                    form_data_list for form_data_list in
                    page_data[0]]

    if hint_form_data_list_page_dict:
        eval_js('uzbl.formfiller.hintForms({})'.format(
            json.dumps(hint_form_data_list_page_dict)))

    if update_form_data_list_page_dict:
        eval_js('uzbl.formfiller.updateForms({})'.format(
            json.dumps(update_form_data_list_page_dict)))

    return 0


def main(argv=None):

    parser = ArgumentParser(description='form filler for uzbl')
    parser.add_argument('action', help='action to perform',
                        choices=['load', 'store', 'append', 'edit', 'auto'])
    parser.add_argument('-i', '--index', type=int, default=-1,
                        help='data index to set or retrieve')
    parser.add_argument('-r', '--recipient', action='append',
                        help='gpg recipient, repeat for multiple, '
                             'required to store')

    args = parser.parse_args()

    retval = True
    if args.action == 'load':
        retval = load_action(args.index)
    elif args.action in ['store', 'append']:
        if args.recipient is None or len(args.recipient) < 1:
            print "at least one recipient required to store!"
        retval = store_action(args.index, args.recipient,
                              args.action == 'append')
    elif args.action == 'edit':
        retval = edit_action()
    elif args.action == 'auto':
        retval = auto_action()

    return retval


if __name__ == "__main__":
    sys.exit(main(sys.argv))
