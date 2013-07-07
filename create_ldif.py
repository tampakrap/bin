#!/usr/bin/env python
# -*- coding: utf8 -*-

from Crypto.PublicKey import RSA
from datetime import datetime, timedelta
from edpwd import random_string
from passlib.hash import ldap_md5_crypt
from random import randrange, randint

ORGANIZATION = 'dc=tampakrap,dc=gr'
DOMAIN = ORGANIZATION.replace('dc=', '').replace(',', '.')

ORGANIZATIONAL_UNITS = (
    'users', 'groups', 'system',
)

BASE_DN = 'ou=%s,%s' % (ORGANIZATIONAL_UNITS[0], ORGANIZATION)

ROOTDN = 'Manager'
ROOTPW = 'secret'

LDIF_PATH = '/tmp/generated-ldif'

NAMES = (
    ('anole', ('Victor', 'Borkowski')),
    ('archangel', ('Waren', 'Worthington')),
    ('archer', ('Jude', 'Black')),
    ('armor', ('Hisako', 'Ichiki')),
    ('artie', ('Arhtur', 'Maddicks')),
    ('aurora', ('Jeanne-Marie', 'Beaubier')),
    ('banshee', ('Sean', 'Cassidy')),
    ('beak', ('Barnell', 'Bohusk')),
    ('beast', ('Henry', 'McCoy')),
    ('bedlam', ('Jesse', 'Aaronson')),
    ('bird-brain', ('Bird', 'Boy')),
    ('bishop', ('Lucas', 'Bishop')),
    ('blindfold', ('Ruth', 'Aldine')),
    ('blink', ('Clarice', 'Ferguson')),
    ('bling', ('Roxanne', 'Washington')),
    ('boom-boom', ('Tabitha', 'Smith')),
    ('box', ('Madison', 'Jeffries')),
    ('cable', ('Nathan Christopher', 'Summers')),
    ('cannonball', ('Samuel Zachary', 'Guthrie')),
    ('cerise', ('Cerise', 'Ksekoliar')),
    ('changeling', ('Kevin', 'Sydney')),
    ('choir', ('Irina', 'Clayton')),
    ('cloak', ('Tyrone', 'Johnson')),
    ('colossus', ('Piotr', 'Nikolaievitch')),
    ('copycat', ('Vanessa', 'Carlysle')),
    ('crusaderx', ('Bran', 'Braddock')),
    ('cyclops', ('Scott', 'Summers')),
    ('cypher', ('Douglas Aaron', 'Ramsey')),
    ('dagger', ('Tandy', 'Bowen')),
    ('danger', ('Danger', 'Room')),
    ('darwin', ('Armando', 'Muñoz'), ('Armando', 'Munoz')),
    ('daytripper', ('Amanda', 'Sefton')),
    ('dazzler', ('Alison', 'Blaire')),
    ('deadpool', ('Wade', 'Wilson')),
    ('domino', ('Neena', 'Thurman')),
    ('douglock', ('Kirk', 'Jones')),
    ('drnemesis', ('James Nicola', 'Brandley')),
    ('dust', ('Sooraya', 'Qadir')),
    ('elixir', ('Joshua', 'Foley')),
    ('energizer', ('Katie', 'Power')),
    ('eye-boy', ('Trevor', 'Smith')),
    ('fantomex', ('Charlie', 'Cluster')),
    ('feral', ('Maria', 'Callasantos')),
    ('firefist', ('Russell', 'Collins')),
    ('forearm', ('Marcus', 'Tucker')),
    ('frenzy', ('Joanna', 'Cargill')),
    ('gambit', ('Rémy', 'LeBeau'), ('Remy', 'LeBeau')),
    ('genesis', ('Evan', 'Sabahnur')),
    ('gentle', ('Nezhno', 'Abidemi')),
    ('gomi', ('Alphonsus', 'Lefszycic')),
    ('graymalkin', ('Jonas', 'Graymalkin')),
    ('greystone', ('Devlin', 'Greystone')),
    ('havok', ('Alexander', 'Summers')),
    ('hellion', ('Julian', 'Keller')),
    ('hope', ('Hope', 'Summers')),
    ('iceman', ('Robert', 'Drake')),
    ('indra', ('Paras', 'Gavaskar')),
    ('ink', ('Eric', 'Gitter')),
    ('jubilee', ('Jubilation', 'Lee')),
    ('juggernaut', ('Cain', 'Marko')),
    ('karma', ('Xian Coy', 'Manh')),
    ('kylun', ('Colin', 'McKay')),
    ('legion', ('David', 'Haller')),
    ('lifeguard', ('Heather', 'Cameron')),
    ('loa', ('Alani', 'Ryan')),
    ('longneck', ('William', 'Hanover')),
    ('m', ('Monet Yvette Clarisse Maria Therese', 'St. Croix')),
    ('magik', ('Illyana Nikolievna', 'Rasputina')),
    ('magma', ('Amara Juliana', 'Olivians Aquilla')),
    ('magneto', ('Max', 'Eisenhardt')),
    ('marrow', ('Sarah', 'Rushman')),
    ('match', ('Ben', 'Hamill')),
    ('mercury', ('Cessily', 'Kincaid')),
    ('micromax', ('Scott', 'Wright')),
    ('mimic', ('Calvin', 'Rankin')),
    ('mirage', ('Danielle', 'Moonstar')),
    ('mystique', ('Raven', 'Darkhölme'), ('Raven', 'Darkholme')),
    ('nightcrawler', ('Kurt', 'Wagner')),
    ('no-girl', ('Martha', 'Johansson')),
    ('northstar', ('Jean-Paul', 'Beaubier')),
    ('omerta', ('Paul', 'Provenzano')),
    ('onyx', ('Sidney', 'Green')),
    ('oya', ('Idie', 'Okonkwo')),
    ('phoenix', ('Jean', 'Grey')),
    ('pixie', ('Megan', 'Gwynn')),
    ('polaris', ('Lorna', 'Dane')),
    ('primal', ('Teon', 'Macik')),
    ('prodigy', ('David', 'Alleyne')),
    ('professorx', ('Charles', 'Xavier')),
    ('psylocke', ('Elizabeth', 'Braddock')),
    ('quicksilver', ('Pietro Django', 'Maximoff')),
    ('random', ('Marshall Evan', 'Stone III')),
    ('rictor', ('Julio Esteban', 'Richter')),
    ('risque', ('Gloria Dolorez', 'Muñoz'), ('Gloria Dolorez', 'Munoz')),
    ('rockslide', ('Santo', 'Vaccarro')),
    ('rogue', ('Anne Marie', 'Darkhölme'), ('Anne Marie', 'Darkhoelme')),
    ('sabra', ('Ruth', 'Bat-Seraph')),
    ('sabretooth', ('Victor', 'Creed')),
    ('shadowcat', ('Katherine Anne', 'Pryde')),
    ('shard', ('Shard', 'Bishop')),
    ('shark-girl', ('Iara', 'dos Santos')),
    ('shatterstar', ('Benjamin', 'Russell')),
    ('siryn', ('Theresa', 'Cassidy')),
    ('skids', ('Sally', 'Blevins')),
    ('slipstream', ('Davis', 'Cameron')),
    ('sprite', ('Jia', 'Jing')),
    ('storm', ('Ororo', 'Monroe')),
    ('sunfire', ('Shiro', 'Yoshida')),
    ('sunpyre', ('Leyu', 'Yoshida')),
    ('sunspot', ('Roberto', 'Da Costa')),
    ('surge', ('Noriko', 'Ashida')),
    ('sway', ('Suzanne', 'Chan')),
    ('tampakrap', ('Θοδωρής', 'Χατζημίχος'), ('Theo', 'Chatzimichos')),
    ('tempus', ('Eva', 'Bell')),
    ('thunderbird', ('John', 'Proudstar')),
    ('toad', ('Mortimer', 'Toynbee')),
    ('trance', ('Hope', 'Abbott')),
    ('transonic', ('Laurie', 'Tromette')),
    ('triage', ('Christopher', 'Muse')),
    ('vanisher', ('Telford', 'Porter')),
    ('velocidad', ('Gabriel', 'Cuohuelo')),
    ('vulcan', ('Gabriel', 'Summers')),
    ('warbird', ('Ava\'Dara', 'Naganandini')),
    ('warpath', ('James', 'Proudstar')),
    ('widget', ('Kate', 'Rasputin')),
    ('wolfsbane', ('Rahne', 'Sinclair')),
    ('wolverine', ('James', 'Howlett')),
    ('wraith', ('Hector', 'Rendoza')),
    ('x-23', ('Laura', 'Kinney')),
    ('x-man', ('Nate', 'Grey')),
    ('xorn', ('Kuan-Yin', 'Xorn')),
    ('zero', ('Kenji', 'Uedo')),
)
LEN_NAMES = len(NAMES) - 1

