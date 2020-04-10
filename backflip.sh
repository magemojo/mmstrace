#!/bin/bash
#MageMojo Backup Script v3.2
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
echo "Checking installed Magento version..."
echo ""
sleep 3

###################################
## STRATUS MAGENTO VERSION AUDIT ##
###################################

FILE="/srv/$WEB/app/etc/local.xml"
FILE2="/srv/$WEB/app/etc/env.php"

###########################################
## CHECK M1/M2 CONFIGS IN SAME DIRECTORY ##
###########################################


if [ -e "$FILE" ] && [ -e "$FILE2" ];
        then
                clear
                echo ""
                        echo "Something went wrong, Dave."
                echo ""
                sleep 2
                        echo "My sensors have detected both versions of Magento."
                echo ""
                sleep 1
                        echo "Please manually check which version is installed."
                echo ""
                sleep 1
                        echo "Exiting now...Goodbye Dave."
                echo ""
                exit

########################
## CHECK IF M1 EXISTS ##
########################

        elif [ -e "$FILE" ];
        then

                echo "Magento 1 detected."
		sleep 3
                echo ""

                        EPGREP=`cat $FILE | grep -m 1 host`
                                STEP="${EPGREP/<host><![CDATA[/}"
                                STEP="${STEP/]]><\/host>/}"
                                STEP="${STEP// /}"
                                STEP=$(echo "$STEP" | tr -d '\r')

                        DBGREP=`cat $FILE | grep -m 1 dbname`
                                DAB="${DBGREP/<dbname><![CDATA[/}"
                                DAB="${DAB/]]><\/dbname>/}"
                                DAB="${DAB// /}"
                                DAB=$(echo "$DAB" | tr -d '\r')

                        USGREP=`cat $FILE | grep -m 1 username`
                                STUSR="${USGREP/<username><![CDATA[/}"
                                STUSR="${STUSR/]]><\/username>/}"
                                STUSR="${STUSR// /}"
                                STUSR=$(echo "$STUSR" | tr -d '\r')

                        PSGREP=`cat $FILE | grep -m 1 password`
                                STPAS="${PSGREP/<password><![CDATA[/}"
                                STPAS="${STPAS/]]><\/password>/}"
                                STPAS="${STPAS// /}"
                                STPAS=$(echo "$STPAS" | tr -d '\r')
                echo ""

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
echo "ENDPOINT: [$STEP]"
echo ""
echo "DATABASE: [$DAB]"
echo ""
echo "USERNAME: [$STUSR]"
echo ""
echo "PASSWORD: [$STPAS]"
echo ""
echo "*******************************"
df -h
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

cd "/srv"

mkdir backups > /dev/null 2>&1
cd "/srv/backups"
mkdir $YOLO
cd "/srv/backups/$YOLO"
mkdir files/
mkdir database/
cd "/srv/backups/$YOLO/database"

echo "Dumping MySQL database...Hold your clicks, it could be awhile!"
echo ""

/usr/bin/mysqldump -h $STEP -u $STUSR -p$STPAS $DAB > $DAB.sql && sed -i 's/DEFINER=[^*]*\*/\*/g' $DAB.sql && gzip $DAB.sql

cd "/srv"
/bin/tar -cvzf /srv/backups/$YOLO/files/$WEB.tar.gz $WEB/
cd "/srv/backups"
tar -czvf $YOLO.tar.gz $YOLO
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

########################
## CHECK IF M2 EXISTS ##
########################

        elif [ -e "$FILE2" ];
        then
                echo "Magento 2 Detected."
                echo ""
                        DAB=$(php -r '$data = include '"'$FILE2'"'; print $data["db"]["connection"]["default"]["dbname"];')
                        STEP=$(php -r '$data2 = include '"'$FILE2'"'; print $data2["db"]["connection"]["default"]["host"];')
                        STUSR=$(php -r '$data3 = include '"'$FILE2'"'; print $data3["db"]["connection"]["default"]["username"];')
                        STPAS=$(php -r '$data4 = include '"'$FILE2'"'; print $data4["db"]["connection"]["default"]["password"];')
                echo ""
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
echo "ENDPOINT: [$STEP]"
echo ""
echo "DATABASE: [$DAB]"
echo ""
echo "USERNAME: [$STUSR]"
echo ""
echo "PASSWORD: [$STPAS]"
echo ""
echo "*******************************"
df -h
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

cd "/srv"

mkdir backups > /dev/null 2>&1
cd "/srv/backups"
mkdir $YOLO
cd "/srv/backups/$YOLO"
mkdir files/
mkdir database/
cd "/srv/backups/$YOLO/database"

echo "Dumping MySQL database...Hold your clicks, it could be awhile!"
echo ""

/usr/bin/mysqldump -h $STEP -u $STUSR -p$STPAS $DAB > $DAB.sql && sed -i 's/DEFINER=[^*]*\*/\*/g' $DAB.sql && gzip $DAB.sql

cd "/srv"
/bin/tar -cvzf /srv/backups/$YOLO/files/$WEB.tar.gz $WEB/
cd "/srv/backups"
tar -czvf $YOLO.tar.gz $YOLO
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

        else

###############################
## NO MAGENTO VERSIONS FOUND ##
###############################

    clear
            echo ""
                echo "No Magento installations detected.."
            echo ""
        sleep 1
                echo "Please manually check for installations."
            echo ""
        sleep 2
                echo "Exiting now...Goodbye Dave."
           echo ""
        sleep 3
    exit

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
