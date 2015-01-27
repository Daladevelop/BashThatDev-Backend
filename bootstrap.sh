#!/usr/bin/env bash

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


# run all shell scripts from /import
if ls /vagrant/import/*.sh &> /dev/null; then
	echo -n "checking and running import scripts..." >&3
	for file in /vagrant/import/*.sh; do
		bash $file
	done
	echo "done!" >&3
fi

