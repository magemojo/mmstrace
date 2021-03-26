#!/usr/bin/env python
# MageMojo AutoBan
# v1.8
# Auto-add IPs related to carding attacks / TOR / custom paths
# Cron should be set to same time as <time> variable for carding (default is 1 minute)


########## GLOBAL NEEDED THINGS | DO NOT CHANGE ##########
import datetime
import os
import os.path
from os import path
import argparse
import socket


########## GLOBAL VARIABLES ##########

# This is the path to the nginx log files
logfile = "/log/access.log"
logfile2 = "/log/access.log.1"

# This is the path to the nginx conf files
whitelist = "/srv/mmautoban/white.list"
nginxfile = "/srv/.nginx/server_level/mmautoban.conf"
nginxfilecarts = "/srv/.nginx/server_level/mmautobancarts.conf"
nginxtor = "/srv/.nginx/server_level/mmautobantor.conf"
nginxcustom = "/srv/.nginx/server_level/mmautobancustom.conf"
#nginxfile = "/srv/mmautoban/test/mmautoban.conf" #testingonly
#nginxfilecarts = "/srv/mmautoban/test/mmautobancarts.conf" #testingonly
#nginxtor = "/srv/mmautoban/test/mmautobantor.conf" #testingonly
#nginxcustom = "/srv/mmautoban/test/mmautobancustom.conf" #testingonly

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
if str(path.exists(whitelist)) == "False":
    touchit="touch " + whitelist
    os.system(touchit)
if str(path.exists(nginxcustom)) == "False":
    touchit="touch " + nginxcustom
    os.system(touchit)
if str(path.exists(mmpath + "tmp")) == "False":
    makeit="mkdir " + mmpath + "tmp"
    os.system(makeit)

# How many minutes ago of logfile should we check SET THIS SAME AS CRON
# example for 1 minute  = "time = 1"
# THIS SHOULD NOT BE CHANGED, AUTOBAN IS USELESS IF NOT CHECKING AS FREQUENTLY AS POSSIBLE
time = 1

# How many minutes ago should we check for attacks before unbanning? (for carding option ONLY)
utime = 15

# How many attacks should be considered "an active attack" in utime above (for carding option ONLY)
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

# get exact time for "var time set" in case it has been changed
time = time * -1
ago = now + datetime.timedelta(minutes = time)

#convert to right format to use as string for search
n = now.strftime("%d\/%b\/%Y:%H:%M")
f = ago.strftime("%d\/%b\/%Y:%H:%M")


######### GLOBAL ARGUMENT MAGIC AKA WHAT ARE WE DOING? ##########
parser = argparse.ArgumentParser()
parser.add_argument('-c','--carding', action='store', dest='carding', type=int,
    help="blocks carding attacks at <num> bad attempts per IP or cart. 1=AGGRESSIVE & is meant for active attacks.")
parser.add_argument('-u', '--unban', action='store_true',
    help="unbans IPs & carts (from carding attacks) unless attack is active")
parser.add_argument('-t', '--torexits', action='store_true',
    help="blocks TOR exit nodes")
parser.add_argument('-p', '--custompath', action='store', dest='custompath', type=str,
    help="Auto blocks a custom path <path> at <limit> per <minutes>")
parser.add_argument('-m', action='store', dest='minutes', type=int,
    help="<minutes> subvar for --custompath")
parser.add_argument('-l', action='store', dest='limit', type=int,
    help="<limit> subvar for --custompath")
parser.add_argument('-r', action='store', dest='refresh', type=int,
    help="<refresh> subvar for --custompath")
args = parser.parse_args()


######### GLOBAL FUNCTION ###########

# Adds whitelisted IPs to conf during unban
def wlist(whitelist,nginxfile):
    with open(whitelist) as wfile:
        #check whitelist and add IPs to conf as allowed
        contents = wfile.readlines()
        for line in reversed(contents):
            line = line.replace("\n", "")
            try:
                socket.inet_aton(line)
                wl = "echo 'allow " + line + ";' >> " + nginxfile
                os.system(wl)
                print(n + PINK + " " + line + GREEN + " WHITE-LISTED" + NC)
            except socket.error:
                print(RED + line + " is not a valid IP in white.list" + NC) # Not legal

