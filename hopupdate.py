#!/usr/bin/env python
# Abusive IP Grabber from MageMojo HOP Updater 1.0

import os
import time

# Wait 2 seconds to be sure hop.py has closed
time.sleep(2)

# copy latest file to hop.py
moveit = "mv ./hop.check /srv/.nginx/hop.py"
os.system(moveit)

remove = "rm ./hopupdate.py"
os.system(remove)