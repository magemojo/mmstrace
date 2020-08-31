#!/bin/bash
#MageMojo Backup Script v3.3
#Backup client stuff in a flash!
#
# ***WARNING - READ INSTRUCTIONS BEFORE USE***
#
# ***FOR USE ON STRATUS SYSTEMS ONLY***
#
#Be sure you are entering correct information.
#
#Usage: ./backflip.sh
#
#Example: Creates backup_12-25-2017.tar.gz
#
#Report bugs to justin@magemojo.com
clear
echo "======================================="
echo "======================================="
echo "▄▄▄▄·  ▄▄▄·  ▄▄· ▄ •▄ ·▄▄▄▄▄▌  ▪   ▄▄▄·"
echo "▐█ ▀█▪▐█ ▀█ ▐█ ▌▪█▌▄▌▪▐▄▄·██•  ██ ▐█ ▄█"
echo "▐█▀▀█▄▄█▀▀█ ██ ▄▄▐▀▀▄·██▪ ██▪  ▐█· ██▀·"
echo "██▄▪▐█▐█ ▪▐▌▐███▌▐█.█▌██▌.▐█▌▐▌▐█▌▐█▪·•"
echo "·▀▀▀▀  ▀  ▀ ·▀▀▀ ·▀  ▀▀▀▀ .▀▀▀ ▀▀▀.▀   "
echo "     =============================     "
echo "          .::[Setup Menu]::.           "
echo "======================================="
echo "======================================="
echo ""
echo "Press [1]: Create Stratus Backup"
echo "Press [Q]: Exit"
echo ""

#####################
## READ USER INPUT ##
#####################

echo "======================================="
echo "***************************************"
read -p "Please make a selection: " -n 1 -r
echo ""

################################################
## CASE MATCHES INPUT DUMPS TO REPLY VARIABLE ##
################################################

case $REPLY in

########################################
## SELECTION 1: Create Stratus Backup ##
########################################

1) clear
echo "***********************************"
echo "***     BACKUP SCRIPT SETUP     ***"
echo "***********************************"
echo ""
echo "1.) Creates backup of docroot"
echo "2.) Dumps Stratus database."
echo ""
echo "***********************************"
echo "   !!!Please use responsibly!!!"
echo "***********************************"
echo ""
read -p "Press [Enter] key to continue..."
clear

echo ""
echo "Specify Docroot (E.g., public_html)."
echo "==============================="
echo "TIP: Ensure no spaces."
echo "==============================="
read -p "Docroot: " WEB
echo ""

clear
echo ""
echo "Grabbing MySQL information from Stratus..."
echo ""
sleep 3

#########################
## STRATUS MYSQL PARSE ##
#########################
##    By: Ian Carey    ##
#########################

cd "/srv"

/usr/share/stratus/cli database.config > streetcred.log 2>&1


STUSR=$(cat streetcred.log | grep Username | awk '{print $3}' | cut -c3- | rev | cut -c4- | rev)
DAB=$(cat streetcred.log | grep Username | awk '{print $7}' | cut -c3- | rev | cut -c4- | rev)
STPAS=$(cat streetcred.log | grep Username | awk '{print $14}' | cut -c3- | rev | cut -c4- | rev)

clear
echo "********************************"
echo "***   BACKUP SETUP REVIEW    ***"
echo "********************************"
echo ""
echo "Please review the collected"
echo "data and verify correct."
echo ""
echo "DOCROOT: /srv/[$WEB]"
echo ""
echo "DATABASE: [$DAB]"
echo ""
echo "USERNAME: [$STUSR]"
echo ""
echo "PASSWORD: [$STPAS]"
echo ""
echo "*******************************"
echo "*******************************"
echo ""
read -p "Are you sure you wish to proceed (Y/N)?" -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]
then

clear

YOLO="backup_$(date +%Y-%m-%d)"

echo "Awww yeah lets get busy! Setting up script environment..."
echo ""

mkdir backups > /dev/null 2>&1
cd "/srv/backups"
mkdir $YOLO
cd "/srv/backups/$YOLO"
mkdir files/
mkdir database/
cd "/srv/backups/$YOLO/database"

echo "Dumping MySQL database...Hold your clicks, it could be awhile!"
echo ""

#############################
##   PLAY NICE WITH MYSQL  ##
##      w/ love Jackie     ##
#############################


nice -n 15 /usr/bin/mysqldump -h mysql -u $STUSR -p$STPAS --single-transaction --opt --skip-lock-tables --max_allowed_packet=512M $DAB > $DAB.sql && sed -i 's/DEFINER=[^*]*\*/\*/g' $DAB.sql && gzip $DAB.sql 


cd "/srv"
/bin/tar -cvzf /srv/backups/$YOLO/files/$WEB.tar.gz $WEB/
cd "/srv/backups"
tar -czvf $YOLO.tar.gz $YOLO
rm -f "/srv/streetcred.log"
rm -rf "/srv/backups/$YOLO"

clear

echo "+==================================================================+"
echo "| █████╗ ██╗     ██╗         ██████╗  ██████╗ ███╗   ██╗███████╗██╗|"
echo "|██╔══██╗██║     ██║         ██╔══██╗██╔═══██╗████╗  ██║██╔════╝██║|"
echo "|███████║██║     ██║         ██║  ██║██║   ██║██╔██╗ ██║█████╗  ██║|"
echo "|██╔══██║██║     ██║         ██║  ██║██║   ██║██║╚██╗██║██╔══╝  ╚═╝|"
echo "|██║  ██║███████╗███████╗    ██████╔╝╚██████╔╝██║ ╚████║███████╗██╗|"
echo "|╚═╝  ╚═╝╚══════╝╚══════╝    ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝|"
echo "+==================================================================+"
echo "===================================================================="
echo ""
echo " Backup Location:"
echo ""
echo " /srv/backups/$YOLO.tar.gz"
echo ""
echo "+==================================================================+"
echo "|           ..::[ Don't forget to remove the script ]::..          |"
echo "+==================================================================+"
echo ""

else
exit 0
fi
;;

##############################
## Selection 3: Script Exit ##
##############################

q)
exit
;;

################################
## WRONG INPUT DISPLAYS SUCH. ##
## GIVES VALID OPTIONS.       ##
## RESTARTS SCRIPT            ##
################################

*) echo "" 
echo "Invalid selection. Please choose either: 1 or Q"
sleep 2
echo ""
echo "Restarting script now..."
sleep 3
bash $(basename $0) && exit;;
esac