# Bans an IP
def doban(line,file):
    whitelist = "/srv/mmautoban/white.list"
    global reload
    with open(file) as nfile:

        # Check IP is legit (in case file format has changed in source)
        # Then block if not already blocked
        try:
            socket.inet_aton(line)
            linetest = line + ";"

            if linetest in nfile.read():
                print(n + " " + line + " already added to blocks or in white.list")
            else:
                with open(whitelist) as wfile:
                    if line in wfile.read():
                        print(n + PINK + " " + line + NC + " not blocked cause in white.list" + NC)
                    else:
                        #print(whitelist)  #DEBUG
                        #print(line)  #DEBUG
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
        # tally file exists
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
                # tally file exists but thing is not in it
                else:
                    save = "echo '" + str(thing) + ",1 ' >> " + mmpath + "savecounts.tally"
                    os.system(save)
                    if maxcount==1:
                        maxreached=1
                        return maxreached
                    else:
                        maxreached=0
                        return maxreached
        # tallyfile doesnt exist yet
        else:
           save = "echo '" + str(thing) + ",1 ' > " + mmpath + "savecounts.tally"
           os.system(save)
           if maxcount==1:
               maxreached=1
               return maxreached
           else:
               maxreached=0
               return maxreached

def getminsago(now,mins):
    # get exact time for <minutes> ago variable for pulling from log
    minsneg = mins * -1
    minsago = now + datetime.timedelta(minutes = minsneg)
    # convert to right format to use as string for search
    m = minsago.strftime("%d\/%b\/%Y:%H:%M")
    return m

