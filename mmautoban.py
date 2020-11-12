#!/usr/bin/env python
# MageMojo AutoBan
# v1.3
# Auto-add IPs related to carding attacks
# Cron should be set to (time-1)


########## NEEDED THINGS ##########
import datetime
import os
import subprocess

########## FUNCTIONS ##########
def doban(line):
    # deny IP in nginx if not already there
    with open(nginxfile) as nfile:
        linetest = line + ";"
        if linetest in nfile.read():
            print(n + " " + line + " already added to blocks")
        else:
            ban = "echo 'deny " + line + ";' >> " + nginxfile
            os.system(ban)
            print(n + PINK + " " + line + RED + " BLOCKED" + NC)

def dobancart(cartid):
    #deny CART in nginx if not already there
    with open(nginxfilecarts) as nfile:
        if cartid in nfile.read():
            print(n + " " + cartid + " already added to blocks")
        else:
            bancart = "echo 'if ($request_uri ~ " + cartid + ") { return 403; }' >> " + nginxfilecarts
            os.system(bancart)
            print(n + " " + PURPLE + cartid + RED + " BLOCKED" + NC)


########## VARIABLES ##########

# This is the path to the nginx log files
logfile = "/log/access.log"
logfile2 = "/log/access.log.1"

# This is the path to the nginx conf files
nginxfile = "/srv/.nginx/server_level/mmautoban.conf"
nginxfilecarts = "/srv/.nginx/server_level/mmautobancarts.conf"

# MageMojo Autoban absolute path MUST BE A TRAILING /
mmpath = "/srv/mmautoban/"

# How many minutes ago of logfile should we check
time = -2

# Some Pretty Colors for logs
NC='\033[0m' # No Color
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[0;33m'
PINK='\033[0;35m'
PURPLE='\033[0;95m'
GREEN='\033[0;32m'


########## GET TIME VARS ##########

# Get Current Date/Time
getnow = datetime.datetime.now()
now = getnow.strftime("%d/%b/%Y:%H:%M")
now = datetime.datetime.strptime(now, '%d/%b/%Y:%H:%M')

# get exact time for "var time set" and "var timestatic set" minutes ago
ago = now + datetime.timedelta(minutes = time)

#convert to right format to use as string for search
n = now.strftime("%d\/%b\/%Y:%H:%M")
f = ago.strftime("%d\/%b\/%Y:%H:%M")


########## CHECK LOGS FOR ATTACKERS ##########

# Check logs for IPs with cart adds
checkcart = "sed -rne '/" + f + "/,/" + n + "/ p' " + logfile + " | grep /checkout/cart/add/uenc/ | grep product | grep POST > " + mmpath + "foundcart.log"
#checkcart = "cat " + logfile + " | grep /checkout/cart/add/uenc/ | grep product | grep POST > " + mmpath + "foundcart.log"
os.system(checkcart)
#print(checkcart)

# Check logs for payment API with 400 response
checkapi = "sed -rne '/" + f + "/,/" + n + "/ p' " + logfile + " | grep rest/default/V1/guest-carts | grep payment-information | grep POST | grep ' 400 ' > " + mmpath + "foundapi.log"
#checkapi = "cat " + logfile + " | grep rest/default/V1/guest-carts | grep payment-information | grep POST | grep ' 400 ' > " + mmpath + "foundapi.log"
os.system(checkapi)
#print(checkapi)


########## PROCESS FINDINGS AND BLOCK IF DETERMINED FAKE ##########

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
                print(n + " " + PINK + line + NC + " Blocking for no static or reload")
                doban(line)
                reload = 1
            else:
                # Check excessive hits to addcart URL in general /checkout/cart/add/uenc/
                hits = os.popen("grep " + line + " " + logfile + " | grep 'POST /checkout/cart/add/uenc/' | wc -l").read().replace("\n", "")
                hits = int(hits)
                if hits > 100:
                    #ban it
                    print(n + " " + PINK + line + NC + " Blocking for addcart count " + str(hits))
                    doban(line)
                    reload = 1
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
            print(n + " " + PINK + line + NC + " Blocking for 400 paymentAPI return")
            doban(line)
            reload = 1

            # Get cart mask id & ban it too!
            cartid = os.popen("grep " + line + " " + mmpath + "foundapi.log | grep -o -P '(?<=guest-carts/).*(?=/payment-information)' | uniq").read().replace("\n", "")
            print(n + " blocking cart " + PURPLE + cartid + NC)
            if len(str(cartid)) == 32:
                dobancart(cartid)
                reload = 1
            else:
                #print(len(cartid))
                #errorcheck = "cp /srv/mmautoban/foundapi.log /srv/mmautoban/foundapi.error"
                #os.system(errorcheck)
                print(n + RED + " Can't get cart from string. It is an unexpected result: " + PURPLE + str(cartid) + NC)

# Reload nginx nicely if we added blocks
if reload == 1:
    doreload = "/usr/share/stratus/cli nginx.update"
    os.system(doreload)
    print(n + GREEN + " Reloaded nginx config: /usr/share/stratus/cli nginx.update" + NC)


################# GET STATS ###################

# Attacks today
attackssofar = os.popen("grep payment-information " + logfile + " | grep -e ' 403 ' -e ' 400 ' | grep POST | wc -l").read().replace("\n", "")
blocksuccess = os.popen("grep payment-information " + logfile + " | grep ' 403 ' | grep POST | wc -l").read().replace("\n", "")
ratiotoday = round(float(int(blocksuccess))/float(int(attackssofar)) * 100,2)

# Attacks yesterday
attacksyester = os.popen("grep payment-information " + logfile2 + " | grep -e ' 403 ' -e ' 400 ' | grep POST | wc -l").read().replace("\n", "")
blocksuccess2 = os.popen("grep payment-information " + logfile2 + " | grep ' 403 ' | grep POST | wc -l").read().replace("\n", "")
ratioyester = round(float(int(blocksuccess2))/float(int(attacksyester)) * 100,2)

# Total lifetime blocked IPs and carts
blockedips = os.popen("cat " + nginxfile + " | wc -l").read().replace("\n", "")
blockedcarts = os.popen("cat " + nginxfilecarts + " | wc -l").read().replace("\n", "")

print(n + " Successfully blocked! TODAY: " + YELLOW + str(blocksuccess) + " requests / " + str(attackssofar) + " attacks = " + RED + str(ratiotoday) + "%" + NC)
print(n + " Successfully blocked! YESTERDAY: " + YELLOW + str(blocksuccess2) + " requests / " + str(attacksyester) + " attacks = " + RED + str(ratioyester) + "%" + NC)
print(n + YELLOW + " IPs blocked lifetime: " + RED + str(blockedips) + NC)
print(n + YELLOW + " Carts blocked lifetime: " + RED + str(blockedcarts) + NC)
print(BLUE + "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++" + NC)