LOCATIONS = (
    ('Amsterdam, Netherlands', (52.373056, 4.892222)),
    ('Athens, Greece', (37.966667, 23.716667)),
    ('Barcelona, Spain', (41.383333, 2.183333)),
    ('Beijing, China', (39.913889, 116.391667)),
    ('Berlin, Germany', (52.516667, 13.383333)),
    ('Brussels, Belgium', (50.85, 4.35)),
    ('Budapest, Hungary', (47.471944, 19.050278)),
    ('Cairo, Egypt', (30.033333, 31.216667)),
    ('Dublin, Ireland', (53.347778, -6.259722)),
    ('Helsinki, Finland', (60.170833, 24.9375)),
    ('Johannesburg, South Africa', (-26.204444, 28.045556)),
    ('Larissa, Greece', (39.641667, 22.416667)),
    ('London, UK', (51.507222, -0.1275)),
    ('Los Angeles, USA', (34.05, -118.25)),
    ('Madrid, Spain', (40.4, -3.683333)),
    ('Moscow, Russia', (55.75, 37.616667)),
    ('Mumbai, India', (18.975, 72.825833)),
    ('New York, USA', (40.67, -73.94)),
    ('Oslo, Norway', (59.95, 10.75)),
    ('Paris, France', (48.8567, 2.3508)),
    ('Prague, Greece', (50.083333, 14.416667)),
    ('Rome, Italy', (41.9, 12.5)),
    ('San Francisco, USA', (37.783333, -122.416667)),
    ('Saint Petersburg, Russia', (59.95, 30.3)),
    ('Stockholm, Sweden', (59.329444, 18.068611)),
    ('Sydney, Australia', (-33.859972, 151.211111)),
    ('Thessaloniki, Greece', (40.65, 22.9)),
    ('Tokyo, Japan', (35.689506, 139.6917)),
    ('York, UK', (53.958333, -1.080278)),
    ('Vancouver, Canada', (49.25, -123.1)),
    ('Vienna, Austria', (48.208333, 16.373056)),
    ('Warsaw, Polland', (52.233333, 21.016667)),
    ('Zagreb, Croatia', (45.816667, 15.983333)),
    ('Zurich, Switzerland', (46.95, 7.45)),
)
LEN_LOCATIONS = len(LOCATIONS) - 1

