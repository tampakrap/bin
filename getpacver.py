#!/usr/bin/python

from bs4 import BeautifulSoup
from colorama import Fore
from pkg_resources import parse_version as V
import argparse
import contextlib
import json
import os
import osc.conf
import osc.core
import re
import rpm
import ssl
import sys
import urllib2

projects_packages = {
    'benchmark': ['forkbomb'],
    'devel:languages:python': ['python-django-auth-ldap', 'python-django-international', 'python-mockldap'],
    'devel:languages:ruby:extensions': ['rubygem-colored', 'rubygem-cri', 'rubygem-deep_merge', 'rubygem-faraday', 'rubygem-faraday_middleware',
                                        'rubygem-faraday_middleware-multi_json', 'rubygem-hub', 'rubygem-json_pure', 'rubygem-log4r',
                                        'rubygem-multi_json', 'rubygem-ruby-augeas', 'rubygem-systemu'],
    'devel:libraries:c_c++': ['augeas'],
    'devel:tools:building': ['colorgcc', 'colormake'],
    'devel:tools:scm:svn': ['python-svneverever', 'svn2git'],
    'home:sleep_walker:gentoo': ['eix', 'gentoolkit-dev', 'gentoo-syntax', 'gentoo-zsh-completions', 'portage-utils', 'python-gentoolkit',
                                 'python-portage', 'python-snakeoil', 'sandbox'],
    'network:utilities': ['libtorrent', 'nmcli-dmenu', 'rtorrent'],
    'security:privacy': ['password-store', 'python-pass_python_keyring'],
    'server:irc': ['bitlbee'],
    'utilities': ['pmount', 'uam'],
    'systemsmanagement:puppet': ['mcollective', 'puppet-dashboard', 'puppetdb', 'python-puppetboard', 'python-pypuppetdb', 'rubygem-augeas',
                                 'rubygem-facter', 'rubygem-hiera', 'rubygem-puppet', 'rubygem-puppet-lint', 'rubygem-r10k'],
    'Virtualization': ['virt-what'],
    'X11:Utilities': ['urxvt-font-size', 'urxvt-perls', 'urxvt-tabbedex', 'xautolock', 'xxkb'],
}

LISTINDEX = {
    'distfiles.gentoo.org': 'distfiles',
    'download.augeas.net': '',
    'ftp.debian.org': 'debian/pool/main/p/pmount',
    'get.bitlbee.org': 'src',
    'hartwork.org': 'public',
    'www.ibiblio.org': 'pub/linux/X11/screensavers',
    'home.tiscali.cz:8080': '~cz210552/distfiles',
    'people.redhat.com': '~rjones/virt-what/files/',
}

SOCIAL_VCS = ['github.com', 'bitbucket.org']
OBS_BASE_PATH = '/home/tampakrap/Repos/opensuse/obs'
RESULT_TMPL = '{:^15} {separ} {:^37} {separ} {:^26} {separ} {:^15} {separ} {:^8}' + Fore.RESET
CONTEXT = ssl._create_unverified_context()


class PkgServiceNotFoundError(Exception):
    pass


class PkgServiceNotImplementedError(Exception):
    pass


class PkgOutdatedError(Exception):
    pass


@contextlib.contextmanager
def silence(stdchan=sys.stdout):
    backup = os.dup(stdchan.fileno())
    dest_file = open(os.devnull, 'w')
    os.dup2(dest_file.fileno(), stdchan.fileno())
    yield
    os.dup2(backup, stdchan.fileno())
    dest_file.close()


