#!/bin/bash
echo 
sudo sed -i 's/us.archive/se.archive/' /etc/apt/sources.list

#install needed packages
sudo apt-get update
sudo apt-get install -y apache2 unzip build-essential python-pip python-dev screen
sudo pip install zope.interface
sudo pip install autobahn websocket twisted twisted.internet.processes


cd /var/www
wget https://github.com/Daladevelop/BashThatDev-Frontend/archive/master.zip
unzip -x master.zip
mv BashThatDev-Frontend-master/* ./
rm -rf BashThatDev-Frontend-master
echo
echo
echo "Start server with run-server.sh"
