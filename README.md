# mmstrace
strace script for Magento on stratus

Good for finding the reason for a slow page or non-admin page that is giving an error. Just paste in the url of the page you want to strace. Remove this script once testing is complete.

Must be in Magento root ( pub folder for M2.1 or 2.2 template)

git clone https://github.com/magemojo/mmstrace;mv mmstrace mmdl;cd mmdl; mv mmstrace* ../;cd ..;chmod u+x mmstrace.py;./mmstrace.py

9/29/2019 changed slow query and path list to 10 instead of 5. Added top tables accessed and count.

