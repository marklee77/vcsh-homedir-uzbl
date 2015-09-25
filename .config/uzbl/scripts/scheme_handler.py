#!/usr/bin/env python
import os
import subprocess
import sys
import urlparse

from argparse import ArgumentParser


def detach_open(cmd):
    # Thanks to the vast knowledge of Laurence Withers (lwithers) and this
    # message:
    # http://mail.python.org/pipermail/python-list/2006-November/587523.html
    if not os.fork():
        null = os.open(os.devnull, os.O_WRONLY)
        for i in range(3):
            os.dup2(null, i)
        os.close(null)
        subprocess.Popen(cmd)
    print 'USED'


def mailto_handler(url


def main(argv=None):

    parser = ArgumentParser(description='scheme handler for uzbl')
    parser.add_argument('uri', help='uri to operate on')

    args = parser.parse_args()

    u = urlparse.urlparse(args.uri)

    if u.scheme == 'mailto':
        # get subject from query string...
        detach_open(['urxvtcd', '-e', 'mutt', u.path])

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