IM_PROTOCOLS = ('xmpp', 'irc')
LEN_IM_PROTOCOLS = len(IM_PROTOCOLS) - 1

MAILS = ('yahoo.com', 'gmail.com', 'hotmail.com')
LEN_MAILS = len(MAILS) - 1

ROLES = {
    'special': (
        'security', 'trustees', 'docs', 'pr', 'council', 'forums', 'planet',
        'overlays', 'wiki', 'recruiters', 'retirement', 'staff'),
    'normal': (
        'mysql', 'ldap', 'server', 'kde', 'qt', 'desktop', 'virtualization',
        'python', 'ruby', 'php', 'perl', 'mozilla', 'gnome', 'games', 'office',
        'crypto', 'dotnet', 'hardened', 'amd64', 'alpha', 'ppc', 'alsa',
        'app-backup', 'cluster', 'java', 'kernel', 'media', 'mail', 'webapp',
        'pam', 'postgres', 'printing', 'samba', 'sci', 'sound', 'sparc',
        'suse', 'tex', 'video', 'vim', 'voip', 'x86', 'x11', 'xfce', 'bsd')
}

OPTIONAL_ATTRS = {
    'single_value': ('birthday', 'gentooLocation', 'gentooRoles',
                     'gentooLongitude', 'userPassword'),
    'multi_value': ('gentooGPGKey', 'gentooIM', 'gentooMentor', 'gentooDevBug',
                    'sshPublicKey', 'mail'),
}


