# mmstrace

Jackie Angus : strace script for Magento on stratus

Good for finding the reason for a slow page or non-admin page that is giving an error. Just paste in the url of the page you want to strace. Remove this script once testing is complete.

Must be in Magento root ( pub folder for M2.1 or 2.2 template)

wget https://github.com/magemojo/mmstrace/raw/master/mmstrace.tar.gz;tar -xvzf mmstrace.tar.gz;chmod u+x mmstrace.py;./mmstrace.py

2/5/2020 Removed MHM section. Added query string usage & Redis activity. Added core_session and core_cache usage detection. 
9/29/2019 changed slow query and path list to 10 instead of 5. Added top tables accessed and count.

# backflip.sh

Justin Waggoner

Backflip v4.2 is now available. Backflip is a multi-use backup utility. It automatically extracts Stratus details such as the MySQL username, MySQL password, and MySQL database name for a nice POC-friendly MySQL dump. The script will dump and package everything neatly and report to you the location of the generated backup. All you have to do is press a key, enter a doc root and Backflip will do the rest.

# dns.sh

Steven Jackson

DNS quick-script to show WHOIS info, DNS records, mail records, DKIM, SSL info. 

# mmautoban.py

Jackie Angus

Autoblocks IPs & carts from carding attacks and/or TOR exit nodes as a cron depending on options you choose. Will not work at other hosts. 

Download to /srv/mmautoban/

wget https://github.com/magemojo/mmstrace/raw/master/mmautoban.py

For carding attack blocking: Set cron to run every 1min: /usr/bin/python /srv/mmautoban/mmautoban.py --carding 3 >> /srv/mmautoban/mmautoban.log

To unban IPs & carts, set separate cron to run every 2hrs: /usr/bin/python /srv/mmautoban/mmautoban.py --unban >> /srv/mmautoban/mmautoban.log

For TOR exit node blocking: Set cron to run once a day to check for updates: /usr/bin/python /srv/mmautoban/mmautoban.py --torexits >> /srv/mmautoban/mmautobanTOR.log

Option: --carding <NUM>
For carding attacks to payment-information API URL: 
<NUM> is the number of times an IP or cart can return a 400 (declined) from the payment api before being banned. 
1 is very aggressive and should be used only when under active attack by several different ranges of IPs. This is because a legit customer can also receive a 400 error when a card is denied, or they enter the wrong zipcode. Immune to this setting, an IP that returns a 400 from the payment api and has not accessed any static files (pub/static) will be automatically banned. 
Set cron every 1min example: /usr/bin/python /srv/mmautoban/mmautoban.py --carding 3 >> /srv/mmautoban/mmautoban.log
Logs/stats will be in /srv/mmautoban/mmautoban.log

Option: --unban
To unban previously banned carts/IPs unless the store is currently under attack. 
Set cron every 2hrs: /usr/bin/python /srv/mmautoban/mmautoban.py --unban >> /srv/mmautoban/mmautoban.log
Logs for unban will be in /srv/mmautoban/mmautoban.log

Option: --torexits
Blocks TOR exit nodes and keeps the list up to date via cron
Set cron to once a day: /usr/bin/python /srv/mmautoban/mmautoban.py --torexits >> /srv/mmautoban/mmautoban.log
Logs for TOR will be in /srv/mmautoban/mmautobanTOR.log

Option: --custom -l -m -r
Choose any path to monitor for excessive POSTS
-l <limit> = the max number of POSTS allowed to the path before an IP is banned
-m <minutes> = time frame in minutes to count the POSTS above
-r <refresh> = how often should we refresh everything and unban IPs (in minutes)
Set cron to every 1 min
Example: This cron will block an IP if it posts to myadminpath/ more than 10 times in 60 minutes. It will refresh confs/unban those IPs every 120 minutes. ( unless the site is currently under attack )
/usr/bin/python /srv/mmautoban/mmautoban.py --custompath myadminpath/ -l 10 -m 60 -r 120 >> /srv/mmautoban/mmautoban.log


# magento-mirror-1.9.4.5.tar.gz

magento.com

Latest Copy of Magento 1 for our customers that still want it installed.

# fire-in-the-hole.sh

Nemanja Djuric

Script gather abusive list from http://iplists.firehol.org/?ipset=firehol_abusers_30d RBL convert to nginx deny format and saves within /srv/.nginx/server_level/block-abusers.conf filename. RBL updates few times a day so enough to create cron task running on every 6 hours.

An ipset made from blocklists that track abusers in the last 30 days. (includes: cleantalk_new_30d cleantalk_updated_30d php_commenters_30d php_dictionary_30d php_harvesters_30d php_spammers_30d stopforumspam sblam).

Each time the IP list is changed, modified, or updated we keep track of its size (both number of entries and number of unique IPs matched). Using this information we can detect what the list maintainers do, get an idea of the list trend and its maintainers habbits.

# hop.py ( HOUSE OF PAIN )

Jackie Angus
  
8/4/2021 Version 1.1 Updates self / Added error checks for CF errors
  
Pull Attack IPs from Data Warehouse for a specific instance

  Cron Usage: python3 /srv/.nginx/hop.py --uuid INSERTUUIDHERE >> /srv/ban.log
  
  5,25,45 * * * * (At minute 5, 25, and 45)

Curls banlist for specific uuid from House Of Pain API
Checks file is not empty/exists
Converts list to nginx deny format in /srv/.nginx/server_level/INSERTUUIDHERE.conf
Updates nginx /usr/share/stratus/cli nginx.update
Rolls back if error returned from nginx.update
