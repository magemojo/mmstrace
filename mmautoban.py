#!/usr/bin/env python
# MageMojo AutoBan
# v1.5
# Auto-add IPs related to carding attacks
# Cron should be set to (time-1)


########## GLOBAL NEEDED THINGS | DO NOT CHANGE ##########
import datetime
import os
import os.path
from os import path
import subprocess
import argparse
import socket

########## GLOBAL VARIABLES ##########

# This is the path to the nginx log files
logfile = "/log/access.log"
logfile2 = "/log/access.log.1"

# This is the path to the nginx conf files
nginxfile = "/srv/.nginx/server_level/mmautoban.conf"
nginxfilecarts = "/srv/.nginx/server_level/mmautobancarts.conf"
nginxtor = "/srv/.nginx/server_level/mmautobantor.conf"
#nginxfile = "/srv/mmautoban/test/mmautoban.conf" #testingonly
#nginxfilecarts = "/srv/mmautoban/test/mmautobancarts.conf" #testingonly
#nginxtor = "/srv/mmautoban/test/mmautobantor.conf" #testingonly

# MageMojo Autoban absolute path MUST BE A TRAILING /
mmpath = "/srv/mmautoban/"
#mmpath = "/srv/mmautoban/test/" #testingonly

# Check if files above exist. If they don't, create them.
if str(path.exists(nginxfile)) == "False":
    touchit="touch " + nginxfile
    os.system(touchit)
if str(path.exists(nginxfilecarts)) == "False":
    touchit="touch " + nginxfilecarts
    os.system(touchit)
if str(path.exists(nginxtor)) == "False":
    touchit="touch " + nginxtor
    os.system(touchit)

# How many minutes ago of logfile should we check
time = -1

# How many minutes ago should we check for attacks before unbanning?
utime = -15

# How many attacks should be considered "an active attack" in utime above
activelimit = 10

# Some Pretty Colors for logs
NC='\033[0m' # No Color
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
PINK='\033[0;35m'
PURPLE='\033[0;95m'
GREEN='\033[0;32m'

# Update location for TOR exit node list
torurl = "https://check.torproject.org/torbulkexitlist"
torfile = "torbulkexitlist"


########## GLOBAL GET TIME VARS ##########

# Get Current Date/Time
getnow = datetime.datetime.now()
now = getnow.strftime("%d/%b/%Y:%H:%M")
now = datetime.datetime.strptime(now, '%d/%b/%Y:%H:%M')

# get exact time for "var time set" and "var timestatic set" minutes ago
ago = now + datetime.timedelta(minutes = time)
uago = now + datetime.timedelta(minutes = utime)

#convert to right format to use as string for search
n = now.strftime("%d\/%b\/%Y:%H:%M")
f = ago.strftime("%d\/%b\/%Y:%H:%M")
u = uago.strftime("%d\/%b\/%Y:%H:%M")


######### GLOBAL ARGUMENT MAGIC AKA WHAT ARE WE DOING? ##########
parser = argparse.ArgumentParser()
parser.add_argument('-c','--carding', action='store', dest='carding', type=int,
    help="blocks carding attacks at <num> bad attempts per IP or cart. 1=AGGRESSIVE & is meant for active attacks.")
parser.add_argument('-u', '--unban', action='store_true',
    help="unbans IPs & carts (from carding attacks) unless attack is active")
parser.add_argument('-t', '--torexits', action='store_true',
    help="blocks TOR exit nodes")
args = parser.parse_args()

######### GLOBAL FUNCTION ###########
def doban(line,file):
    global reload
    with open(file) as nfile:

        # Check IP is legit (in case file format has changed in source)
        # Then block if not already blocked
        try:
            socket.inet_aton(line)
            linetest = line + ";"

            if linetest in nfile.read():
                print(n + " " + line + " already added to blocks")
            else:
                ban = "echo 'deny " + line + ";' >> " + file
                os.system(ban)
                print(n + PINK + " " + line + RED + " BLOCKED" + NC)
                reload = 1

        except socket.error:
            print(RED + line + " is not a valid IP?" + NC) # Not legal

