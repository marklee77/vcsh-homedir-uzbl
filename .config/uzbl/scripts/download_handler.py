#!/usr/bin/env python

import gtk
import os

dialog = gtk.FileChooserDialog("Save Download As...",
                               None,
                               gtk.FILE_CHOOSER_ACTION_SAVE,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_SAVE, gtk.RESPONSE_OK))
dialog.set_default_response(gtk.RESPONSE_OK)

dialog.set_current_folder(os.path.join(os.getenv('HOME'), 'Downloads'))
dialog.set_current_name('test.txt')

response = dialog.run()
if response == gtk.RESPONSE_OK:
    filename = dialog.get_filename()
    if os.path.isfile(filename):
        confirm = gtk.MessageDialog(
            None,
            gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
            gtk.MESSAGE_INFO,
            gtk.BUTTONS_OK_CANCEL,
            "Overwrite Existing File?")
        response = confirm.run()
        confirm.destroy()
        if response == gtk.RESPONSE_OK:
            print "Overwrite!"
        else:
            print "Don't Overwrite!"

    print dialog.get_filename()

dialog.destroy()
