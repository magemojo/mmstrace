#!/usr/bin/python
#Run this from magento root dir (pub for 2.1 template)
#Problems? Questions? Edits? ask Jackie

import os
import sys
try:
   from urllib.parse import urlparse
except ImportError:
   from urlparse import urlparse

#CHECK IF STRATUS OR MHM
print "\033[1;45m" + str("1. STRATUS") + "\033[1;m"
print "\033[1;45m" + str("2. MHM") + "\033[1;m"
wtype = raw_input("1 or 2? > ")
if wtype == '1':
   sphp = "/usr/bin/php"
   stratus = "1"
elif wtype == '2':
   stratus = "0"
else:
   print "Unknown Option Selected!"
   sys.exit()

#GET URL PARTS
print " "
print "\033[1;45m" + str("example url: https://mysite.com/catalog/cats.html") + "\033[1;m"
#print "example url: https://mysite.com/catalog/cats.html"
url = raw_input("url? > ")
parse_object = urlparse(url)
surl = parse_object.netloc
spage = parse_object.path
sscheme = parse_object.scheme

if spage == "":
   surl = "/"
   
if surl == "":
   print "Please enter url correctly"
   sys.exit() 

#FOR TESTING   
#print url
#print surl
#print spage
#print sscheme

if sscheme == 'http':
   shttp = ""
elif sscheme == 'https':
   shttp = 'HTTPS="on"'
else:
   shttp = ""
   print "Unknown scheme - assuming http"
   print "url is: " + url
   print "You may want to start over"

#GET INTERNAL IP commented out. IP command was remvoved from stratus.
#intip = os.popen("ip -f inet addr | grep 'global eth0' | awk '{print $2}' | rev | cut -c4- | rev").read()
#intip = intip.replace("\n", '')
#print intip
intip = '192.168.1.2'
  
if stratus == '1':

   #BUILD STRACE CMD
   print ""
   finalstrace = shttp + " HTTP_HOST=" + surl + " REQUEST_METHOD=GET" + " SERVER_ADDR=" + intip + " REMOTE_ADDR=" + intip + " REQUEST_URI=" + spage + " SERVER_NAME=" + surl + " strace -r -s 1024 -T -e trace=sendto,connect,network,memory,file,open,write php index.php 1>/dev/null 2>mmstrace/strace.out"
   print finalstrace
   print ""

   #RUN STRACE FOR STRATUS
   print "Running strace...."
   os.system(finalstrace)

   #SLOW PATHS TOP 10
   pathsslow = "grep '/srv/' mmstrace/strace.out | sort -n | tail -10 > mmstrace/strace_paths_slow"
   os.system(pathsslow)

elif stratus == '0':

   #GET PHP VERSION
   print " "
   print "\033[1;45m" + str("1. PHP 5.4") + "\033[1;m"
   print "\033[1;45m" + str("2. PHP 5.5") + "\033[1;m"
   print "\033[1;45m" + str("3. PHP 5.6") + "\033[1;m"
   print "\033[1;45m" + str("4. PHP 7.0") + "\033[1;m"
   getphp = raw_input("Choose #1-4  > ")
   
   #detecting php version via mmcli not working well in some cases. Commented this out & asking for it instead.
   #getphp = os.popen("mmcli vhost:list | grep -B40 " + surl + " | grep -A 5 phpfpm | grep -A1 version").read()
   #getphp = getphp.replace("version:", '').replace("\n", '').replace(" ", '')
   #print getphp

   if getphp == '1':
      sphp = "php"
   elif getphp == '2':
      sphp = "php55"
   elif getphp == '3':
      sphp = "php56"
   elif getphp == '4':
      sphp = "php70"
   else:
      print "A number 1-4 was not chosen: exiting..."
      sys.exit()

   #BUILD STRACE CMD
   finalstrace = shttp + " HTTP_HOST=" + surl + " REQUEST_METHOD=GET" + " REQUEST_URI=" + spage + " SERVER_NAME=" + surl + " strace -r -s 1024 -T -e trace=sendto,connect,file,network,memory,open,write " + sphp + " index.php 1>/dev/null 2>mmstrace/strace.out"
   print " "
   print finalstrace

   #RUN STRACE FOR MHM
   print "Running strace...."
   print " "
   os.system(finalstrace)

   #SLOW PATHS TOP 10
   pathsslow = "grep '/home/' mmstrace/strace.out | sort -n | tail -10 > mmstrace/strace_paths_slow"
   os.system(pathsslow)


