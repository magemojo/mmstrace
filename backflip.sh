#!/bin/bash
############################################
#        Stratus Backup Script v4.2        #
############################################
#        Multi-use Backup Utility!         #
#                                          #
#     FOR USE ON STRATUS SYSTEMS ONLY      #
#                                          #
############################################
# Usage: ./backflip.sh                     #
############################################
# Report bugs: justin@webscalenetworks.com #
############################################
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
echo "Press [1]: Full Backup"
echo "Press [2]: Database Only"
echo "Press [3]: Files Only"
echo "Press [4]: Full Backup (No media)"
echo "Press [5]: Files Only (No media)"
echo "Press [Q]: Exit"
echo ""
echo "======================================="
echo "***************************************"
read -p "Please make a selection: " -n 1 -r
echo ""

################################################
## CASE MATCHES INPUT DUMPS TO REPLY VARIABLE ##
################################################

case $REPLY in

##############################
## SELECTION 1: Full Backup ##
##############################

1) clear
echo "###################################"
echo "###                             ###"
echo "###    [ FULL BACKUP SETUP ]    ###"
echo "###                             ###"
echo "###################################"
echo ""
echo "1.) Creates files backup."
echo "2.) Creates MySQL backup."
echo ""
echo "###################################"
echo "#   !!!Please use responsibly!!!  #"
echo "###################################"
echo ""
read -p "Press [Enter] key to continue..."
clear

echo ""
echo "Specify Docroot (E.g., public_html)."
echo "#############################################"
echo "# TIP: No spaces. No slashes. No backspace. #"
echo "#############################################"
read -p "Docroot: " WEB

[[ -z "$WEB" ]] && { echo "" && echo "ERROR: Blank input not permitted!"; sleep 2 && echo "" && echo "Restarting script now..." && sleep 3 && bash $(basename $0) && exit; }

clear
echo ""
echo "Grabbing MySQL information from Stratus..."
echo ""
sleep 3

#########################
## STRATUS MYSQL PARSE ##
##       [ SMP1 ]      ##
#########################
##    By: Ian Carey    ##
#########################

cd "/srv"

/usr/share/stratus/cli database.config > streetcred.log 2>&1

STUSR=$(cat streetcred.log | grep Username | awk '{print $3}' | cut -c3- | rev | cut -c4- | rev)
DAB=$(cat streetcred.log | grep Username | awk '{print $7}' | cut -c3- | rev | cut -c4- | rev)
STPAS=$(cat streetcred.log | grep Username | awk '{print $14}' | cut -c3- | rev | cut -c4- | rev)

clear
echo "#####################################"
echo "###                               ###"
echo "###     [ USER INPUT REVIEW ]     ###"
echo "###                               ###"
echo "#####################################"
echo ""
echo "Please review your inputs."
echo ""
echo "DOCROOT: /srv/[$WEB]"
echo ""
echo "#####################################"
echo "###     [ STRATUS CLI REVIEW ]    ###"
echo "#####################################"
echo ""
echo "DATABASE: [$DAB]"
echo ""
echo "USERNAME: [$STUSR]"
echo ""
echo "PASSWORD: [$STPAS]"
echo ""
echo "#####################################"
echo "#####################################"
echo ""
read -p "Are you sure you wish to proceed (Y/N)?" -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]
then

clear

YOLO="backup_$(date +%Y-%m-%d)"

echo "Cool story! Setting up the script environment..."
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

nice -n 15 /usr/bin/mysqldump -h mysql -u $STUSR -p$STPAS --single-transaction --no-tablespaces --opt --skip-lock-tables --max_allowed_packet=512M $DAB > $DAB.sql && sed -i 's/DEFINER=[^*]*\*/\*/g' $DAB.sql && gzip $DAB.sql 

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

########################################################################
########################################################################
##                                                                    ##
##                   ..::[  MENU SELECTION 2 ]::..                    ##
##                                                                    ##
########################################################################
########################################################################


################################
## SELECTION 2: Database Only ##
################################

2) clear
echo "####################################"
echo "###                              ###"
echo "###     [ MySQL DUMP SETUP ]     ###"
echo "###                              ###"
echo "####################################"
echo ""
echo "1.) POC-Friendly dump."
echo "2.) Removes definers."
echo ""
echo "####################################"
echo "#   !!!Please use responsibly!!!   #"
echo "####################################"
echo ""
read -p "Press [Enter] key to continue..."
clear

echo ""
echo "Grabbing MySQL information from Stratus..."
echo ""
sleep 3


#########################
## STRATUS MYSQL PARSE ##
##       [ SMP2 ]      ##
#########################
##    By: Ian Carey    ##
#########################

cd "/srv"

/usr/share/stratus/cli database.config > streetcred.log 2>&1

STUSR=$(cat streetcred.log | grep Username | awk '{print $3}' | cut -c3- | rev | cut -c4- | rev)
DAB=$(cat streetcred.log | grep Username | awk '{print $7}' | cut -c3- | rev | cut -c4- | rev)
STPAS=$(cat streetcred.log | grep Username | awk '{print $14}' | cut -c3- | rev | cut -c4- | rev)