# Date calculations used to get random birthdate
start_birthdate = datetime(1965, 1, 1)
end_birthdate = datetime(1995, 12, 31)
delta = end_birthdate - start_birthdate
birthdate_int_delta = delta.days * 24 * 60 * 60

# Date calculations used to get random gentoo join date
start_joindate = datetime(2003, 1, 1)
end_joindate = datetime.now()
delta = end_joindate - start_joindate
joindate_int_delta = delta.days * 24 * 60 * 60


def set_random_date(birthdate=False, join=False, start_date=False):
    if birthdate and join:
        raise Exception("You must enable only one of birthdate and join")
    if birthdate:
        int_delta = birthdate_int_delta
        start_date = start_birthdate
    elif join:
        int_delta = joindate_int_delta
        start_date = start_joindate
    else:
        start_date = datetime.strptime(start_date, '%Y/%m/%d')
        delta = end_joindate - start_date
        int_delta = delta.days * 24 * 60 * 60
    random_second = randrange(int_delta)
    date = start_date + timedelta(seconds=random_second)
    return str(date).split(' ')[0].replace('-', '/')


def set_password(secret):
    return ldap_md5_crypt.encrypt(secret)


def set_ssh_key():
    key_length = randint(1, 3) * 1024
    key = RSA.generate(key_length)
    return key.exportKey('OpenSSH')


def set_im(username):
    protocol = IM_PROTOCOLS[randint(0, LEN_IM_PROTOCOLS)] + '://'
    if protocol == 'xmpp://':
        mail = MAILS[randint(0, LEN_MAILS)]
        return '%s%s@%s' % (protocol, username, mail)
    elif protocol == 'irc://':
        return '%sirc.freenode.net/%s' % (protocol, username)


def set_mail(username):
    mail = MAILS[randint(0, LEN_MAILS)]
    return '%s@%s' % (username, mail)


def set_roles(content):
    enabled_roles = ''
    comma = ''
    for role in ROLES['special']:
        if randint(1, 10) == 1:
            if enabled_roles:
                comma = ', '
            enabled_roles += '%s%s' % (comma, role)
            content += """
gentooACL: %s.group""" % role

    for role in ROLES['normal']:
        if randint(1, 10) <= 2:
            if enabled_roles:
                comma = ', '
            enabled_roles += '%s%s' % (comma, role)

    content += """
gentooRoles: %s""" % enabled_roles

    return content


def set_optional_attr(category, attr, status, username, location, lat, lon):
    content = ''
    if status == 'user':
        if attr in ['gentooDevBug', 'gentooMentor', 'gentooRoles']:
            return content
    gentoolocation = None
    gentoomail = None
    mentor = []
    mail = []
    im = []
    if randint(1, 5) <= 4:
        if category == 'multi_value':
            repeat = randint(1, 3)
            for i in range(repeat):
                result = []
                if attr == 'gentooGPGKey':
                    result = random_string(40, letters=False, digits=False,
                                           hexdigits=True).upper()
                    content += """
gentooGPGFingerprint: 0x%s""" % result[-8:]
                elif attr == 'gentooIM':
                    candidate = set_im(username)
                    if candidate in im:
                        return ''
                    im.append(candidate)
                    result = candidate
                elif attr == 'gentooMentor':
                    mentor.append(username)
                    candidate = NAMES[randint(0, LEN_NAMES)][0]
                    if candidate in mentor:
                        return ''
                    mentor.append(candidate)
                    result = candidate
                elif attr == 'mail':
                    candidate = set_mail(username)
                    if candidate in mail:
                        return ''
                    mail.append(candidate)
                    result = candidate
                elif attr == 'gentooDevBug':
                    result = randint(1, 999999)
                elif attr == 'sshPublicKey':
                    result = set_ssh_key()
                content += """
%s: %s""" % (attr, result)
        else:
            result = ''
            if attr == 'birthday':
                result = set_random_date(birthdate=True)
            elif attr == 'gentooLocation':
                result = gentoolocation = location
            elif attr == 'gentooLongitude':
                result = lon
                content += """
gentooLatitude: %s""" % lat
            elif attr == 'userPassword':
                result = set_password('secret')
            if result:
                content += """
%s: %s""" % (attr, result)

    # gentooLocation, gentooRoles and mail @g.o are mandatory for developers
    if status == 'developer':
        if attr == 'gentooLocation' and not gentoolocation:
            content += """
%s: %s""" % (attr, location)
        elif attr == 'gentooRoles':
            content = set_roles(content)
        elif attr == 'mail' and not gentoomail:
            content += """
%s: %s@gentoo.org""" % (attr, username)
            gentoomail = True

    return content


