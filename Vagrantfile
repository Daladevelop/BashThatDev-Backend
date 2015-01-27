# -*- mode: ruby -*-:
# vi: set ft=ruby :

# read our settings
require 'fileutils'
require 'yaml'
settings = YAML.load_file('settings.yml')

# Vagrantfile API/syntax version. Don't touch unless you know what you're doing!
VAGRANTFILE_API_VERSION = "2"

unless Vagrant.has_plugin?("vagrant-hostsupdater")
  raise "\n\nMISSING PLUGIN: vagrant-hostsupdater!\n\nInstall by running:\n\n# vagrant plugin install vagrant-hostsupdater"
end

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.box = "hashicorp/precise64"
#  config.vm.box_url = "http://images.dalnix.se/devnode1204_20140616.box"
  config.vm.network :private_network, ip: settings['box']['ip'], netmask: settings['box']['netmask']
  config.hostsupdater.aliases = [settings['box']['hostname'], settings['box']['hostalias']]
  config.hostsupdater.remove_on_suspend = true
  # config.vm.network "forwarded_port", guest: 80, host: 8080
  # config.vm.network "public_network"
  config.vm.provider "virtualbox" do |vb|
    vb.gui = settings['box']['gui']
    vb.customize ["modifyvm", :id, "--natdnsproxy1", "off"]
    vb.customize ["modifyvm", :id, "--natdnshostresolver1", "off"]
    vb.customize ["modifyvm", :id, "--memory", settings['box']['memory']]
  end
  config.vm.provision :shell, :path => "bootstrap.sh"

  if ! File.directory?('www/')
    Dir.mkdir 'www/'
  end

#  config.vm.synced_folder "www/", "/var/www"
  config.vm.synced_folder "server/", "/home/server"
end

