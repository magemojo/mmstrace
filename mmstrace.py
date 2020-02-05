#!/usr/bin/python
#Run this from magento root dir (pub for 2.1 template)
#Problems? Questions? Edits? ask Jackie

import os
import sys
try:
   from urllib.parse import urlparse
except ImportError:
   from urlparse import urlparse

sphp = "/usr/bin/php"
stratus = "1"

#GET URL PARTS
print "\033[1;45m" + str("example url: https://mysite.com/catalog/cats.html") + "\033[1;m"
url = raw_input("url? > ")
parse_object = urlparse(url)
surl = parse_object.netloc
spage = parse_object.path
sscheme = parse_object.scheme
squery =  parse_object.query

if spage == "":
   surl = "/"

if surl == "":
   print "Please enter url correctly"
   sys.exit()

#check scheme
if sscheme == 'http':
   shttp = ""
elif sscheme == 'https':
   shttp = 'HTTPS="on"'
else:
   shttp = ""
   print "Unknown scheme - assuming https"
   print "url is: " + url
   print "You may want to start over"
   shttp = 'HTTPS="on"'

#GET INTERNAL IP commented out. IP command was remvoved from stratus.
#intip = os.popen("ip -f inet addr | grep 'global eth0' | awk '{print $2}' | rev | cut -c4- | rev").read()
#intip = intip.replace("\n", '')
#print intip
intip = '192.168.1.2'

#BUILD STRACE CMD
print ""
if squery == "":
   finalstrace = shttp + " HTTP_HOST=" + surl + " REQUEST_METHOD=GET" + " SERVER_ADDR=" + intip + " REMOTE_ADDR=" + intip + " REQUEST_URI=" + spage + " SERVER_NAME=" + surl + " strace -r -s 1024 -T -e trace=sendto,connect,network,memory,file,open,write php index.php 1>/dev/null 2>mmstrace/strace.out"
else:
   squery = '"' + squery + '"'
   finalstrace = shttp + " HTTP_HOST=" + surl + " REQUEST_METHOD=GET" + " SERVER_ADDR=" + intip + " REMOTE_ADDR=" + intip + " REQUEST_URI=" + spage + " QUERY_STRING=" + squery + " SERVER_NAME=" + surl + " strace -r -s 1024 -T -e trace=sendto,connect,network,memory,file,open,write php index.php 1>/dev/null 2>mmstrace/strace.out"
print finalstrace
print ""

#RUN STRACE FOR STRATUS
print "Running strace...."
os.system(finalstrace)

#SLOW PATHS TOP 10
pathsslow = "grep '/srv/' mmstrace/strace.out | sort -n | tail -10 > mmstrace/strace_paths_slow"
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
queryredis = "grep 'sendto' mmstrace/strace.out | grep -E 'HMSET|HGET|HSET|HMGET|EXPIRE|redis' > mmstrace/redis.out"
os.system(queryredis)

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
   modcmd = "n98-magerun dev:module:list | grep -v Mage_ >> mmstrace/strace-notable.out"
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
info = "echo 'This section greps for keywords of interest: error, exception, connect, fatal, core_cache, core_session' > mmstrace/strace_errors.out"
errcmd = "grep error mmstrace/strace.out | grep -v libgpg-error.so | grep -v 'read(' >> mmstrace/strace_errors.out"
errcmdb = "grep exception mmstrace/strace.out | grep -v 'read(' >> mmstrace/strace_errors.out"
errcmdc = "grep connect mmstrace/strace.out | grep -v magento-module-connector | grep -v module-resource-connections | grep -v 'read(' >> mmstrace/strace_errors.out"
errcmdf = "grep fatal mmstrace/strace.out | grep -v 'read(' >> mmstrace/strace_errors.out"
errcmdcc = "grep core_cache mmstrace/strace.out | grep -v 'read(' >> mmstrace/strace_errors.out"
errcmdcs = "grep core_session mmstrace/strace.out | grep -v 'read(' >> mmstrace/strace_errors.out"
os.system(info)
os.system(errcmd)
os.system(errcmdb)
os.system(errcmdc)
os.system(errcmdf)
os.system(errcmdcc)
os.system(errcmdcs)
print "\033[1;45m" + str("Results at " + sscheme + "://" + surl + "/mmstrace/") + "\033[1;m"
