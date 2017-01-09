#!/bin/bash
PRINTERSCRIPT=/usr/bin/nm-defaultprinter.py
UPDATESCRIPT=/usr/bin/nm-updatecheck.py
DEFAULTPRINTER="PDF"
echo $CONNECTION_ID $CONNECTION_UUID $CONNECTION_FILENAME $2


## Funktionen durchführen, je nach Aktion eine andere
case "$2" in
	pre-up)
		;;

        up)
		$PRINTERSCRIPT -i "$CONNECTION_ID" -C
		#$UPDATESCRIPT -i "$CONNECTION_ID" -C
                ;;

        pre-down)
		;;

	down)
		#echo "DOWN DEFAULTPRINTER: " $(lpstat -d|awk '{print $NF}')
		$PRINTERSCRIPT -i "$CONNECTION_ID" -S -p $(lpstat -d|awk '{print $NF}')
		$PRINTERSCRIPT -C
		#$UPDATESCRIPT -C
                ;;

	vpn-pre-up)
		;;

	vpn-up)
		;;

	vpn-pre-down)
		;;

	vpn-down)
		;;

	hostname)
		;;

	dhcp4-change)
		;;

	dhcp6-change)
		;;

	connectivity-change)
		#echo "CC DEFAULTPRINTER: " $(lpstat -d|awk '{print $NF}')
		;;

       *)
                echo $"Usage: $0 <interface> {pre-up|up|pre-down|down|vpn-pre-up|vpn-up|vpn-pre-down|vpn-down|hostname|dhcp4-change|dhcp6-change}"
		echo $"<interface> = {eth[0-9]|wlan[0-9]}"
                exit 1
esac

exit 0

#nmcli  con show --active
activ_con=($(nmcli -t -f UUID con show --active ))
[[ x"${activ_con[0]}" = "x" ]] && active_con=default
