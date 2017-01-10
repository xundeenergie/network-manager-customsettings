#!/bin/bash

if /usr/bin/nm-updatecheck.py -G -c; then
  /bin/systemctl start update.target
else
  /bin/systemctl stop update.target
fi

exit 0

