#Put together by Steven Jackson 7/9/2019

read  -p "whats the domain? " domain

echo -e "\n \n \n ==================================================== \n DNS INFO FOR $domain \n ==================================================== \n"
#Whois
        echo -e "\n\e[30;48;5;44m WHOIS: \e[0m"
        domain2=$(echo $domain | sed -r 's/.*\.([^.]+\.[^.]+)$/\1/' )
        timeout 4 whois $domain2 | awk '/rar:/ {print} /ate:/ {print} /tus:/ {print} /No match/ {print}'

#DNS info
        echo -e "\n\e[30;48;5;44m DNS info: \e[0m"
        maindig(){(echo -e "Host\t\t TTL\t Type\t Pointed-To\n"
        dig ${domain} ns | sed -n '/QUESTION/,/ADDITIONAL/p' | sed -n '/ANSWER/,/ADDITIONAL/p' \
        | grep ${domain} | awk -vOFS='\t' '{print $1, $2, $4, $5}'
        dig ${domain} | sed -n '/QUESTION/,/ADDITIONAL/p' | sed -n '/ANSWER/,/ADDITIONAL/p' \
        | grep ${domain} | awk -vOFS='\t' '{print $1, $2, $4, $5}'
        dig ${domain} mx | sed -n '/QUESTION/,/ADDITIONAL/p' | sed -n '/ANSWER/,/ADDITIONAL/p' \
        | grep ${domain} | awk -vOFS='\t' '{print $1, $2, $4, $6}'
        dig www.${domain} | sed -n '/QUESTION/,/ADDITIONAL/p' | sed -n '/ANSWER/,/ADDITIONAL/p' \
        | grep ${domain} | awk -vOFS='\t' '{print $1, $2, $4, $5}'

        if [[ $(dig ${domain} mx | grep -A 1 ANSWER | grep ${domain} | awk '{print $6}') == mail.${domain}. ]]
        then
                dig mail.${domain} | grep -A 1 ANSWER | grep ${domain} | awk -vOFS='\t' '{print $1, $2, $4, $5}'
        fi)
        }

        maindig

        printf "\nrDNS lookup results of above IP's:\n\n"
        for f in $(maindig | grep -Eo '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}'); do echo -ne "$f\t" && dig -x $f +short; done
        printf "\n"

#Mail Section
        echo -e "\n\n\e[30;48;5;44m Mail records: \e[0m\n"
#SPF
        spf=$(dig +nocmd $1 txt +multiline +noall +answer \
        | awk -F'"' '/spf/{print $2}')

        if [[ ${#spf} > 0 ]]; then
            echo -e "SPF:\n\n$spf"
        else
            echo -e "$domain does not appear to have an SPF configured!"
        fi

#DKIM
        dkim=$(dig "default._domainkey.${domain}" txt +nocmd +short \
        | awk -F'"|;|=|\\\\' '{print $9$11}')
        if [[ ${#dkim} = 0 ]]; then
            dkim=$(dig "default._domainkey.${domain}" txt +nocmd +short \
            | awk -F'p=|"' '{print $3}')
        fi
          if [[ ${#dkim} > 0 ]]; then
            pretty_dkim="-----BEGIN PUBLIC KEY-----\n${dkim}\n-----END PUBLIC KEY-----"
            echo -e "\nDKIM:\n"
            echo -e $pretty_dkim | fold -w 64 | openssl rsa -noout -text -pubin | head -1
            echo
            echo -e $pretty_dkim | fold -w 64
        else
            echo -e "\n$domain does not appear to have a DKIM configured at default._domainkey.$domain"
        fi

#DMARC
        dmarc=$(dig _dmarc.$domain txt +noall +answer +short \
        | grep 'DMARC' \
        | tr -d \")
        if [[ ${#dmarc} > 0 ]]; then
            echo -e "\nDMARC:\n\n$dmarc"
        else
            echo -e "\n$domain does not appear to have a DMARC configured!"
        fi
        echo

#Curl
        echo -e "\n\e[30;48;5;44m Domain Status: \e[0m\n"
        timeout 4s curl -IL $domain --max-redirs 4 2>&1 |  awk '/HTTP/{print $2, $3, $4} /Location/ {print "To: " $2} /Couldn/ {print "\033[1;31m"  $3, $4, $5 "\033[0m"} '

#SSL
        echo -e "\n\n\e[30;48;5;44m SSL Info: \e[0m\n"
        ssl=$(timeout 4s echo -n \
        | openssl s_client -connect ${1}:${2:-443} -servername $domain 2>/dev/null \
        | openssl x509 -dates -serial -issuer -subject -text \
        | awk '/Not B/ {print "Issued: " $3, $4, $5, $6 } /Not A/ {print "Expires: " $4, $5, $6, $7 } /Issuer/ {print }' | head -4 )
        if [[ ${#ssl} > 1 ]]; then
           echo -e "SSL:\n\n$ssl"
        else
           echo -e "$domain does not appear to have an SSL installed!\n"
        fi
  echo ""

#Deletes the file
rm -f dns.txt
