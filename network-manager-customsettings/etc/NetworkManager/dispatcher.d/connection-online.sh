#!/bin/bash

echo "CMDLINE con-on 1 $1 2 $2"

#UNITS="network-online.target connection-online.target"
UNITS="connection-online.target"

case $2 in
    connectivity-change)
        if /usr/bin/nm-online --timeout 5; then
            /bin/systemctl start ${UNITS}
        else
            /bin/systemctl stop ${UNITS}
        fi
        ;;
#    up)
#        /bin/systemctl start connection-online@${1}.target
#        ;;
#    down)
#        /bin/systemctl stop connection-online@${1}.target
#        ;;
    *)
        echo "nwonline cmdline $@"
        ;;
esac

#if /usr/bin/nm-online --timeout 5; then
#    /bin/systemctl start ${UNITS}
#else
#    /bin/systemctl stop ${UNITS}
#fi

exit 0