def savecounts(thing):
        #save cart or ip in savecountsfile
        global maxcount
        global maxreached
        if str(path.exists(mmpath + 'savecounts.tally')) == "True":
            with open(mmpath + 'savecounts.tally') as sfile:
                if thing in sfile.read():
                    gettally = os.popen("grep -m1 " + thing + " " + mmpath + "savecounts.tally | awk -F ',' '{print $2}'").read().replace("\n", "")
                    newtally = int(gettally)+1
                    sedtally = "sed -i 's/\(" + str(thing) + ",\)\(.*\)/\1" + str(thing) + "," + str(newtally) + "/' " + mmpath + "savecounts.tally"
                    #print(sedtally)
                    os.system(sedtally)
                    if newtally >= maxcount:
                        maxreached=1
                        return maxreached
                else:
                    save = "echo '" + str(thing) + ",1 ' >> " + mmpath + "savecounts.tally"
                    os.system(save)
                    if maxcount==1:
                        maxreached=1
                        return maxreached
                    else:
                        maxcount=0
                        return maxreached
        else:
           save = "echo '" + str(thing) + ",1 ' > " + mmpath + "savecounts.tally"
           os.system(save)
           if maxcount==1:
               maxreached=1
               return maxreached
           else:
               maxcount=0
               return maxreached


