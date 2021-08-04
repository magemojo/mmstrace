#!/usr/bin/env python
# Abusive IP Grabber from MageMojo HOP 1.1

########## GLOBAL NEEDED THINGS | DO NOT CHANGE ##########
import os
import os.path
from os import path
import ipaddress
import socket
import argparse
import subprocess
wlist=[] #declare list

# Some Pretty Colors for logs
NC='\033[0m' # No Color
RED='\033[0;31m'
GREEN='\033[0;32m'

# Make this file if non-existant
if str(path.exists("/srv/.nginx/white.list")) == "False":
    touchit="touch /srv/.nginx/white.list"
    os.system(touchit)

# Get UUID
parser = argparse.ArgumentParser()
parser.add_argument('-u','--uuid', action='store', dest='uuid', type=str, help="uuid of the instance")
args = parser.parse_args()

if args.uuid:
    # Put white.list in a pythonlist if not empty
    filesize = os.path.getsize("/srv/.nginx/white.list")
    if filesize == 0:
        print("No whitelist found or empty")
    else:
        with open("/srv/.nginx/white.list") as w:
            contents = w.readlines()
            for line in contents:
                line = line.replace("\n", "")
                wlist.append(line)
    # URL
    uuid = str(args.uuid)
    url = "https://magemojo.com/mojo_scripts/banlist.php?uuid={" + uuid + "}"
    #print(url)

    # GET IP list
    getlist = "cd /tmp/;curl " + url + " -o \'#1.list\'"
    os.system(getlist)

    # Check file exists or is not empty
    filesize = os.path.getsize("/tmp/" + uuid + ".list")
    if filesize == 0:
        print(RED + " Something is wrong. Source list not found or empty" + NC)
    else:
        # Build awk to add deny nginx format
        do = "awk \'{print \"deny \"$0\";\"}\' /tmp/" + uuid + ".list"

        # Make sure to ignore whitelisted IPs
        for ip in wlist:
            try:
                # Check if real IP
                if '/24' in ip:
                    ipaddress.ip_network(ip)
                else:
                    socket.inet_aton(ip)
                do = do + " | grep -v " + str(ip)
            except socket.error:
                print(RED + ip + " is not a valid IP in white.list" + NC) # Not legal


        # Tell it where to put them
        do = do + " | uniq > /srv/.nginx/server_level/" + uuid + ".conf"

        # Run it
        os.system(do)
        #print(do)  ## debug

        # Clean up tmp file
        rm = "rm /tmp/" + uuid + ".list"
        os.system(rm)

        # Reload nginx to apply changes
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