#!/usr/bin/env python

import lxml.html as lh
import urllib2
from sys import argv

serverlist = []
mirrorage = []
probe = []
laglist = []

def parse_mirror_status(option):
    if option == 'portage':
        url = 'http://mirrorstats.gentoo.org/rsync/'
        limit = '1 hour'
    elif option == 'distfiles':
        url = 'http://mirrorstats.gentoo.org/'
    else:
        print 'Not acceptable argument, please specify rsync or distfiles'
    statslist = 0
    doc = lh.parse(urllib2.urlopen(url))
    temp = doc.iter('td')
    for item in temp:
        if item.get('align') == 'RIGHT':
            if item.text_content().endswith('@'):
                serverlist.append(item.text_content())
            elif ( item.text_content().endswith('hours') or \
                    item.text_content().endswith('hour') or \
                    item.text_content().endswith('minutes') or \
                    item.text_content().endswith('days') ) and statslist == 0:
                mirrorage.append(item.text_content())
                statslist = 1
            elif ( item.text_content().endswith('hours') or \
                    item.text_content().endswith('hour') or \
                    item.text_content().endswith('minutes') or \
                    item.text_content().endswith('days') or \
                    item.text_content().endswith('renewed') ) and statslist == 1:
                probe.append(item.text_content())
                statslist = 0

def find_lagging_mirrors(limit):
    for i in range(len(mirrorage)):
        if mirrorage[i].endswith('hours'):
            temp = mirrorage[i].replace(' hours', '').replace(' hour', '')
            temp = int(temp) * 60
            if temp > limit:
                laglist.append('%d, %s' % (i, serverlist[i]))
        elif mirrorage[i].endswith('days'):
            temp = mirrorage[i].replace(' days', '')
            temp = float(temp) * 60 * 24
            laglist.append('%d, %s' % (i, serverlist[i]))
    for item in laglist:
        print item

def main():
    error = 'First argument needs to be portage or distfiles'
    try:
        if argv[1] not in ['portage', 'distfiles']:
            print error
    except IndexError:
        print error
        return
    option = argv[1]
    parse_mirror_status(option)
    #laglist.append(option)
    if option == 'rsync':
        find_lagging_mirrors(60)
    else:
        find_lagging_mirrors(480)

if __name__ == '__main__':
    main()