class Package:
    rpmspec_name = None
    rpmspec_version = None
    upstream_name = None
    upstream_version = None
    service = None
    repo_owner = None
    repo_name = None
    _spec = None
    _spec_pkg = None

    def __init__(self, spec_path):
        self._spec = self._get_rpmspec(spec_path)
        self._spec_pkg = self._spec.packages[0].header
        self.rpmspec_name = self._get_rpmspec_name()
        self.rpmspec_version = self._get_rpmspec_version()
        self.upstream_name = self._get_upstream_name(self.rpmspec_name)
        self.service = self._get_service()
        self.upstream_version = self._get_upstream_version()

    def _get_rpmspec(self, spec_path):
        with silence(sys.stderr):
            spec = rpm.spec(spec_path)
        return spec

    def _get_rpmspec_name(self):
        return self._spec_pkg['name']

    def _get_upstream_name(self, name):
        return name.replace('python-', '').replace('rubygem-', '')

    def _get_rpmspec_version(self):
        return self._spec_pkg['version']

    def _get_service(self):
        for source in self._spec.sources:
            url = source[0]
            if url.startswith('http') or url.startswith('ftp'):
                obj = re.search('(https?|ftp)://([^/]*)(.*)', url)
                if obj.group(2) in SOCIAL_VCS:
                    self.repo_owner, self.repo_name = obj.group(3).split('/')[1:3]
                return obj.group(2)

        raise PkgServiceNotFoundError

    def _get_upstream_version(self):

        def clean_version(version):
            try:
                version = version.split('%s-' % self.upstream_name)[1]
            except IndexError:
                pass

            try:
                version = version.split('%s_' % self.upstream_name)[1]
            except IndexError:
                pass

            try:
                version = version.split('.tar')[0]
            except IndexError:
                pass

            version = version.replace('-src', '').replace('.tgz', '').replace('.orig', '').replace('-', '_')
            if version.startswith('v'):
                version = version[1:]

            return version.strip()

        def get_max_version(versions_list):
            curr_max = versions_list[0]
            for version in versions_list:
                if V(version) > V(curr_max):
                    curr_max = version
            return curr_max

        def from_listindex():
            versions = []
            with open('/tmp/listindex_%s' % self.service, 'r') as listindex:
                lines = listindex.readlines()
                for line in lines:
                    if re.search("^%s(-|_)[0-9]" % self.upstream_name, line):
                        versions.append(clean_version(line))
            return get_max_version(versions)

        if self.service == 'github.com':
            up_res = urllib2.urlopen('https://api.%s/repos/%s/%s/tags' % (self.service, self.repo_owner, self.repo_name))
            version = json.loads(up_res.read())[0]['name']
        elif self.service == 'pypi.python.org':
            up_res = urllib2.urlopen('https://%s/pypi/%s/json' % (self.service, self.upstream_name))
            version = json.loads(up_res.read())['info']['version']
        elif self.service == 'rubygems.org':
            up_res = urllib2.urlopen('https://%s/api/v1/gems/%s.json' % (self.service, self.upstream_name))
            version = json.loads(up_res.read())['version']
        elif self.service == 'downloads.sourceforge.net':
            up_res = urllib2.urlopen('https://%s/projects/%s/rss?limit=1' % ('.'.join(self.service.split('.')[1:]), self.upstream_name))
            version = BeautifulSoup(up_res.read(), 'html.parser').find('guid').contents[0]
        elif self.service == 'bitbucket.org':
            up_res = urllib2.urlopen('https://api.%s/1.0/repositories/%s/%s/tags' % (self.service, self.repo_owner, self.repo_name))
            version = sorted(json.loads(up_res.read()).keys(), reverse=True)[0]
        elif self.service.endswith('.googlecode.com'):
            up_res = urllib2.urlopen('https://code.google.com/feeds/p/%s/downloads/basic' % self.upstream_name)
            version = BeautifulSoup(up_res.read(), 'html.parser').find('entry').find('id').contents[0]
        elif self.service == 'git.zx2c4.com':
            up_res = urllib2.urlopen('http://%s/%s/log/' % (self.service, self.upstream_name))
            version = BeautifulSoup(up_res.read(), 'html.parser').find('a', 'tag-deco').contents[0]
        elif self.service in LISTINDEX.keys():
            version = from_listindex()
        else:
            raise PkgServiceNotImplementedError(self.service)

        return clean_version(version)

    def compare_versions(self):
        if self.upstream_version != self.rpmspec_version:
            raise PkgOutdatedError


