#!/usr/bin/env python
import os
import subprocess
import sys
import urlparse

from argparse import ArgumentParser

handlers = {}


def detach_open(cmd):
    # Thanks to the vast knowledge of Laurence Withers (lwithers) and this
    # message:
    # http://mail.python.org/pipermail/python-list/2006-November/587523.html
    subprocess.Popen(cmd)
    #if not os.fork():
    #    null = os.open(os.devnull, os.O_WRONLY)
    #    for i in range(3):
    #        os.dup2(null, i)
    #    os.close(null)
    #    subprocess.Popen(cmd)


def mailto_mutt_handler(url_result):
    """ This function does mutt-specific generates mutt-specific command-line
        options based on the passed url """

    terminal_app = os.getenv('TERMINAL', 'xterm')
    detach_open([terminal_app, '-e', 'mutt', url_result.geturl()])

handlers['mailto'] = mailto_mutt_handler


def main(argv=None):

    parser = ArgumentParser(description='scheme handler for uzbl')
    parser.add_argument('url', help='url to operate upon')

    args = parser.parse_args()

    url_result = urlparse.urlparse(args.url)

    handler_func = handlers.get(url_result.scheme, None)

    if handler_func:
        handler_func(url_result)
        print 'USED'

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
