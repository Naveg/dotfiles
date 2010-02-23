#!/usr/bin/env python

import os
import sys
import subprocess
import ConfigParser as cp

CONFIG = 'branches.cfg'

def find_config(upfrom):
    '''Look for a branches config file up the tree from the given path'''
    path = os.path.abspath(upfrom)
    while True:
        cfgpath = os.path.join(path, CONFIG)
        if os.path.isfile(cfgpath):
            cfg = cp.SafeConfigParser()
            cfg.read(cfgpath)
            return cfg

        path, last = os.path.split(path)
        if last == '':
            raise Exception("No %s found." % CONFIG)


def find_docroot(upfrom):
    '''Look for an htdocs folder up the tree from
    the given path'''
    path = os.path.abspath(upfrom)
    while True:
        dirpath = os.path.join(path, 'htdocs')
        if os.path.isdir(dirpath):
            return dirpath

        path, last = os.path.split(path)
        if last == '':
            raise Exception("No docroot found. Are you in a Mahara working copy?")


def main():
    if len(sys.argv) < 2:
        raise Exception("You must specify the branch to checkout.")
    cfg = find_config(os.getcwd())
    branch = sys.argv[1]
    if not cfg.has_option('branches', branch):
        raise Exception("No configuration for branch %s." % branch)
    db = cfg.get('branches', branch)
    if not cfg.has_option('databases', db):
        raise Exception("No configuration for database %s." % db)
    user = cfg.get('databases', db)
    if not cfg.has_option('users', user):
        raise Exception("No configuration for user %s." % user)
    pw = cfg.get('users', user)
    docroot = find_docroot(os.getcwd())
    path = os.path.join(docroot, 'config.php')
    f = open(path, 'r')
    lines = f.readlines()
    f.close()
    for index, line in enumerate(lines):
        if '$cfg->dbname' in line:
            lines[index] = "$cfg->dbname = '%s';\n" % db
        elif '$cfg->dbuser' in line:
            lines[index] = "$cfg->dbuser = '%s';\n" % user
        elif '$cfg->dbpass' in line:
            lines[index] = "$cfg->dbpass = '%s';\n" % pw
    f = open(path, 'w')
    print 'Altering %s' % path
    f.write(''.join(lines))
    f.close()
    subprocess.call(['git', 'checkout', branch])

try:
    main()
except Exception, e:
    print e
