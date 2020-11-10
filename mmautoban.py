#!/usr/bin/env python
# MageMojo AutoBan
# Auto-add IPs related to carding attacks
# Cron should be set to every 1min


########## NEEDED THINGS ##########
import datetime
import os
import subprocess


########## FUNCTIONS ##########
def doban(line):
    # deny in nginx if not already there
    with open(nginxfile) as nfile:
        linetest = line + ";"
        if linetest in nfile.read():
            print(n + " " + line + " already added to blocks")
        else:
            ban = "echo 'deny " + line + ";' >> " + nginxfile
            os.system(ban)
            global reload
            reload = 1

            
########## VARIABLES ##########

# This is the path to the nginx log file
logfile = "/log/access.log"

# This is the path to the nginx conf file
#nginxfile = "/srv/.nginx/server_level/mmautoban.conf"
nginxfile = "/srv/.nginx/server_level/mmautoban.conf"

# MageMojo Autoban absolute path MUST BE A TRAILING /
mmpath = "/srv/mmautoban/"

# How many minutes ago of logfile should we check
time = -2


########## GET TIME VARS ##########

# Get Current Date/Time
getnow = datetime.datetime.now()
now = getnow.strftime("%d/%b/%Y:%H:%M")
now = datetime.datetime.strptime(now, '%d/%b/%Y:%H:%M')

# get exact time for "var time set" and "var timestatic set" minutes ago
ago = now + datetime.timedelta(minutes = time)
agostatic = now + datetime.timedelta(minutes = timestatic)

#convert to right format to use as string for search
n = now.strftime("%d\/%b\/%Y:%H:%M")
f = ago.strftime("%d\/%b\/%Y:%H:%M")
s = agostatic.strftime("%d\/%b\/%Y:%H:%M")


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
    print(n + " No cart adds found")
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
            #print(checkstatic)
            sfilesize = os.path.getsize(mmpath + "static.log")

            # If there has been no access to static files then block IP, otherwise do nothing
            if sfilesize == 0:
                # ban it
                doban(line)
                print(n + " " + line + " blocked for no static or reload")
            else:
                # Check hits to this URL /checkout/cart/add/uenc/aHR0cHM6Ly93d3cub3Jlby5jb20vb3Jlby1jb29raWUtZmxhdm9yZWQtbGlwLWJhbG0tc2V0LW9mLTI%2C/product/1335/
                hits = os.popen("grep " + line + " " + logfile + " | grep 'POST /checkout/cart/add/uenc/aHR0cHM6Ly93d3cub3Jlby5jb20vb3Jlby1jb29raWUtZmxhdm9yZWQtbGlwLWJhbG0tc2V0LW9mLTI%2C/product/' | wc -l").read().replace("\n", "")
                hits = int(hits)
                if hits > 20:
                    #ban it
                    doban(line)
                    print(n + " " + line + " blocked for addcart count " + str(hits))
                else:
                    print(n + " " + line + " addcart appears legit")


# Check if anything is found this go for API attacks
filesize = os.path.getsize(mmpath + "foundapi.log")
if filesize == 0:
    print(n + " No carding attacks found")
else:
    # GET IPs
    getips = "awk {'print $1'} " + mmpath + "foundapi.log | sort | uniq | sort -n  > " + mmpath + "/ipsapi.log"
    os.system(getips)

    # Loop through found attacker IPs
    with open(mmpath + "ipsapi.log") as f:
        contents = f.readlines()
        for line in reversed(contents):
            line = line.replace("\n", "")

            # ban it
            doban(line)
            print(n + " " + line + " blocked for 400 paymentAPI return")

# Reload nginx nicely if we added blocks
if reload == 1:
    doreload = "/usr/share/stratus/cli nginx.update"
    os.system(doreload)
