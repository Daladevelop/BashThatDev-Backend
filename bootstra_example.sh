#!/usr/bin/env bash
set -e # Exit script immediately on first error.
set -x # Print commands and their arguments as they are executed.

# so we can print stuff to the guests terminal if we want to
exec 3> /dev/tty1
echo >&3

function parse_yaml {
	local prefix=$2
	local s='[[:space:]]*' w='[a-zA-Z0-9_]*' fs=$(echo @|tr @ '\034')
	sed -ne "s|^\($s\):|\1|" \
		-e "s|^\($s\)\($w\)$s:$s[\"']\(.*\)[\"']$s\$|\1$fs\2$fs\3|p" \
		-e "s|^\($s\)\($w\)$s:$s\(.*\)$s\$|\1$fs\2$fs\3|p"  $1 |
	awk -F$fs '{
		indent = length($1)/2;
		vname[indent] = $2;
		for (i in vname) {if (i > indent) {delete vname[i]}}
		if (length($3) > 0) {
			vn=""; for (i=0; i<indent; i++) {vn=(vn)(vname[i])("_")}
			printf("%s%s%s=\"%s\"\n", "'$prefix'",vn, $2, $3);
		}
	}'
}
# parse our settings file
eval $(parse_yaml /vagrant/settings.yml)


# fix swap
swapon $(blkid | grep swap | awk  ' { print $2 }' | sed -e 's/"//g')
# remove faulty line
sed -i '/swap/d' /etc/fstab
# add correct
echo "$(blkid | grep swap | awk  ' { print $2 }' | sed -e 's/"//g') none swap sw 0 0" >> /etc/fstab

# set up package.json
if [ ! -f "/vagrant/package.json" ]; then
cat > /vagrant/package.json << EOF
{
	"name": "$project_title",
	"version": "1.0.0",
	"devDependencies": {
		"grunt": "~0.4.1",
		"grunt-cli": "~0.1.0",
		"grunt-contrib-concat": "~0.3.0",
		"grunt-contrib-uglify": "~0.4.0",
		"grunt-contrib-less": "~0.10.0",
		"grunt-contrib-watch": "~0.6.0",
		"grunt-phplint": "0.0.5",
		"grunt-contrib-csslint": "~0.2.0",
		"grunt-contrib-compress": "~0.11.0"
	}
}
EOF
fi

# tweak apache settings
echo -n "Setting up apache..." >&3
if [[ -n "$apache_run_user" ]]; then
	sed -i "s/export APACHE_RUN_USER=.*/export APACHE_RUN_USER=$apache_run_user/g" /etc/apache2/envvars
	sed -i "s/export APACHE_RUN_GROUP=.*/export APACHE_RUN_GROUP=$apache_run_group/g" /etc/apache2/envvars
	chown $apache_run_user:$apache_run_group /var/lock/apache2
fi
echo "done!" >&3

# tweak php settings
echo -n "Setting php settings..." >&3
sed -i "s/post_max_size = .*/post_max_size = $php_post_max_size/" /etc/php5/apache2/php.ini
sed -i "s/memory_limit = .*/memory_limit = $php_memory_limit/" /etc/php5/apache2/php.ini
sed -i "s/upload_max_filesize .*/upload_max_filesize = $php_upload_max_filesize/" /etc/php5/apache2/php.ini
if [ "$php_display_errors" == "yes" ]; then
	sed -i "s/error_reporting = .*/error_reporting = E_ALL | E_STRICT/" /etc/php5/apache2/php.ini
	sed -i "s/display_errors = .*/display_errors = On/" /etc/php5/apache2/php.ini
	sed -i "s/.*error_prepend_string = .*/error_prepend_string = \"<span style='display: block; width: 100%; position: relative; top: 0px; left: 0px; color: #ff0000; z-index: 1000; background-color: #fff; padding: 75px 20px 20px 20px; background-image: url(http:\/\/static.dalnix.se\/Dalnix_Logo_RGB.png); background-repeat: no-repeat; background-size: 100px; background-position: 20px 20px;'>\"/" /etc/php5/apache2/php.ini	
	sed -i "s/.*error_append_string = .*/error_append_string = \"<\/span>\"/" /etc/php5/apache2/php.ini
fi
echo "done!" >&3

if [ "$db_create" == "yes" ]; then
	# create database
	echo -n "creating database..." >&3
	echo "CREATE DATABASE \`$db_name\`" | mysql -u$db_user -p$db_pass
	echo "done!" >&3

	if [ "$db_autodump" == "yes" ]; then
		# set up auto dump db
		echo -n "dumping db to $db_autodump_file every $db_autodump_interval minutes..." >&3
		mkdir -p $(dirname $db_autodump_file)
		echo "*/$db_autodump_interval * * * * root mysqldump -u$db_user -p$db_pass $db_name > $db_autodump_file" > /etc/cron.d/db_autodump
	fi
