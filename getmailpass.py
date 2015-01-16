#!/usr/bin/env python

import keyring
import socket
import sys


def get_passeval(account):
    if account == 'gmail':
        account = 'google'
        service = 'tampakrap.gr/%s/mutt' % socket.gethostname()
    elif account == 'gentoo':
        service = 'various'
    elif account == 'suse':
        account = 'suse.de'
        service = 'sites'
    elif account == 'novell':
        account = 'novell.com'
        service = 'sites'
    try:
        passfile_content = keyring.get_password(service, account).split('\n')[0]
        return passfile_content
    except AttributeError:
        raise Exception("GPG key expired")

if __name__ == "__main__":
    try:
        print(get_passeval(sys.argv[1]))
    except Exception, e:
        sys.stderr.write(str(e))
        sys.exit(1)