def checktimestamp(now,mins,file,m,max):
    # check if timestamp exists in logfile
    checkthis = os.popen("grep -m1 '" + m + "' " + file + " | wc -l").read().replace("\n", "")
    #print("grep -m1 '" + m + "' " + file + " | wc -l")  #DEBUG
    if int(checkthis) >= 1:
        #print("In log file? checkthis = " + str(checkthis))  #DEBUG
        return m
    else:
        if max >= 1:
            #print("max reached? max = " + str(max))  #DEBUG
            if mins >= 2:
                minstry = mins-1
                max = max - 1
                #print("timestamp not found, checking with " + str(now) + ", " + str(minstry) + ", " + str(file) + ", " + str(m) + ", " + str(max))  #DEBUG
                checktimestamp(now,minstry,file,getminsago(now,minstry),max)
            else:
                return m
        else:
            return m

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
    checkcart = "sed -rne '/" + f + "/,/" + n + "/ p' " + logfile + " | grep /checkout/cart/add/uenc/ | grep product | grep POST > " + mmpath + "tmp/cart.found.tmp"
    #checkcart = "cat " + logfile + " | grep /checkout/cart/add/uenc/ | grep product | grep POST > " + mmpath + "tmp/cart.found.tmp"
    os.system(checkcart)

    # Check logs for payment API with 400 response
    checkapi = "sed -rne '/" + f + "/,/" + n + "/ p' " + logfile + " | grep V1/guest-carts | grep payment-information | grep POST | grep ' 400 ' > " + mmpath + "tmp/api.found.tmp"
    #checkapi = "cat " + logfile + " | grep rest/default/V1/guest-carts | grep payment-information | grep POST | grep ' 400 ' > " + mmpath + "tmp/api.found.tmp"
    os.system(checkapi)


    ########## CA PROCESS FINDINGS AND BLOCK IF DETERMINED FAKE ##########

    # Check if anything is found this go for cart adds
    filesize = os.path.getsize(mmpath + "tmp/cart.found.tmp")
    if filesize == 0:
        print(n + GREEN + " No cart adds found" + NC)
    else:
        # GET IPs
        getips = "awk {'print $1'} " + mmpath + "tmp/cart.found.tmp | sort | uniq | sort -n  > " + mmpath + "tmp/cart.ips.tmp"
        os.system(getips)

        # Loop through found IPs that added to cart
        with open(mmpath + "tmp/cart.ips.tmp") as f:
            contents = f.readlines()
            for line in reversed(contents):
                line = line.replace("\n", "")

                # Check logs for previous static file access or customer load section
                checkstatic = "grep " + line + " " + logfile + " | grep static > " + mmpath + "tmp/static.found.tmp"
                checkload = "grep " + line + " " + logfile + " | grep customer/section/load >> " + mmpath + "tmp/static.found.tmp"
                os.system(checkstatic)
                os.system(checkload)
                sfilesize = os.path.getsize(mmpath + "tmp/static.found.tmp")

                # If there has been no access to static files then block IP, otherwise check for excessive hits to cart
                if sfilesize == 0:
                    # ban it
                    print(n + " " + PINK + line + NC + " Logging for no static or reload")
                    if savecounts(line) == 1:
                        doban(line,nginxfile)
                else:
                    # Check excessive hits to addcart URL in general /checkout/cart/add/uenc/
                    hits = os.popen("grep " + line + " " + logfile + " | grep 'POST /checkout/cart/add/uenc/' | wc -l").read().replace("\n", "")
                    hits = int(hits)
                    if hits > 1000:
                        #ban it
                        if str(66.249) in line:
                            print(n + RED + " Can't block for cartadd " + PINK + LINE + RED + ". Google Bot." + NC)
                        else:
                            print(n + " " + PINK + line + NC + " Logging for addcart count " + str(hits))
                            if savecounts(line) == 1:
                                doban(line,nginxfile)
                    else:
                        print(n + " " + PINK + line + GREEN + " Addcart appears legit" + NC)


    # Check if anything is found this go for API attacks
    filesize = os.path.getsize(mmpath + "tmp/api.found.tmp")
    if filesize == 0:
        print(n + GREEN + " No carding attacks found" + NC)
    else:
        # GET IPs
        getips = "awk {'print $1'} " + mmpath + "tmp/api.found.tmp | sort | uniq | sort -n  > " + mmpath + "tmp/api.ips.tmp"
        os.system(getips)

        # Loop through found attacker IPs
        with open(mmpath + "tmp/api.ips.tmp") as f:
            contents = f.readlines()
            for line in reversed(contents):
                line = line.replace("\n", "")

                # ban  IP
                print(n + " " + PINK + line + NC + " Logging for 400 paymentAPI return")
                if savecounts(line) == 1:
                    doban(line,nginxfile)

                # Get cart mask id & ban it too!
                cartid = os.popen("grep -m1 " + line + " " + mmpath + "tmp/api.found.tmp | grep -o -P '(?<=guest-carts/).*(?=/payment-information)' | uniq").read().replace("\n", "")
                print(n + " Logging cart " + PURPLE + cartid + NC)
                if len(str(cartid)) == 32:
                    if savecounts(cartid) == 1:
                        dobancart(cartid)
                else:
                    #print(len(cartid))
                    #errorcheck = "cp /srv/mmautoban/tmp/api.found.tmp /srv/mmautoban/tmp/foundapi.error"
                    #os.system(errorcheck)
                    #print("grep " + line + " " + mmpath + "tmp/api.found.tmp | grep -o -P '(?<=guest-carts/).*(?=/payment-information)' | uniq")
                    print(n + RED + " Can't get cart from string. It is an unexpected result: " + PURPLE + str(cartid) + NC)

    ################# CA GET STATS ###################

    # Total lifetime blocked IPs
    if str(path.exists(mmpath + "totalbanned.log")) == "False":
        touchit = "touch " + mmpath + "totalbanned.log"
        os.system(touchit)
    blockedpast = os.popen("cat " + mmpath + "totalbanned.log | grep -v Cleared | grep -v allow | wc -l").read().replace("\n", "")
    blockednow = os.popen("cat " + nginxfile + " | grep -v Cleared | grep -v allow | wc -l").read().replace("\n", "")
    if blockedpast == "":
        blockedpast = 0
    if blockednow == "":
        blockednow = 0
    blockedips = int(blockedpast) + int(blockednow)
    print(n + YELLOW + " IPs blocked lifetime: " + RED + str(blockedips) + NC)

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
                doban(line,nginxtor)


