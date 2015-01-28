BashThatDev-Backend
===================

The backend for a browser based multiplayer ice-climber inspired game.


For easy development there is a vagrant box for this setup. 
Install Vagrant Either from http://vagrantup.com or from your local packet distribution system, ie: sudo apt-get install vagrant

then simply run vagrant up and wait for 5 minutes while all packages install and compile. 

It also downloads latest version of the frontend from github. Note: It only pulls the lates on initial provisioning. After that you have to manually download any new versions.To connect to the server do 'vagrant ssh'. You _could_ ofcourse rerun /vagrant/import/init.sh to get latest version of the frontend. Please remove all files in /var/www prior. 

When its all done you can run ./run-server.sh to run the server. It is started inside a sceen on the server, simply press "ctrl + a +d" to detach or "ctrl + c" to exit. 

T
The host: http://moosegame.jump will be the adress for the server. 


TODO:
* Refactor the code to conform to PEP 8
* Create a LICENSE file
