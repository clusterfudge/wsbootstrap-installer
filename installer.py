#!/usr/bin/env python
#########################
#
# wsbootstrap installer
#
#########################

import json
import sys
import subprocess
import os
import errno
import zipfile

try:
    import httplib2
except:
    print("Failed to import httplib2. Try installing globally with easy_install or pip.")
    sys.exit(1)

WSBOOTSTRAP_REPO_URL="http://api.github.com/repos/clusterfudge/wsbootstrap"
GET_REF_RESOURCE = "/git/refs"
GET_TAGS_RESOURCE = "/tags"
GET_ZIPBALL_RESOURCE = "/zipball"

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def get(url, result_file=None):
    http = httplib2.Http()
    response, content = http.request(url)
    if result_file:
        with open(result_file, 'wb') as f:
            f.write(content)
    return content

# strip the separator arg from argv (if we're piping this script into an interpreter)
if len(sys.argv) > 0 and sys.argv[0] == '-':
    sys.argv = sys.argv[1:]

# allow installer to specify release from command line
# default is latest release, or latest git tag
release_name = "latest"
if len(sys.argv) > 0 and len(sys.argv[0].strip()) > 0:
    release_name = sys.argv[0]

if release_name == "latest":
    releases = json.loads(get(WSBOOTSTRAP_REPO_URL + GET_TAGS_RESOURCE))
    release_name = releases[0].get('name')
    release_ref = "tags/" + release_name
elif release_name[0] == "v":
    release_ref = "tags/" + release_name
else:
    release_ref = "heads/" + release_name


release_commit_url = WSBOOTSTRAP_REPO_URL + GET_REF_RESOURCE + "/" + release_ref
release_commit = json.loads(get(release_commit_url)).get('object').get('sha')

# download zipball
zipball_url = WSBOOTSTRAP_REPO_URL + GET_ZIPBALL_RESOURCE + "/" + release_commit
zipball_download_file = "/tmp/wsbootstrap-%s.zip" % release_name
print("Downloading " + zipball_url + "...")
get(zipball_url, zipball_download_file)

# extract zipfile into development directory
extract_location = os.path.join(os.path.expanduser('~'), 'development', 'wsbootstrap')
mkdir_p(extract_location)

zipref = zipfile.ZipFile(zipball_download_file, 'r')
zipref.extractall(extract_location)
zipref.close()

# link new install to current
current_link = os.path.join(extract_location, 'current')
if os.path.islink(current_link):
    os.remove(current_link)
elif os.path.exists(current_link):
    os.rename(current_link, current_link + '.bak')

installed_version = "clusterfudge-wsbootstrap-" + release_commit[:7]

os.symlink(os.path.join(extract_location, installed_version), current_link)

# link ~/.bashrc to current install, if not already
rc_file = os.path.join(os.path.expanduser('~'), '.bashrc')
if os.path.islink(rc_file):
    os.remove(rc_file)
elif os.path.exists(rc_file):
    os.rename(rc_file, rc_file + ".bak")

os.symlink(os.path.join(current_link, '.bashrc'), rc_file)
print("Installation complete. Start a new shell (or source your .bashrc file) to load wsbootstrap.")
print("$ . ~/.bashrc")