clear
echo "#####################################"
echo "###     [ STRATUS CLI REVIEW ]    ###"
echo "#####################################"
echo ""
echo "DATABASE: [$DAB]"
echo ""
echo "USERNAME: [$STUSR]"
echo ""
echo "PASSWORD: [$STPAS]"
echo ""
echo "#####################################"
echo "#####################################"
echo ""
read -p "Are you sure you wish to proceed (Y/N)?" -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]
then

clear

YOLO="db_$(date +%Y-%m-%d)"

echo "Freshly squeezed cranberry juice coming up!"
echo ""

mkdir backups > /dev/null 2>&1
cd "/srv/backups"
mkdir db > /dev/null 2>&1
cd "/srv/backups/db"

echo "Dumping MySQL database...Hold your clicks, it could be awhile!"
echo ""

#############################
##   PLAY NICE WITH MYSQL  ##
##      w/ love Jackie     ##
#############################

nice -n 15 /usr/bin/mysqldump -h mysql -u $STUSR -p$STPAS --single-transaction --no-tablespaces --opt --skip-lock-tables --max_allowed_packet=512M $DAB > $DAB.sql && sed -i 's/DEFINER=[^*]*\*/\*/g' $DAB.sql && gzip $DAB.sql

mv $DAB.sql.gz $YOLO.sql.gz
cd "/srv"
rm -f "/srv/streetcred.log"

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
echo " /srv/backups/db/$YOLO.sql.gz"
echo ""
echo "+==================================================================+"
echo "|           ..::[ Don't forget to remove the script ]::..          |"
echo "+==================================================================+"
echo ""

else
exit 0
fi
;;

########################################################################
########################################################################
##                                                                    ##
##                   ..::[  MENU SELECTION 3 ]::..                    ##
##                                                                    ##
########################################################################
########################################################################


#############################
## SELECTION 3: Files-Only ##
#############################

3) clear
echo "###################################"
echo "###                             ###"
echo "###    [ FILES-ONLY BACKUP ]    ###"
echo "###                             ###"
echo "###################################"
echo ""
echo "1.) Creates a files-only backup."
echo ""
echo "###################################"
echo "#   !!!Please use responsibly!!!  #"
echo "###################################"
echo ""
read -p "Press [Enter] key to continue..."
clear

echo ""
echo "Specify Docroot (E.g., public_html)."
echo "#############################################"
echo "# TIP: No spaces. No slashes. No backspace. #"
echo "#############################################"
read -p "Docroot: " WEB

[[ -z "$WEB" ]] && { echo "" && echo "ERROR: Blank input not permitted!"; sleep 2 && echo "" && echo "Restarting script now..." && sleep 3 && bash $(basename $0) && exit; }

clear
echo "#####################################"
echo "###                               ###"
echo "###     [ USER INPUT REVIEW ]     ###"
echo "###                               ###"
echo "#####################################"
echo ""
echo "Please review your inputs."
echo ""
echo "DOCROOT: /srv/[$WEB]"
echo ""
echo "#####################################"
echo "#####################################"
echo ""
read -p "Are you sure you wish to proceed (Y/N)?" -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]
then

clear

YOLO="files_$(date +%Y-%m-%d)"

echo "Awesome! Setting up the script environment..."
echo ""

cd "/srv"
mkdir backups > /dev/null 2>&1
cd "/srv/backups"
mkdir $YOLO
cd "/srv/backups/$YOLO"
mkdir files/
echo "This is a files-only archive. Does not contain database." > README.md
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

########################################################################
########################################################################
##                                                                    ##
##                   ..::[  MENU SELECTION 4 ]::..                    ##
##                                                                    ##
########################################################################
########################################################################


#########################################
## SELECTION 4: Full Backup (No Media) ##
#########################################

4) clear
echo "##############################################"
echo "###                                        ###"
echo "###    [ FULL BACKUP SETUP (No Media) ]    ###"
echo "###                                        ###"
echo "##############################################"
echo ""
echo "1.) Creates files backup."
echo "2.) Creates MySQL backup."
echo "3.) Excludes media from archive."
echo ""
echo "##############################################"
echo "#        !!!Please use responsibly!!!        #"
echo "##############################################"
echo ""
read -p "Press [Enter] key to continue..."
clear

echo ""
echo "Specify Docroot (E.g., public_html)."
echo "#############################################"
echo "# TIP: No spaces. No slashes. No backspace. #"
echo "#############################################"
read -p "Docroot: " WEB

[[ -z "$WEB" ]] && { echo "" && echo "ERROR: Blank input not permitted!"; sleep 2 && echo "" && echo "Restarting script now..." && sleep 3 && bash $(basename $0) && exit; }

clear
echo ""
echo "Grabbing MySQL information from Stratus..."
echo ""
sleep 3

#########################
## STRATUS MYSQL PARSE ##
##       [ SMP4 ]      ##
#########################
##    By: Ian Carey    ##
#########################

cd "/srv"