######### CARDING ATTACKS --c --carding argument #########
if args.carding >= 1:
    global maxcount
    maxcount = int(args.carding)

    ########## CA FUNCTIONS ##########
    def dobancart(cartid):
        #deny CART in nginx if not already there
        with open(nginxfilecarts) as nfile:
            if cartid in nfile.read():
                print(n + " " + cartid + " already added to blocks")
            else:
                bancart = "echo 'if ($request_uri ~ " + cartid + ") { return 403; }' >> " + nginxfilecarts
                os.system(bancart)
                print(n + " " + PURPLE + cartid + RED + " BLOCKED" + NC)
                reload = 1

    ########## CA CHECK LOGS FOR ATTACKERS ##########

    # Check logs for IPs with cart adds
    checkcart = "sed -rne '/" + f + "/,/" + n + "/ p' " + logfile + " | grep /checkout/cart/add/uenc/ | grep product | grep POST > " + mmpath + "foundcart.log"
    #checkcart = "cat " + logfile + " | grep /checkout/cart/add/uenc/ | grep product | grep POST > " + mmpath + "foundcart.log"
    os.system(checkcart)

    # Check logs for payment API with 400 response
    checkapi = "sed -rne '/" + f + "/,/" + n + "/ p' " + logfile + " | grep V1/guest-carts | grep payment-information | grep POST | grep ' 400 ' > " + mmpath + "foundapi.log"
    #checkapi = "cat " + logfile + " | grep rest/default/V1/guest-carts | grep payment-information | grep POST | grep ' 400 ' > " + mmpath + "foundapi.log"
    os.system(checkapi)


    ########## CA PROCESS FINDINGS AND BLOCK IF DETERMINED FAKE ##########

    # Check if anything is found this go for cart adds
    filesize = os.path.getsize(mmpath + "foundcart.log")
    if filesize == 0:
        print(n + GREEN + " No cart adds found" + NC)
    else:
        # GET IPs
        getips = "awk {'print $1'} " + mmpath + "foundcart.log | sort | uniq | sort -n  > " + mmpath + "ipscart.log"
        os.system(getips)

        # Loop through found IPs that added to cart
        with open(mmpath + "ipscart.log") as f:
            contents = f.readlines()
            for line in reversed(contents):
                line = line.replace("\n", "")

                # Check logs for previous static file access or customer load section
                #checkstatic = "sed -rne '/" + s + "/,/" + n + "/ p' " + logfile + " | grep " + line + " | grep static > " + mmpath + "static.log"
                checkstatic = "grep " + line + " " + logfile + " | grep static > " + mmpath + "static.log"
                checkload = "grep " + line + " " + logfile + " | grep customer/section/load >> " + mmpath + "static.log"
                os.system(checkstatic)
                os.system(checkload)
                sfilesize = os.path.getsize(mmpath + "static.log")

                # If there has been no access to static files then block IP, otherwise check for excessive hits to cart
                if sfilesize == 0:
                    # ban it
                    print(n + " " + PINK + line + NC + " Logging for no static or reload")
                    if savecounts(line) == 1:
                        doban(line,ngixfile)
                else:
                    # Check excessive hits to addcart URL in general /checkout/cart/add/uenc/
                    hits = os.popen("grep " + line + " " + logfile + " | grep 'POST /checkout/cart/add/uenc/' | wc -l").read().replace("\n", "")
                    hits = int(hits)
                    if hits > 100:
                        #ban it
                        if str(66.249) in line:
                            print(n + RED + " Can't block for cartadd " + PINK + LINE + RED + ". Google Bot." + NC)
                        #elif "127.0.0.1" in line:
                            #print(n + RED + " Can't block for cartadd " + PINK + LINE + RED + ". OtherWhitelisted IP." + NC)
                        else:
                            print(n + " " + PINK + line + NC + " Logging for addcart count " + str(hits))
                            if savecounts(line) == 1:
                                doban(line,nginxfile)
                    else:
                        print(n + " " + PINK + line + GREEN + " Addcart appears legit" + NC)


    # Check if anything is found this go for API attacks
    filesize = os.path.getsize(mmpath + "foundapi.log")
    if filesize == 0:
        print(n + GREEN + " No carding attacks found" + NC)
    else:
        # GET IPs
        getips = "awk {'print $1'} " + mmpath + "foundapi.log | sort | uniq | sort -n  > " + mmpath + "ipsapi.log"
        os.system(getips)

        # Loop through found attacker IPs
        with open(mmpath + "ipsapi.log") as f:
            contents = f.readlines()
            for line in reversed(contents):
                line = line.replace("\n", "")

                # ban  IP
                print(n + " " + PINK + line + NC + " Logging for 400 paymentAPI return")
                if savecounts(line) == 1:
                    doban(line,nginxfile)

                # Get cart mask id & ban it too!
                cartid = os.popen("grep " + line + " " + mmpath + "foundapi.log | grep -o -P '(?<=guest-carts/).*(?=/payment-information)' | uniq").read().replace("\n", "")
                print(n + " Logging cart " + PURPLE + cartid + NC)
                if len(str(cartid)) == 32:
                    if savecounts(cartid) == 1:
                        dobancart(cartid)
                else:
                    #print(len(cartid))
                    #errorcheck = "cp /srv/mmautoban/foundapi.log /srv/mmautoban/foundapi.error"
                    #os.system(errorcheck)
                    print(n + RED + " Can't get cart from string. It is an unexpected result: " + PURPLE + str(cartid) + NC)


    ################# CA GET STATS ###################

    # Attacks today
    #attackssofar = os.popen("grep payment-information " + logfile + " | grep -e ' 403 ' -e ' 400 ' | grep POST | wc -l").read().replace("\n", "")
    #blocksuccess = os.popen("grep payment-information " + logfile + " | grep ' 403 ' | grep POST | wc -l").read().replace("\n", "")
    #if int(attackssofar) > 0:
    #    ratiotoday = round(float(int(blocksuccess))/float(int(attackssofar)) * 100,2)
    #else:
    #    ratiotoday = 0

    # Attacks yesterday
    #attacksyester = os.popen("grep payment-information " + logfile2 + " | grep -e ' 403 ' -e ' 400 ' | grep POST | wc -l").read().replace("\n", "")
    #blocksuccess2 = os.popen("grep payment-information " + logfile2 + " | grep ' 403 ' | grep POST | wc -l").read().replace("\n", "")
    #if int(attacksyester) > 0:
    #    ratioyester = round(float(int(blocksuccess2))/float(int(attacksyester)) * 100,2)
    #else:
    #    ratioyester = 0

    # Total lifetime blocked IPs
    if str(path.exists(mmpath + "totalbanned.log")) == "False":
        touchit = "touch " + mmpath + "totalbanned.log"
        os.system(touchit)
    blockedpast = os.popen("cat " + mmpath + "totalbanned.log | grep -v Cleared | wc -l").read().replace("\n", "")
    blockednow = os.popen("cat " + nginxfile + " | grep -v Cleared | wc -l").read().replace("\n", "")
    blockedips = int(blockedpast) + int(blockednow)
    print(n + YELLOW + " IPs blocked lifetime: " + RED + str(blockedips) + NC)

    #Number of carts currently blocked
    #blockedcarts = os.popen("cat " + nginxfilecarts + " | wc -l").read().replace("\n", "")

    #Percentage stats
    #print(n + " Successfully blocked! TODAY: " + YELLOW + str(blocksuccess) + " requests / " + str(attackssofar) + " attacks = " + RED + str(ratiotoday) + "%" + NC)
    #print(n + " Successfully blocked! YESTERDAY: " + YELLOW + str(blocksuccess2) + " requests / " + str(attacksyester) + " attacks = " + RED + str(ratioyester) + "%" + NC)
    print(BLUE + "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++" + NC)