#SLOW QUERIES / COUNT ALL QUERIES
querycmd = "grep 'sendto' mmstrace/strace.out |grep -E 'SELECT|SHOW|INSERT|UPDATE|SET |store-|mysql' | sort -n | tail -10 > mmstrace/strace_queries"
qtagcount = "echo -n ' queries total = ' >> mmstrace/strace_queries"
querycount = "grep 'sendto' mmstrace/strace.out | grep -E 'SELECT|SHOW|INSERT|UPDATE|SET |store-|mysql' | wc -l >> mmstrace/strace_queries"
queryinfo = "awk '{for(i=1;i<=NF;i++)if($i~/FROM/)print $(i+1)}' mmstrace/strace.out | sort | uniq -c | sort -nr > mmstrace/query_info";
os.system(querycmd)
os.system(qtagcount)
os.system(querycount)
os.system(queryinfo)

#SESSION/REDIS CACHE INFO
#queryredis = "grep 'sendto' mmstrace/strace.out | grep -E 'HMSET|HGET|HSET|HMGET|EXPIRE|redis' > mmstrace/redis.out"
#os.system(queryredis)

#GET OTHER INFO
#CHECK IF M2 or M1 FIRST
if os.path.exists("../bin/magento"):
   checkcmd = "n98-magerun2 sys:info > mmstrace/strace-notable.out"
   modcmd = "n98-magerun2 dev:module:list | grep -v Magento_ >> mmstrace/strace-notable.out"
   cachecmd = "n98-magerun2 cache:list >> mmstrace/strace-notable.out"
elif os.path.exists("bin/magento"):
   checkcmd = "n98-magerun2 sys:info > mmstrace/strace-notable.out"
   modcmd = "n98-magerun2 dev:module:list | grep -v Magento_ >> mmstrace/strace-notable.out"
   cachecmd = "n98-magerun2 cache:list >> mmstrace/strace-notable.out"
else:
   compilecmd = "php -f shell/compiler.php -- state > mmstrace/strace-notable.out"
   checkcmd = "n98-magerun sys:info >> mmstrace/strace-notable.out"
   modcmd = "n98-magerun dev:module:list | grep -v Magento >> mmstrace/strace-notable.out"
   cachecmd = "n98-magerun cache:list >> mmstrace/strace-notable.out"
   os.system(compilecmd)
   
os.system(checkcmd)
os.system(modcmd)
os.system(cachecmd)

#GET TIME
timecmd = "curl -w '@mmstrace/curl-format.txt' -o /dev/null -s '" + url + "' > mmstrace/curl-time.out"
spacecmd = "echo ' ' >> mmstrace/strace-notable.out"
os.system(timecmd)
os.system(spacecmd)


#ANY ERRORS OR INTERESTING THINGS
info = "echo 'This section greps for keywords of interest: error, exception, connect' > mmstrace/strace_errors.out"
errcmd = "grep error mmstrace/strace.out | grep -v libgpg-error.so | grep -v 'read(' >> mmstrace/strace_errors.out"
errcmdb = "grep exception mmstrace/strace.out | grep -v 'read(' >> mmstrace/strace_errors.out"
errcmdc = "grep connect mmstrace/strace.out | grep -v magento-module-connector | grep -v module-resource-connections | grep -v 'read(' >> mmstrace/strace_errors.out"
os.system(info)
os.system(errcmd)
os.system(errcmdb)
os.system(errcmdc)

print "\033[1;45m" + str("Results at " + sscheme + "://" + surl + "/mmstrace/") + "\033[1;m"
#print "Results at " + sscheme + "://" + surl + "/mmstrace/"

