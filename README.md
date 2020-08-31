# mmstrace
strace script for Magento on stratus

Good for finding the reason for a slow page or non-admin page that is giving an error. Just paste in the url of the page you want to strace. Remove this script once testing is complete.

Must be in Magento root ( pub folder for M2.1 or 2.2 template)

wget https://github.com/magemojo/mmstrace/raw/master/mmstrace.tar.gz;tar -xvzf mmstrace.tar.gz;chmod u+x mmstrace.py;./mmstrace.py

2/5/2020 Removed MHM section. Added query string usage & Redis activity. Added core_session and core_cache usage detection. 
9/29/2019 changed slow query and path list to 10 instead of 5. Added top tables accessed and count.

# blackflip.sh
Backflip v3.3 is now available. This version eliminates the need for Magento version checking and pulls MySQL data straight from Stratus courtesy of Ian, and features store-friendly nice MySQL dumps for almost zero POC hits.