######### --unban -u UNBANS IPs & Carts previosuly banned unless attack is underway now ###########
if args.unban:
    # Get timestamp, then check if it exists in log & adjust if not
    u = getminsago(now,utime)
    u = checktimestamp(now,utime,logfile,u,10)

    # Check if attack is active
    checkattacks1 = "sed -rne '/" + str(u) + "/,/" + n + "/ p' " + logfile + " | grep V1/guest-carts | grep payment-information | grep POST | grep ' 400 ' > " + mmpath + "tmp/unban.check.tmp"
    checkattacks2 = "sed -rne '/" + str(u) + "/,/" + n + "/ p' " + logfile + " | grep V1/guest-carts | grep payment-information | grep POST | grep ' 403 '>> " + mmpath + "tmp/unban.check.tmp"
    os.system(checkattacks1)
    os.system(checkattacks2)
    count = os.popen("cat " + mmpath + "tmp/unban.check.tmp | wc -l").read().replace("\n", "")
    if int(count) > activelimit:
        print(n + " " + RED + str(count) + " attacks logged in past " + str(utime) + " minutes. Skipping unbans." + NC)
    else:
        print(n + " " + GREEN + "Unbanning IPs & carts since only " + str(count) + " attacks logged in past " + str(utime) + " minutes." + NC)
        if str(path.exists(mmpath + "totalbanned.log")) == "False":
            touchit = "touch " + mmpath + "totalbanned.log"
            os.system(touchit)
        unbanips = "cat " + nginxfile + " >> " + mmpath + "totalbanned.log;echo '# Cleared at " + n + "' > " + nginxfile
        unbancarts = "echo '# Cleared at " + n + "' > " + nginxfilecarts
        emptytally = "echo '1.1.1.1,1' > " + mmpath + "savecounts.tally"
        os.system(unbanips)
        wlist(whitelist,nginxfile)
        os.system(unbancarts)
        os.system(emptytally)
        reload =1

