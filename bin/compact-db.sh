#!/bin/bash

COUCHDB=`mygpo/print-couchdb.py`

curl -s -H "Content-Type: application/json" -X POST $COUCHDB/_compact > /dev/null

