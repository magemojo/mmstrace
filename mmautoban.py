#!/usr/bin/env python
# MageMojo AutoBan
# Auto-add IPs related to carding attacks
# Cron should be set every 5 minutes

#variables
nginxfile = "/srv/.nginx/server_level/mmautoban.conf"

# Needed things
import datetime
import os
import subprocess

# Get Current Date/Time
getnow = datetime.datetime.now()
now = getnow.strftime("%d/%b/%Y:%H:%M")
now = datetime.datetime.strptime(now, '%d/%b/%Y:%H:%M')
#print(now)

# get time 5 minutes ago
fiveago = now + datetime.timedelta(minutes = -5)
#print(fiveago)

#convert to right format
n = now.strftime("%d\/%b\/%Y:%H:%M:59")
f = fiveago.strftime("%d\/%b\/%Y:%H:%M:00")
#print(n)
#print(f)

# check log for past 5min
sed = "sed -rne '/" + f + "/,/" + n + "/ p' /log/access.log | grep rest/default/V1/guest-carts | grep payment-information
#print(sed)
os.system(sed)

# check if no attackers found otherwise get IPs
filesize = os.path.getsize("/srv/mmautoban/found.log")
if filesize == 0:
    print(n + " No carding attacks found")
else:
    # GET IPs
    getips = "awk {'print $1'} /srv/mmautoban/found.log | sort | uniq | sort -n  > /srv/mmautoban/ips.log"
    #print(getips)
    os.system(getips)

    # Loop through found attacker IPs
    with open("/srv/mmautoban/ips.log") as f:
        contents = f.readlines()
        for line in reversed(contents):
            line = line.replace("\n", "")
            #print(line)

            # deny in nginx if not already there
            with open(nginxfile) as nfile:
                linetest = line + ";"
                if linetest in nfile.read():
                    print(n + " " + line + " already added to blocks")
                else:
                    ban = "echo 'deny " + line + ";' >> " + nginxfile
                    print(n + " " + line + " blocked")
                    os.system(ban)

    # Reload nginx nicely
    reload = "/usr/share/stratus/cli nginx.update"
    os.system(reload)