########## --custompath -p Auto blocks a custom path <path> at <maxcount> per <minutes>
if args.custompath >= 1:
    cpath = str(args.custompath)
    mins = int(args.minutes)
    limit = int(args.limit)
    refresh = int(args.refresh)
    #limitreached = 0  #define

    # check if refresh tally exists and log this run
    if str(path.exists(mmpath + "refresh.tally")) == "False":
        rdo = "echo 1 > " + mmpath + "refresh.tally"
        os.system(rdo)
        newtally = 1
    else:
        rtally = os.popen("awk {'print $1'} " + mmpath + "refresh.tally").read().replace("\n", "")
        newtally = int(rtally) + 1
        rdo = "echo " + str(newtally) + " > " + mmpath + "refresh.tally"
        os.system(rdo)
    #print("refresh-check = " + str(newtally) + " - " + str(refresh)) #DEBUG
    #time to refresh / unban?
    if int(newtally) >= refresh:
        # Get timestamp, then check if it exists in log & adjust if not
        u = getminsago(now,utime)
        u = checktimestamp(now,utime,logfile,u,10)

        # Check if attack is active
        check = os.popen("sed -rne '/" + str(u) + "/,/" + n + "/ p' " + logfile + " | grep '" + cpath + "' | grep POST | wc -l").read().replace("\n", "")
        #print("sed -rne '/" + str(u) + "/,/" + n + "/ p' " + logfile + " | grep '" + cpath + "' | grep POST | wc -l")   #DEBUG
        if int(check) >= activelimit:
            print(n + " " + RED + str(check) + " POSTS logged in past " + str(utime) + " minutes. Skipping refresh & unbans." + NC)
        else:
            print(PURPLE + "NOTE: This cron autobans IPS posting to the path " +  cpath + " more than " + str(limit) + " times in " + str(mins) + " minutes" + NC)
            print(PURPLE + "It ubans every " + str(refresh) + " minutes" + NC)
            print("These options are set in the cron command")
            #print("/usr/bin/python /srv/mmautoban/mmautoban.py --custompath " + cpath + " -l " + str(limit) + " -m " + str(mins) + " -r " + str(refresh) + " >> /srv/mmautoban/mmautoban.log")
            print(n + " " + GREEN + "Unbanning IPs & refreshing logs since only " + str(check) + " attacks logged in past " + str(utime) + " minutes." + NC)
            if str(path.exists(mmpath + "custom.totalbanned.log")) == "False":
                touchit = "touch " + mmpath + "custom.totalbanned.log"
                os.system(touchit)
            unbanips = "cat " + nginxcustom + " >> " + mmpath + "custom.totalbanned.log;echo '# Cleared at " + n + "' > " + nginxcustom
            emptytally = "echo '0' > " + mmpath + "refresh.tally"
            os.system(unbanips)
            wlist(whitelist,nginxcustom)
            os.system(emptytally)
            reload =1

    # Get the timestamp for var <minutes> ago
    m = getminsago(now,mins)
    # Check the timestamp exists in log, if not check 1 minute after (but lets not loop forever, max 10 checks in case log has rotated or site was offline)
    m = checktimestamp(now,mins,logfile,m,10)

    # Check logs for IPs hitting the custom path in the past run (default=1min check <time> var)
    checkpathc = "sed -rne '/" + f + "/,/" + n + "/ p' " + logfile + " | grep '" + cpath + "' | grep POST > " + mmpath + "tmp/custom.path.tmp"
    #print("sed -rne '/" + f + "/,/" + n + "/ p' " + logfile + " | grep '" + cpath + "' | grep POST > " + mmpath + "tmp/custom.path.tmp") #FOR DEBUG
    os.system(checkpathc)

    # Check if anything is found this go for custom path posts
    filesize = os.path.getsize(mmpath + "tmp/custom.path.tmp")
    if filesize == 0:
        print(n + GREEN + " No POSTS to path found " + NC)
    else:
        # get ips
        getipsc = "awk {'print $1'} " + mmpath + "tmp/custom.path.tmp | sort | uniq | sort -n  > " + mmpath + "tmp/custom.ips.tmp"
        os.system(getipsc)

        # loop through results
        with open(mmpath + "tmp/custom.ips.tmp") as f:
            contents = f.readlines()
            for line in reversed(contents):
                line = line.replace("\n", "")
                # count number of times IP has hit the path in past <m> minutes
                hits = os.popen("sed -rne '/" + m + "/,/" + n + "/ p' " + logfile + " | grep " + line + " | grep '" + cpath + "' | grep POST | wc -l").read().replace("\n", "")
                #print("sed -rne '/" + m + "/,/" + n + "/ p' " + logfile + " | grep " + line + " | grep '" + cpath + "' | grep POST | wc -l") #FOR DEBUG
                hits = int(hits)

                if hits >= limit:
                    print(n + " " + PURPLE + " Ban Check:" + str(line) + " for " + str(hits) + " hit(s)" + NC)
                    doban(line,nginxcustom)
                else:
                    print(n + " " + GREEN + " Logging " + str(line) + " for " + str(hits) + " hit(s)" + NC)


######### GLOBAL RELOAD NGINX NICELY IF WE ADDED BLOCKS ##########
if reload == 1:
    doreload = "/usr/share/stratus/cli nginx.update"
    os.system(doreload)
    print(n + GREEN + " Reloaded nginx config: /usr/share/stratus/cli nginx.update" + NC)