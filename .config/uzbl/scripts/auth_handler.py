#!/usr/bin/env python
# FIXME: pass default key through uzbl?
# move load and store out of login_popup to main

import gtk
import os
import re
import sys
import yaml

from argparse import ArgumentParser
from gnupg import GPG
from xdg.BaseDirectory import xdg_data_home

default_recipients = ['0xCB8FE39384C1D3F4']
gpg = GPG()
uzbl_site_data_dir = os.path.join(xdg_data_home, 'uzbl', 'site-data')


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


def gen_data_file(hostname):
    hostname = re.sub('^www[^.]*\.', '', hostname).lower()
    return os.path.join(uzbl_site_data_dir, hostname, 'auth.yml.asc')


def load_auth_data(hostname):
    return load_data_file(gen_data_file(hostname))


def store_auth_data(data, hostname):
    return store_data_file(data, default_recipients, gen_data_file(hostname))


def responseToDialog(entry, dialog):
    dialog.response(gtk.RESPONSE_OK)


def updatePassword(login, password, accounts):
    index = login.get_active()
    if -1 < index < len(accounts):
        password.set_text(accounts[index].get('password', ''))


def login_popup(hostname, realm):

    accounts = [
        {'username': 'user1', 'password': 'password1'},
        {'username': 'user2', 'password': 'password2'},
        {'username': 'user3', 'password': 'password3'},
        {'username': 'user4', 'password': 'password4'},
    ]

    login = gtk.combo_box_entry_new_text()
    for account in accounts:
        if 'username' in account:
            login.append_text(account['username'])

    password = gtk.Entry()
    password.set_visibility(False)

    vbox_entries = gtk.VBox()
    vbox_entries.pack_start(login)
    vbox_entries.pack_end(password)

    vbox_labels = gtk.VBox()
    vbox_labels.pack_start(gtk.Label("Login:"), False, 5, 5)
    vbox_labels.pack_end(gtk.Label("Password:"), False, 5, 5)

    hbox = gtk.HBox()
    hbox.pack_start(vbox_labels, True, True, 0)
    hbox.pack_end(vbox_entries, True, True, 0)

    dialog = gtk.MessageDialog(
        None,
        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
        gtk.MESSAGE_QUESTION,
        gtk.BUTTONS_OK_CANCEL,
        None)
    dialog.set_markup('{:s} at {:s}'.format(realm, hostname))
    dialog.format_secondary_markup("Please enter login and password:")

    login.child.connect("activate", responseToDialog, dialog)
    login.connect("changed", updatePassword, password, accounts)
    password.connect("activate", responseToDialog, dialog)

    dialog.vbox.pack_start(hbox)
    dialog.show_all()
    response = dialog.run()

    login_info = {'username': login.child.get_text(),
                  'password': password.get_text()}

    print login_info
    print login.get_active()

    dialog.destroy()

    #if realm_data:
    #    realm_data[0] = login_info
    #else:
    #    realm_data.append(login_info)
    #store_auth_data(site_data, hostname)

    return response, login_info


def main(argv=None):

    parser = ArgumentParser(description='auth handler for uzbl')
    parser.add_argument('zone', help='authentication zone')
    parser.add_argument('hostname', help='host or domain name')
    parser.add_argument('realm', help='authentication realm')
    parser.add_argument('repeat', help='repeat request')

    args = parser.parse_args()

    if args.repeat.lower() == 'true':
        return 1

    site_logins = load_auth_data(hostname)
    realm_logins = site_logins.get(realm, [])

    response, login_info = login_popup(args.hostname, args.realm, realm_logins)
    if (response != gtk.RESPONSE_OK):
        return 1

    print login_info.get('username', '')
    print login_info.get('password', '')

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
