#!/usr/bin/env python3

# Take an mbox HTML message (e.g. from mutt), split it using munpack
# (a separate program), and rewrite it so it can be viewed in an
# external browser.
# Can be run from within a mailer like mutt, or independently
# on a single message file.
#
# Usage: viewhtmlmail
#
# Inspired by John Eikenberry <jae@zhar.net>'s view_html_mail.sh
# which sadly no longer works, at least with mail from current Apple Mail.
#
# Copyright 2013 by Akkana Peck. Share and enjoy under the GPL v2 or later.
# Changes:
#   Holger Klawitter 2014: create a secure temp file and avoid temp mbox

# To use it from mutt, put the following lines in your .muttrc:
# macro  index  <F10>  "<pipe-message>~/bin/viewhtmlmail\n" "View HTML in browser"
# macro  pager  <F10>  "<pipe-message>~/bin/viewhtmlmail\n" "View HTML in browser"

import os, sys
import re
import time
import shutil
import email, mimetypes
import tempfile

def view_html_message(tmpdir):

    msg = email.message_from_string(sys.stdin.read())

    html_part = None
    counter = 1
    subfiles = []
    for part in msg.walk():

        # print ""

        # part has, for example:
        # items: [('Content-Type', 'image/jpeg'), ('Content-Transfer-Encoding', 'base64'), ('Content-ID', '<14.3631871432@web82503.mail.mud.yahoo.com>'), ('Content-Disposition', 'attachment; filename="ATT0001414.jpg"')]
        # keys: ['Content-Type', 'Content-Transfer-Encoding', 'Content-ID', 'Content-Disposition']
        # values: ['image/jpeg', 'base64', '<14.3631871432@web82503.mail.mud.yahoo.com>', 'attachment; filename="ATT0001414.jpg"']

        # multipart/* are just containers
        #if part.get_content_maintype() == 'multipart':
        if part.is_multipart() or part.get_content_type == 'message/rfc822':
            continue

        if part.get_content_subtype() == 'html':
            if html_part:
                print("Eek, more than one html part!")
            html_part = part

        # Save it to a file in the temp dir.
        filename = part.get_filename()
        if not filename:
            ext = mimetypes.guess_extension(part.get_content_type())
            if not ext:
                # Use a generic bag-of-bits extension
                ext = '.bin'
            filename = 'part-%03d%s' % (counter, ext)

        # Applications should really sanitize the given filename so that an
        # email message can't be used to overwrite important files.
        # As a first step, guard against ../
        if '../' in filename:
            print(f"Eek! Possible security problem in filename {filename}")
            continue

        filename = os.path.join(tmpdir, filename)

        # print "%10s %5s %s" % (part.get_content_type(), ext, filename)

        # Mailers may use Content-Id or Content-ID (or, presumably, various
        # other capitalizations). So we can't just look it up simply.
        content_id = None
        for k in part.keys():
            if k.lower() == 'content-id':
                # Remove angle brackets, if present.
                # part['Content-Id'] is unmutable -- attempts to change it
                # are just ignored -- so copy it to a local mutable string.
                content_id = part[k]
                if content_id.startswith('<') and content_id.endswith('>'):
                    content_id = content_id[1:-1]

                subfiles.append({ 'filename': filename,
                                  'Content-Id': content_id })
                counter += 1
                fp = open(filename, 'wb')
                fp.write(part.get_payload(decode=True))
                # print "wrote", os.path.join(tmpdir, filename)
                fp.close()
                break     # no need to look at other keys

        if not content_id:
            print(f"{filename} doesn't have a Content-Id, not saving")
            # print "keys:", part.keys()

    # for sf in subfiles:
    #     print sf

    # We're done saving the parts. It's time to save the HTML part.
    htmlfile = os.path.join(tmpdir, "viewhtml.html")
    fp = open(htmlfile, 'wb')
    htmlsrc = html_part.get_payload(decode=True)

    # Substitute all the filenames for CIDs:
    for sf in subfiles:
        htmlsrc = re.sub('cid: ?' + sf['Content-Id'],
                         'file://' + sf['filename'],
                         htmlsrc, flags=re.IGNORECASE)

    fp.write(htmlsrc)
    fp.close()

    # Now we have the file. Call firefox on it.
    print(f"Calling firefox for file://{htmlfile}")
    os.system("firefox -new-window file://" + htmlfile)

    # Wait a while to make sure firefox has loads the imgaes, then clean up.
    time.sleep(6)
    shutil.rmtree(tmpdir)

if __name__ == '__main__':
    tmpdir = tempfile.mkdtemp()
    view_html_message(tmpdir)