/usr/share/stratus/cli database.config > streetcred.log 2>&1

STUSR=$(cat streetcred.log | grep Username | awk '{print $3}' | cut -c3- | rev | cut -c4- | rev)
DAB=$(cat streetcred.log | grep Username | awk '{print $7}' | cut -c3- | rev | cut -c4- | rev)
STPAS=$(cat streetcred.log | grep Username | awk '{print $14}' | cut -c3- | rev | cut -c4- | rev)

clear
echo "#####################################"
echo "###                               ###"
echo "###     [ USER INPUT REVIEW ]     ###"
echo "###                               ###"
echo "#####################################"
echo ""
echo "Please review your input."
echo ""
echo "DOCROOT: /srv/[$WEB]"
echo ""
echo "#####################################"
echo "###     [ STRATUS CLI REVIEW ]    ###"
echo "#####################################"
echo ""
echo "DATABASE: [$DAB]"
echo ""
echo "USERNAME: [$STUSR]"
echo ""
echo "PASSWORD: [$STPAS]"
echo ""
echo "#####################################"
echo "#####################################"
echo ""
read -p "Are you sure you wish to proceed (Y/N)?" -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]
then

clear

YOLO="nomedia_$(date +%Y-%m-%d)"

echo "Oh snap! Setting up the script environment..."
echo ""

mkdir backups > /dev/null 2>&1
cd "/srv/backups"
mkdir $YOLO
cd "/srv/backups/$YOLO"
mkdir files/
mkdir database/
echo "This is a limited archive. Does not contain media." > README.md
cd "/srv/backups/$YOLO/database"

echo "Dumping MySQL database...Hold your clicks, it could be awhile!"
echo ""

#############################
##   PLAY NICE WITH MYSQL  ##
##      w/ love Jackie     ##
#############################

nice -n 15 /usr/bin/mysqldump -h mysql -u $STUSR -p$STPAS --single-transaction --no-tablespaces --opt --skip-lock-tables --max_allowed_packet=512M $DAB > $DAB.sql && sed -i 's/DEFINER=[^*]*\*/\*/g' $DAB.sql && gzip $DAB.sql 

cd "/srv"

##############################
##   EXCLUDE LARGE THINGS   ##
##      w/ love Bojan       ##
##############################

/bin/tar --exclude=$WEB/media -cvzf /srv/backups/$YOLO/files/$WEB.tar.gz $WEB/
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

########################################################################
########################################################################
##                                                                    ##
##                   ..::[  MENU SELECTION 5 ]::..                    ##
##                                                                    ##
########################################################################
########################################################################


########################################
## SELECTION 5: Files-Only (No Media) ##
########################################

5) clear

echo "#############################################"
echo "###                                       ###"
echo "###    [ FILES-ONLY BACKUP (No Media ]    ###"
echo "###                                       ###"
echo "#############################################"
echo ""
echo "1.) Creates a files-only backup."
echo "2.) Excludes media from archive."
echo ""
echo "#############################################"
echo "#       !!!Please use responsibly!!!        #"
echo "#############################################"
echo ""
read -p "Press [Enter] key to continue..."
clear

echo ""
echo "Specify Docroot (E.g., public_html)."
echo "#############################################"
echo "# TIP: No spaces. No slashes. No backspace. #"
echo "#############################################"
read -p "Docroot: " WEB

[[ -z "$WEB" ]] && { echo "" && echo "ERROR: Blank input not permitted!"; sleep 2 && echo "" && echo "Restarting script now..." && sleep 3 && bash $(basename $0) && exit; }

clear
echo "#####################################"
echo "###                               ###"
echo "###     [ USER INPUT REVIEW ]     ###"
echo "###                               ###"
echo "#####################################"
echo ""
echo "Please review your inputs."
echo ""
echo "DOCROOT: /srv/[$WEB]"
echo ""
echo "#####################################"
echo "#####################################"
echo ""
read -p "Are you sure you wish to proceed (Y/N)?" -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]
then

clear

YOLO="files_$(date +%Y-%m-%d)"

echo "Awesome! Setting up the script environment..."
echo ""

cd "/srv"
mkdir backups > /dev/null 2>&1
cd "/srv/backups"
mkdir $YOLO
cd "/srv/backups/$YOLO"
mkdir files/
echo "This is a limited files-only archive. Does not contain media or database." > README.md
cd "/srv"

##############################
##   EXCLUDE LARGE THINGS   ##
##      w/ love Bojan       ##
##############################

/bin/tar --exclude=$WEB/media -cvzf /srv/backups/$YOLO/files/$WEB.tar.gz $WEB/
cd "/srv/backups"
tar -czvf $YOLO.tar.gz $YOLO
rm -f "/srv/streetcred.log"
rm -rf "/srv/backups/$YOLO"

else
exit 0
fi
;;

##############################
## Selection Q: Script Exit ##
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
echo "Invalid selection. Please choose either: 1, 2, 3, 4, 5 or Q"
sleep 2
echo ""
echo "Restarting script now..."
sleep 3
bash $(basename $0) && exit;;
esac
