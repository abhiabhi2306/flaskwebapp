#!/usr/bin/env bash

clear
echo "*******FLASK WEBAPP**********"
echo ""
echo "******* Installing libraries Please Give 'Y' if prompted****** "
sudo apt-get install -y python python-setuptools python-dev build-essential python-pip python-mysqldb
python app.py flask run --host=0.0.0.0