fi

# start wordpress installation
if [ "$wordpress_install" == "yes" ]; then
	# alias wp so root can run
	wp="wp --allow-root"

	# install wp-cli
	echo -n "installing wp-cli..." >&3
	curl -skL https://raw.github.com/wp-cli/builds/gh-pages/phar/wp-cli.phar > /usr/local/sbin/wp
	chmod +x /usr/local/sbin/wp
	echo "done!" >&3

	# install wordpress to /var/www
	echo -n "installing wordpress..." >&3
	cd /var/www
	$wp core download --locale="$wordpress_locale"
	echo "done!" >&3

	# set up wordpress
	echo -n "setting up wordpress..." >&3
	cd /var/www
	$wp core config --dbname="$db_name" --dbuser="$db_user" --dbpass="$db_pass" --dbprefix="$wordpress_dbprefix"
	echo "done!" >&3

	# make wordpress settings
	echo -n "making new wp installation..." >&3
	cd /var/www
	$wp core install --url="$wordpress_siteurl" --title="$wordpress_blogname" --admin_user="$wordpress_admin_user" --admin_password="$wordpress_admin_password" --admin_email="$wordpress_admin_email" 
	echo "done!" >&3

	# install plugins
	echo -n "installing plugins..." >&3
	cd /var/www
	for plugin in $wordpress_plugins; do
		$wp plugin install $plugin --activate
		echo -n "$plugin..." >&3
	done
	echo "done!" >&3

	# set up permalink scructure
	echo -n "changing permalink settings..." >&3
	cd /var/www
	$wp rewrite structure "$wordpress_structure"
	echo "done!" >&3

	# install non public plugins (or cache for speed) from plugins/ dir
	if ls /vagrant/plugins/*.zip &> /dev/null; then
		echo -n "installing provided plugin zipfiles..." >&3
		cd /var/www
		for file in /vagrant/plugins/*.zip; do
			$wp plugin install $file --activate
		done
		echo "done!" >&3
	fi

	# import wordpress test data
	if [ "$wordpress_testdata" == "yes" ]; then
		echo -n "importing wordpress test data..." >&3
		cd /var/www
		curl -skL https://wpcom-themes.svn.automattic.com/demo/theme-unit-test-data.xml > /tmp/testdata.xml
		$wp import /tmp/testdata.xml --authors=create
		rm /tmp/testdata.xml
		echo "done!" >&3
	fi

	# create uploads dir
	if [ ! -d "/var/www/wp-content/uploads" ] && [ "$wordpress_install" == "yes" ]; then
		echo -n "creating uploads dir..." >&3
		mkdir -p /var/www/wp-content/uploads
		echo "done!" >&3
	fi

	# make www-data own it all (we don't really care since we're developers, right ;)
	chown -R www-data:www-data /var/www
fi # end wordpress installation


# make a pretty .htaccess, everyone wants a pretty .htaccess file, right?
echo -n "making a pretty .htaccess file..." >&3
cat > /var/www/.htaccess << EOF
<IfModule mod_rewrite.c>
RewriteEngine On
RewriteBase /
RewriteRule ^index\.php$ - [L]
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteRule . /index.php [L]
</IfModule>
EOF
chown www-data:www-data /var/www/.htaccess
echo "done!" >&3



# enable mod rewrite
echo -n "enabling mod rewrite..." >&3
a2enmod rewrite
echo "done!" >&3



# add simple vhost default
echo -n "writing a simple vhost default..." >&3
cat > /etc/apache2/sites-available/default << EOF
<VirtualHost *:80>
    ServerName $box_hostname
    ServerAlias $box_hostalias
    DocumentRoot /var/www
</VirtualHost>
EOF
echo "done!" >&3



## install popcorn start
if [ "$popcorn_install" == "yes" ] && [ "$wordpress_install" == "yes" ]; then
echo -n "installing popcorn..." >&3

# popcorn rsa key (so we can pull popcorn)
cat > /root/.ssh/popcorn_rsa << EOF
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEAxtOtx82vd4wIp42/oB8UlHGJy31P2h2Aoz3N/JpWud+szDyL
dlys4/qXETW8vqt+G0GPxYrhco3LhkthDEqsWEnNd0+2abK3MZZybhJVy25RsHd0
U4NUpH8SDQj8M7kpScg0SPiuvQB/fnz3XotjfF5UmbJSRfl532iinJKnI9YySPE6
/D+R+tIa+DsExknZDktqo63CjwqQOAaAuZtHrO6n8Lj73TdU4+MMn/5TYsj/Onb1
IiPiz3z502+02JsQF3VDelVv1d82FK7JMU9CIk8dnPyb99HRFysomovdcjaBQGVO
8gkcXm/HnpUxbuU19Q7lwb5G91g+bRvdqGzcXQIDAQABAoIBADFlgbU0GrXeqn/G
LaeAUUKX+p39ogsUbVMhFb3+MjG3qlyLZjKfz6xMI5/4882DGa932FpBqMUnCTty
GshM/QhqPYu42B7mcbD2KbPDBmGmJNFsvA/LfwnnL/rhEpdfFyznemXusqruJr6s
GWD5zFunq+kLbnlIA8lHW67+mFvEeOXwKxkzZ97sLS0rR0D301weC+gMS9ghhtzn
hW1GPBmi9rba6/QZvtngc4PVcd6822s4uvBFM2WvmoGh7245oIFrNaYlpc63pWS8
O3JA08zkk/ppycVBW5eFP1MsQw13FayqN8Ks/qnRGL6TW+InPzQmxYIqiuYZhAyN
HFmFHoECgYEA9vluWn6+8oVMDYKl0q7ECF1fJ0za3Stw/ZhEXcN4nQOBDQMoxsYS
bNBhaKLzZleD+O6kRfQE3hqj7V6WK7C+32D26njlYl9/e5273JHOc9ewhoRDZOB2
OXBhE3c6/a87NqwWFL2d439veNe458+w7ph3b8qx594bKqSXnUssM+0CgYEAzhfN
08vLYlLGe7/58Pa9P7odSWAQ0ICaT9OTLs3Tx2/Ngl8msbGkV15jxtNswiYs/2B7
As9ngZBKyPRS7mCKS0SiBZcRVrGgWQIaMnzok3X6LZSXkLoKWspHSUzEl0iPonFX
7l/9pN/irU7Uk37kQmcYTKl4hzaaN6FhPPVNHDECgYBtaAGixRMBjFssgPvEYPcm
XXaRilJKN7xOGu3uO3Fq3OqGQSgHJidzXLxKBiWc6Jfl5pGPC5I8ccC8nnIX2Kw1
eFbpd7Tl5zgqIq3eABlc5+ejL2RLg8PbnhTi8qaHSuEITyNY/Ma8yO8wsR+QUUkn
6RK/yyMUfCe8tD0VyP9D4QKBgQCM93U/CGd+QnYnESIJ8wtxeoErvjziEQT70xEa
c4kHIm8kXKcf5g0uAY8n4VfD2M7wgvLA8lKvKZ4tpAjRqlENuM1GG5WtgePW3fxD
SnLe4lSUNs4RHV+VyERIW+0gOW6dwv9NOnVJACaROplmpeXFkbTqQwUBH5UOtiDH
zFXJEQKBgA9uuuH7BpPb4DzgWlynMIJiT5s9z5fekqveLqog6K3nv2T3Dr8qJnG1
t9Uh7VZbsU76o19Yj3eHWLnTgAyh7RhsKhIyVDYb/kaa77U6cpdTgQuF5fZBW1ql
Uj+J8Oasu+e46Hzeo6bV1hgb0RfNY80b+d3gd/37419T9XBYTY6X
-----END RSA PRIVATE KEY-----
EOF
cat >> /root/.ssh/config << EOF
Host gitlab.dalnix.se
     IdentityFile ~/.ssh/popcorn_rsa
EOF
chmod 0600 /root/.ssh/popcorn_rsa
cat >> /root/.ssh/known_hosts << EOF
|1|Q2s5JJmE9YmeyRiJbyJUGV3J5jE=|eOyOOE9bXhzeh/5wL5UDfzrPLtM= ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBL6U72cBllydl3N+IK1Yli7H90eKDN0G1HsfNIKdcH3qNIUaY00sJ9i6x74hA4zKtTtDee3Kx+uAlYGPB9Rbt1o=
|1|VQxf20w4RW/8ILkquh/myPavJSU=|vccI+AddoFla2KnCMhvEyvScPWE= ecdsa-sha2-nistp256 AAAAE2VjZHNhLXNoYTItbmlzdHAyNTYAAAAIbmlzdHAyNTYAAABBBL6U72cBllydl3N+IK1Yli7H90eKDN0G1HsfNIKdcH3qNIUaY00sJ9i6x74hA4zKtTtDee3Kx+uAlYGPB9Rbt1o=
EOF

if [ ! -f "/var/www/wp-content/themes/popcorn/style.css" ]; then
	echo -n "installing popcorn parent theme..." >&3
	cd /var/www/wp-content/themes
	git clone git@gitlab.dalnix.se:dalnix/popcorn.git
	cd popcorn
	npm install --silent
	grunt
	echo "done!" >&3
else
	echo -n "updating popcorn parent theme..." >&3
	cd /var/www/wp-content/themes/popcorn
	git pull
	grunt
	echo "done!" >&3
fi

echo -n "switching to popcorn branch $popcorn_branch ..." >&3
git checkout $popcorn_branch
echo "done!"

echo -n "activating popcorn parent theme" >&3
cd /var/www
$wp theme activate popcorn

echo -n "activating $theme_name child theme" >&3
cd /var/www
$wp theme activate $theme_name
echo "done!" >&3

# visit the page once so that custom post types are created
lynx -dump http://localhost

# create popcorn default directory structure (only on first up)
if [ ! -f "/vagrant/www/style.css" ]; then
	echo -n "creating popcorn child theme directory structure..." >&3
	mkdir -p /vagrant/less
	mkdir -p /vagrant/www/css
	mkdir -p /vagrant/www/fonts
	mkdir -p /vagrant/www/images
	mkdir -p /vagrant/www/js/theme
	mkdir -p /vagrant/www/libs/theme/cpts
	mkdir -p /vagrant/www/lang
	echo "done!" >&3
fi

fi ## end popcorn installation



# activate theme
if [ "$wordpress_install" == "yes" ] && [ "$popcorn_install" == "no" ]; then
	echo -n "activating theme..." >&3
	cd /var/www
	$wp theme activate $theme_name
	echo "done!" >&3
fi



### mailcatcher start
if [ "$mailcatcher_install" == "yes" ]; then
echo -n "enable mod_proxy and mailcatcher vhost..." >&3
a2enmod proxy proxy_http
sed -i "s/ServerName.*/ServerName $mailcatcher_hostname /g" /etc/apache2/sites-available/mailcatcher
a2ensite mailcatcher
echo "done!" >&3

