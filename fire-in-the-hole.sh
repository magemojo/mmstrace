#!/bin/bash
#Script gather abusive list from http://iplists.firehol.org/?ipset=firehol_abusers_30d and http://iplists.firehol.org/?ipset=firehol_proxies RBL convert to nginx deny format and saves
#within /srv/.nginx/server_level/block-abusers.conf filename

function block-abusers() {
# generate the new conf
curl -s "https://iplists.firehol.org/files/firehol_abusers_30d.netset" | grep -v "^\#.*" |
while read entry ; do
	check=$(echo $entry | grep -E "^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/?[0-9]*$")
	if [ "$check" != "" ] ; then
		echo "deny ${entry};" >> /tmp/block-abusers.conf
	fi
done

# copy old conf to back if exists
if [ -f /srv/.nginx/server_level/block-abusers.conf ]; then
echo "File exists. Sending to bak"
cp /srv/.nginx/server_level/block-abusers.conf /srv/.nginx/server_level/block-abusers.conf-bak
fi

# check if we have at least 1 line
lines="$(wc -l /tmp/block-abusers.conf | cut -d ' ' -f 1)"
if [ "$lines" -gt 1 ] ; then
	echo "[BLACKLIST] abusers list updated ($lines entries)"
mv /tmp/block-abusers.conf /srv/.nginx/server_level/block-abusers.conf
RELOAD=$(/usr/share/stratus/cli nginx.update 2>&1)
fi

grep -q 'Error' <<< $RELOAD && echo "[NGINX] failed nginx reload after abusers list update fallback to old list" mv /srv/.nginx/server_level/block-abusers.conf-bak /srv/.nginx/server_level/block-abusers.conf || echo "[NGINX] successfull nginx reload after abusers list update"
}

function block-proxy() {
# generate the new conf
curl -s "https://iplists.firehol.org/files/firehol_proxies.netset" | grep -v "^\#.*" |
while read entry ; do
        check=$(echo $entry | grep -E "^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}/?[0-9]*$")
        if [ "$check" != "" ] ; then
                echo "deny ${entry};" >> /tmp/block-proxies.conf
        fi
done

# copy old conf to back if exists
if [ -f /srv/.nginx/server_level/block-proxies.conf ]; then
echo "File exists. Sending to bak"
cp /srv/.nginx/server_level/block-proxies.conf /srv/.nginx/server_level/block-proxies.conf-bak
fi

# check if we have at least 1 line
lines="$(wc -l /tmp/block-proxies.conf | cut -d ' ' -f 1)"
if [ "$lines" -gt 1 ] ; then
        echo "[BLACKLIST] proxies list updated ($lines entries)"
mv /tmp/block-proxies.conf /srv/.nginx/server_level/block-proxies.conf
RELOAD=$(/usr/share/stratus/cli nginx.update 2>&1)
fi

grep -q 'Error' <<< $RELOAD && echo "[NGINX] failed nginx reload after abusers list update fallback to old list" mv /srv/.nginx/server_level/block-proxies.conf-bak /srv/.nginx/server_level/block-proxies.conf || echo "[NGINX] successfull nginx reload after proxies list update"
}

auto_setup(){
read -p "Are you sure you want to continue? <y/N> " prompt
if [[ $prompt == "y" || $prompt == "Y" || $prompt == "yes" || $prompt == "Yes" ]]
then
block-abusers

else
  exit 0
fi
}

#End Function defs

if [ ! -z $1 ];then
	case $1 in
		abusers)
			block-abusers
			;;
		proxies)
			block-proxy
			;;
		*)
			auto_setup
			;;
	esac
else
	auto_setup
fi
