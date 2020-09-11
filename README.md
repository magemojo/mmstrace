# mmstrace

Jackie Angus : strace script for Magento on stratus

Good for finding the reason for a slow page or non-admin page that is giving an error. Just paste in the url of the page you want to strace. Remove this script once testing is complete.

Must be in Magento root ( pub folder for M2.1 or 2.2 template)

wget https://github.com/magemojo/mmstrace/raw/master/mmstrace.tar.gz;tar -xvzf mmstrace.tar.gz;chmod u+x mmstrace.py;./mmstrace.py

2/5/2020 Removed MHM section. Added query string usage & Redis activity. Added core_session and core_cache usage detection. 
9/29/2019 changed slow query and path list to 10 instead of 5. Added top tables accessed and count.

# blackflip.sh

Justin Waggoner

Backflip v4.0 is now available. Backflip is a multi-use backup utility. It automatically extracts Stratus details such as the MySQL username, MySQL password, and MySQL database name for a nice POC-friendly MySQL dump. The script will dump and package everything neatly and report to you the location of the generated backup. All you have to do is press a key, enter a doc root and Backflip will do the rest.

3.3 additions: This version eliminates the need for Magento version checking and pulls MySQL data straight from Stratus courtesy of Ian, and features store-friendly nice MySQL dumps for almost zero POC hits.

# dns.sh

Steven Jackson

DNS quick-script to show WHOIS info, DNS records, mail records, DKIM, SSL info. 