def fetch_listindex(service, suburl):
    file_content = ''
    raw = urllib2.urlopen('http://%s/%s/' % (service, suburl), context=CONTEXT).read()
    links = BeautifulSoup(raw, 'html.parser').find_all('a')
    for link in links:
        content = link['href']
        if re.search("[a-z]+(-|_)[0-9\.]+(-alpha\.orig)?\.t(ar\.|gz)", content):
            file_content += content + '\n'
    with open('/tmp/listindex_%s' % service, 'w') as listindex:
        listindex.write(file_content)


def osc_co_or_up(PRJ_DIR_PATH, PKG_DIR_PATH, prj, pkg_dir):
    try:
        osc_pkg = osc.core.Package(PKG_DIR_PATH)
        if not args.no_osc_up:
            with silence():
                osc_pkg.update()
    except osc.oscerr.NoWorkingCopy:
        with silence():
            osc.core.checkout_package('https://api.opensuse.org', prj, pkg_dir, prj_dir=PRJ_DIR_PATH)


def print_pkg_status_line(status, pkg_dir, service, version, old, color):
    separator = Fore.RESET + '|' + color
    print(color + RESULT_TMPL.format(status, pkg_dir, service, version, old, separ=separator))

def pkg_check(PRJ_DIR_PATH, prj, pkg_dir):
    PKG_DIR_PATH = '%s/%s' % (PRJ_DIR_PATH, pkg_dir)
    osc_co_or_up(PRJ_DIR_PATH, PKG_DIR_PATH, prj, pkg_dir)
    try:
        pkg = Package('%s/%s.spec' % (PKG_DIR_PATH, pkg_dir))
    except PkgServiceNotFoundError:
        print_pkg_status_line('NO SERVICE', pkg_dir, 'No Service Found', '', '', Fore.RED)
    except PkgServiceNotImplementedError, e:
        print_pkg_status_line('UNKNOWN SERVICE', pkg_dir, e, '', '', Fore.RED)
    else:
        try:
            pkg.compare_versions()
            print_pkg_status_line("UP-TO-DATE", pkg.rpmspec_name, pkg.service, pkg.upstream_version, '', Fore.GREEN)
        except PkgOutdatedError:
            print_pkg_status_line("OUTDATED", pkg.rpmspec_name, pkg.service, pkg.upstream_version, pkg.rpmspec_version, Fore.YELLOW)

parser = argparse.ArgumentParser(description='Chech if openSUSE packages are up to date by comparing their versions with \
                                 the equivalent upstream packages.')
parser.add_argument('-l', '--listindex', choices=LISTINDEX.keys() + ['all'], help='Download new package lists from ListIndexes')
parser.add_argument('-p', '--package', nargs=1, help='Check only a specific package.')
parser.add_argument('--no-osc-up', action='store_true', help='Don\'t run `osc update` on local OBS package checkouts')
args = parser.parse_args()

if args.listindex:
    if 'all' in args.listindex:
        for service, suburl in LISTINDEX.iteritems():
            fetch_listindex(service, suburl)
    else:
        services = set(args.listindex) & set(LISTINDEX.keys())
        for service in services:
            fetch_listindex(service, LISTINDEX[service])

osc.conf.get_config()

print(RESULT_TMPL.format('STATUS', 'PACKAGE NAME', 'SERVICE', 'VERSION', 'OLD', separ='|'))
print(RESULT_TMPL.format('', '', '', '', '', separ='+').replace(' ','-'))

if args.package:
    for prj, pkg_dirs in projects_packages.iteritems():
        if args.package[0] in pkg_dirs:
            PRJ_DIR_PATH = '%s/%s' % (OBS_BASE_PATH, prj)
            pkg_check(PRJ_DIR_PATH, prj, args.package[0])
            break
else:
    for prj, pkg_dirs in projects_packages.iteritems():
        PRJ_DIR_PATH = '%s/%s' % (OBS_BASE_PATH, prj)
        for pkg_dir in pkg_dirs:
            pkg_check(PRJ_DIR_PATH, prj, pkg_dir)
