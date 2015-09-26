#!/usr/bin/env python
# FIXME; how to handle cancel?

import gtk
import os
import sys

from argparse import ArgumentParser
from xdg.BaseDirectory import xdg_data_home

uzbl_site_data_dir = os.path.join(xdg_data_home, 'uzbl', 'site_data')


def responseToDialog(entry, dialog, response):
    dialog.response(response)


def login_popup(authInfo, authHost, authRealm):
    dialog = gtk.MessageDialog(
        None,
        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
        gtk.MESSAGE_QUESTION,
        gtk.BUTTONS_OK_CANCEL,
        None)
    dialog.set_markup('%s at %s' % (authRealm, authHost))

    login = gtk.Entry()
    password = gtk.Entry()
    password.set_visibility(False)

    login.connect("activate", responseToDialog, dialog, gtk.RESPONSE_OK)
    password.connect("activate", responseToDialog, dialog, gtk.RESPONSE_OK)

    hbox = gtk.HBox()

    vbox_entries = gtk.VBox()
    vbox_labels = gtk.VBox()

    vbox_labels.pack_start(gtk.Label("Login:"), False, 5, 5)
    vbox_labels.pack_end(gtk.Label("Password:"), False, 5, 5)

    vbox_entries.pack_start(login)
    vbox_entries.pack_end(password)

    dialog.format_secondary_markup("Please enter username and password:")
    hbox.pack_start(vbox_labels, True, True, 0)
    hbox.pack_end(vbox_entries, True, True, 0)

    dialog.vbox.pack_start(hbox)
    dialog.show_all()
    rv = dialog.run()

    output = login.get_text() + "\n" + password.get_text()
    dialog.destroy()
    return rv, output


def main(argv=None):

    parser = ArgumentParser(description='auth handler for uzbl')
    parser.add_argument('zone', help='authentication zone')
    parser.add_argument('host', help='host or domain name')
    parser.add_argument('realm', help='authentication realm')
    parser.add_argument('repeat', type=bool, help='repeat request')

    args = parser.parse_args()

    if args.repeat:
        return 1

    response, data = login_popup(args.zone, args.host, args.realm)
    if (response != gtk.RESPONSE_OK):
        return 1

    print data.get('username', '')
    print data.get('password', '')

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