echo -n "creating mailcather boot script..." >&3
cat > /etc/init.d/mailcatcher << EOF
#!/bin/bash

PID_FILE=/var/run/mailcatcher.pid
NAME=mailcatcher
PROG="/usr/bin/env mailcatcher"
USER=mailcatcher
GROUP=mailcatcher

start() {
	echo -n "Starting MailCatcher"
	if start-stop-daemon --stop --quiet --pidfile \$PID_FILE --signal 0
	then
		echo " already running."
		exit
	fi
	start-stop-daemon \
		--start \
		--pidfile \$PID_FILE \
		--make-pidfile \
		--background \
		--exec \$PROG \
		--user \$USER \
		--group \$GROUP \
		--chuid \$USER \
		-- \
		--foreground \
		--http-ip=0.0.0.0 \
		--http-port=1080 \
		--smtp-port=1025
	echo "."
	return \$?
}

stop() {
	echo -n "Stopping MailCatcher"
	start-stop-daemon \
		--stop \
		--oknodo \
		--pidfile \$PID_FILE
	echo "."
	return \$?
}

restart() {
	stop
	start
}

case "\$1" in
	start)
		start
		;;
	stop)
		stop
		;;
	restart)
		restart
		;;
	*)
		echo "Usage: \$0 {start|stop|restart}"
		exit 1
		;;
