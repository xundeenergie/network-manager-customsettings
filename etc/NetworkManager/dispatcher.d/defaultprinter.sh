#!/bin/bash

PRINTERSCRIPT=/etc/NetworkManager/defaultprinter.py
DEFAULTPRINTER="PDF"
echo $CONNECTION_ID $CONNECTION_UUID $CONNECTION_FILENAME


## Funktionen durchführen, je nach Aktion eine andere
case "$2" in
	pre-up)
		;;

        up)
		$PRINTERSCRIPT -f "$CONNECTION_FILENAME" -C
                ;;

        pre-down)
		;;

	down)
		$PRINTERSCRIPT -C
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

       *)
                echo $"Usage: $0 <interface> {pre-up|up|pre-down|down|vpn-pre-up|vpn-up|vpn-pre-down|vpn-down|hostname|dhcp4-change|dhcp6-change}"
		echo $"<interface> = {eth[0-9]|wlan[0-9]}"
                exit 1
esac

exit 0

#nmcli  con show --active
activ_con=($(nmcli -t -f UUID con show --active ))
[[ x"${activ_con[0]}" = "x" ]] && active_con=default
