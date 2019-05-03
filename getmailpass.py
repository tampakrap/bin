#!/usr/bin/env python3

import keyring
import socket
import sys


def get_passeval(account):
    hostname = socket.gethostname().split('.')[0]
    service = 'sites'

    if account == 'gmail':
        account = 'google'
        service = 'forkbomb.gr/{}/mutt'.format(hostname)
    elif account == 'seznam':
        account += '.cz'
    elif account == 'suse':
        account += '.de'
    elif account == 'novell':
        account += '.com'
    elif account == 'gentoo':
        service = 'various'
    try:
        passfile_content = keyring.get_password(service, account).split('\n')[0]
        return passfile_content
    except AttributeError:
        raise Exception("GPG key expired")

if __name__ == "__main__":
    try:
        print(get_passeval(sys.argv[1]))
    except Exception as e:
        sys.stderr.write(str(e))
        sys.exit(1)