esac
EOF
chmod +x /etc/init.d/mailcatcher
echo "done!" >&3

echo -n "enabling mailcatcher service..." >&3
chmod +x /etc/init.d/mailcatcher
update-rc.d mailcatcher defaults
echo "done!" >&3

echo -n "starting mailcatcher..." >&3
service mailcatcher start
echo "done!" >&3

fi
### mailcatcher end



# create wordpress style.css and index.php (just because I'm a nice guy)
# if we're installing wordpress, we're probably making a wordpress theme
if [ "$wordpress_install" == "yes" ] && [ ! -f "/vagrant/www/style.css" ]; then

# check if we're making popcorn ;)
if [ "$popcorn_install" == "yes" ]; then
	template="Template: popcorn"
	textdomain="Text Domain: popcorn-child"
fi

cat > /vagrant/www/style.css << EOF
/*
Theme Name: $project_title
Description: $theme_description
Author: $theme_author
Author URI: $theme_author_uri
Version: 1.0
$template
$textdomain
*/
EOF
fi

# this is where you'd create base files when creating a new wordpress theme (header, footer etc)
if [ ! -f "/vagrant/www/index.php" ] && [ "$wordpress_install" == "no" ]; then
	echo -n "saying hello to the world..." >&3
	echo "Hello World!" > /var/www/index.php
	echo "done!" >&3