########## BLOCK TOR EXIT NODES -t --torexits ############

# TOR GET IP list from source URL
if args.torexits:
    getlist = "cd " + mmpath + " && curl -O " + torurl
    os.system(getlist)

    #  TOR Loop through IPs in the list
    filesize = os.path.getsize(mmpath + torfile)
    if filesize == 0:
        print(n + RED + " Something is wrong. TOR source list not found or empty" + NC)
    else:
        with open(mmpath + torfile) as f:
            contents = f.readlines()
            for line in reversed(contents):
                line = line.replace("\n", "")
                if savecounts(line) == 1:
                    doban(line,nginxtor)


######### --unban -u UNBANS IPs & Carts previosuly banned unless attack is underway now ###########
if args.unban:
    # Check if attack is active
    checkattacks1 = "sed -rne '/" + u + "/,/" + n + "/ p' " + logfile + " | grep V1/guest-carts | grep payment-information | grep POST | grep ' 400 ' > " + mmpath + "unbancheck.log"
    checkattacks2 = "sed -rne '/" + u + "/,/" + n + "/ p' " + logfile + " | grep V1/guest-carts | grep payment-information | grep POST | grep ' 403 '>> " + mmpath + "unbancheck.log"
    os.system(checkattacks1)
    os.system(checkattacks2)
    count = os.popen("cat " + mmpath + "unbancheck.log | wc -l").read().replace("\n", "")
    if int(count) > activelimit:
        print(n + " " + RED + str(count) + " attacks logged in past " + str(abs(utime)) + " minutes. Skipping unbans." + NC)
    else:
        print(n + " " + GREEN + "Unbanning IPs & carts since only " + str(count) + " attacks logged in past " + str(abs(utime)) + " minutes." + NC)
        if str(path.exists(mmpath + "totalbanned.log")) == "False":
            touchit = "touch " + mmpath + "totalbanned.log"
            os.system(touchit)
        unbanips = "cat " + nginxfile + " >> " + mmpath + "totalbanned.log;echo '# Cleared at " + n + "' > " + nginxfile
        unbancarts = "echo '# Cleared at " + n + "' > " + nginxfilecarts
        emptytally = "echo '1.1.1.1,1' > " + mmpath + "savecounts.tally"
        os.system(unbanips)
        os.system(unbancarts)
        os.system(emptytally)
        reload =1

######### GLOBAL RELOAD NGINX NICELY IF WE ADDED BLOCKS ##########
if reload == 1:
    doreload = "/usr/share/stratus/cli nginx.update"
    os.system(doreload)
    print(n + GREEN + " Reloaded nginx config: /usr/share/stratus/cli nginx.update" + NC)