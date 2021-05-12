#!/usr/bin/env python
# Abusive IP Grabber from MageMojo HOP

########## GLOBAL NEEDED THINGS | DO NOT CHANGE ##########
import os
import os.path
from os import path
import socket
import argparse
import subprocess
out = ""
err = ""

# Some Pretty Colors for logs
NC='\033[0m' # No Color
RED='\033[0;31m'
GREEN='\033[0;32m'

# Get UUID
parser = argparse.ArgumentParser()
parser.add_argument('-u','--uuid', action='store', dest='uuid', type=str, help="uuid of the instance")
args = parser.parse_args()

if args.uuid:
    # URL
    uuid = str(args.uuid)
    url = "https://magemojo.com/mojo_scripts/banlist.php?uuid={" + uuid + "}"
    #print(url)

    # GET IP list
    getlist = "cd /srv/.nginx/;curl " + url + " -o \'#1.list\'"
    os.system(getlist)

    # Loop through IPs in the list
    filesize = os.path.getsize("/srv/.nginx/" + uuid + ".list")
    if filesize == 0:
        print(RED + " Something is wrong. Source list not found or empty" + NC)
    else:
        do = "awk \'{print \"deny \"$0\";\"}\' /srv/.nginx/" + uuid + ".list | uniq > /srv/.nginx/server_level/" + uuid + ".conf"
        os.system(do)
        rm = "rm /srv/.nginx/" + uuid + ".list"
        os.system(rm)
        doreload = "/usr/share/stratus/cli nginx.update"
        nginxupdate = subprocess.run(["/usr/share/stratus/cli","nginx.update"], check=True)

        if "returncode=0" in str(nginxupdate):
            print(nginxupdate)
            print(GREEN + " List good. Reloaded nginx config" + NC)
        else:
            print(nginxupdate)
            mv = "mv /srv/.nginx/server_level/" + uuid + ".conf /srv/.nginx/server_level/" + uuid + ".failed"
            print(RED + " Nginx failed to reload: reverted" + NC)
            nginxupdate = subprocess.run(["/usr/share/stratus/cli","nginx.update"], check=True)
else:
    print(RED + " UUID was not specified. Can not continue" + NC)