fi



# install bootstrap if asked to
if [ "$bootstrap_install" == "yes" ] && [ ! -f "/vagrant/www/css/bootstrap.min.css" ]; then
	echo -n "installing boostrap..." >&3
	cd /tmp
	git clone https://github.com/twbs/bootstrap.git
	cp -r /tmp/bootstrap/dist/* /vagrant/www/
	rm -rf /tmp/bootstrap
	echo "done!" >&3
fi



# install font awesome if asked to
if [ "$fontawesome_install" == "yes" ] && [ ! -f "/vagrant/www/fonts/fontawesome-webfont.ttf" ]; then
	echo -n "installing font awesome..." >&3
	cd  /vagrant
	npm install --silent -g component
	component install FortAwesome/Font-Awesome
	cp -r /vagrant/components/fortawesome-font-awesome/css/ /vagrant/components/fortawesome-font-awesome/fonts/ /var/www/
	rm -rf /vagrant/components/fortawesome-font-awesome/
	echo "done!" >&3
fi



# import post xml data including images
if [ "$wordpress_install" == "yes" ]; then
	if ls /vagrant/import/*.xml &> /dev/null; then
		for file in /vagrant/import/*.xml; do
			echo -n "importing $file..." >&3
			cd /var/www
			$wp import $file --authors=create
			chown -R www-data:www-data /var/www/wp-content/uploads/
			echo "done!" >&3
		done
	fi
fi



# import database dumps
if [ "$db_create" == "yes" ]; then
	if ls /vagrant/import/*.sql &> /dev/null; then
		set +e
		echo "SHOW DATABASES" | mysql -u$db_user -p$db_pass | grep $db_name
		if [ "$?" -eq 0 ]; then
			echo "DROP DATABASE \`$db_name\`" | mysql -u$db_user -p$db_pass
			echo "CREATE DATABASE \`$db_name\`" | mysql -u$db_user -p$db_pass
		else
			echo "CREATE DATABASE \`$db_name\`" | mysql -u$db_user -p$db_pass
		fi
		set -e
		for file in /vagrant/import/*.sql; do
			echo -n "installing db dump from $file..." >&3
			mysql -u$db_user -p$db_pass $db_name < $file
		done

		if [ "$wordpress_install" == "yes" ]; then
			echo -n "resetting blog title from settings.yml..." >&3
			cd /var/www
			$wp option update blogname "240t89usgopdijl2k3jl5kj2346t09u"
			$wp option update blogname "$wordpress_blogname"
			echo "done!" >&3
		fi
	fi

	if [ "$wordpress_install" == "yes" ]; then
		set +e
		cd /var/www
		$wp user list --field=user_login | grep $wordpress_admin_user > /dev/null
		if [ "$?" -eq 1 ]; then
			$wp user create $wordpress_admin_user $wordpress_admin_email --role=administrator --user_pass=$wordpress_admin_password
		else
			$wp user update $wordpress_admin_user --user_pass=$wordpress_admin_password --user_email=$wordpress_admin_email
		fi
		set -e
	fi

fi


# install dummydata after db import
if [ "$wordpress_install" == "yes" ]; then
	# import woocommerce dummy data
	if [ "$woocommerce_dummydata" == "yes" ]; then
		cd /var/www
		echo -n "making sure wordpress-importer is installed and activated..." >&3
		$wp plugin install wordpress-importer --activate
		echo "done!" >&3

		echo -n "importing woocommerce dummy data..." >&3
		$wp import /var/www/wp-content/plugins/woocommerce/dummy-data/dummy-data.xml --authors=create
		echo "done!" >&3
	fi
fi


# run theme specific shell scripts from /import
if ls /vagrant/import/*.sh &> /dev/null; then
	echo -n "checking and running import scripts..." >&3
	for file in /vagrant/import/*.sh; do
		bash $file
	done
	echo "done!" >&3
fi



# activate network plugins
if [ "$wordpress_install" == "yes" ]; then
	echo -n "activating network plugins..." >&3
	cd /var/www
	for plugin in $wordpress_plugins_network_activate; do
		$wp plugin activate $plugin --network
		echo -n "$plugin..." >&3
	done
	echo "done!" >&3
fi



# restart apache
echo -n "restarting apache..." >&3
service apache2 restart
echo "done!" >&3


# install extra packages
echo -n "installing extra packages..." >&3
if [[ -n "$box_extra_packages" ]]; then
	for package in "$box_extra_packages"; do
		apt-get install -y $package
	done
fi

echo "all done!" >&3