def write_file(filename, content):
    f = open('%s/%s.ldif' % (LDIF_PATH, filename), 'w')
    f.write(content)
    f.close()


# Create organization
content = """
dn: %s
objectClass: organization
objectClass: dcObject
o: %s
dc: %s
structuralObjectClass: organization
description: %s RootDN
""" % (ORGANIZATION, DOMAIN, DOMAIN.split('.')[0], DOMAIN)
write_file('00-organization', content)

# Create organizational units
for org_unit in ORGANIZATIONAL_UNITS:
    content = """
dn: ou=%s,%s
objectClass: organizationalUnit
ou: groups
structuralObjectClass: organizationalUnit
""" % (org_unit, ORGANIZATION)
    write_file('01-%s' % org_unit, content)

# Create rootdn
content = """
dn: cn=%s,%s
objectClass: organizationalRole
objectClass: simpleSecurityObject
cn: %s
userPassword: %s
structuralObjectClass: organizationalRole
""" % (ROOTDN, ORGANIZATION, ROOTDN, set_password(ROOTPW))
write_file('02-%s' % ROOTDN, content)

# Create users
uidNumber = 999
for person in NAMES:
    uidNumber += 1

    try:
        nickname, full_name, gecos = person
    except ValueError:
        nickname, full_name = person
        gecos = full_name
    first_name, last_name = full_name
    full_name = ' '.join(full_name)
    gecos = ' '.join(gecos)

    status = randint(1, 10)
    if status <= 4:
        status = 'user'
    elif status <= 8:
        status = 'developer'
    else:
        status = 'retired'

    content = """
dn: uid=%s,%s
uid: %s
cn: %s
givenName: %s
sn: %s
shadowMax: 99999
shadowWarning: 15
shadowInactive: 15
loginShell: /bin/bash
homeDirectory: /home/%s
gecos: %s
gidNumber: 100
uidNumber: %d
objectClass: top
objectClass: person
objectClass: organizationalPerson
objectClass: inetOrgPerson
objectClass: posixAccount
objectClass: shadowAccount
objectClass: ldapPublicKey
objectClass: gentooGroup
structuralObjectClass: inetOrgPerson
gentooACL: user.group""" % (nickname, BASE_DN, nickname, full_name, first_name,
                            last_name, nickname, gecos, uidNumber)

    # Foundation member
    if randint(1, 2) == 1:
        content += """
gentooACL: foundation.group"""

    # Set randomly a subset of the following attrs
    # Their content and number of values is also random
    location, coordinates = LOCATIONS[randint(0, LEN_LOCATIONS)]
    lat, lon = coordinates

    for category, attrs in OPTIONAL_ATTRS.items():
        for attr in attrs:
            content += set_optional_attr(category, attr, status, nickname,
                                         location, lat, lon)

    # Only for developers and retired developers
    if status == 'developer' or status == 'retired':
        join_date = set_random_date(join=True)
        content += """
gentooJoin: %s""" % join_date

    # Only for retired developers
    if status == 'retired':
        content += """
gentooACL: retired.group
gentooRetire: %s""" % set_random_date(start_date=join_date)

    # Only for developers
    if status == 'developer':
        content += """
objectClass: gentooDevGroup
gentooACL: dev.group
gentooACL: user.group
gentooACL: cvs.gentoo.org
gentooACL: dev.gentoo.org"""

    content += '\n'

    write_file('03-%s' % nickname, content)
