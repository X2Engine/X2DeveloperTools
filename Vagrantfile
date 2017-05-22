# -*- mode: ruby -*-
# vi: set ft=ruby :

# All Vagrant configuration is done below. The "2" in Vagrant.configure
# configures the configuration version (we support older styles for
# backwards compatibility). Please don't change it unless you know what
# you're doing.
Vagrant.configure(2) do |config|
  # The most common configuration options are documented and commented below.
  # For a complete reference, please see the online documentation at
  # https://docs.vagrantup.com.

  # Every Vagrant development environment requires a box. You can search for
  # boxes at https://atlas.hashicorp.com/search.
  config.vm.box = "debian/jessie64"

  # Disable automatic box update checking. If you disable this, then
  # boxes will only be checked for updates when the user runs
  # `vagrant box outdated`. This is not recommended.
  # config.vm.box_check_update = false

  # Create a forwarded port mapping which allows access to a specific port
  # within the machine from a port on the host machine. In the example below,
  # accessing "localhost:8080" will access port 80 on the guest machine.
  config.vm.network "forwarded_port", guest: 80, host: 8080

  # Create a private network, which allows host-only access to the machine
  # using a specific IP.
  # config.vm.network "private_network", ip: "192.168.33.10"

  # Create a public network, which generally matched to bridged network.
  # Bridged networks make the machine appear as another physical device on
  # your network.
  # config.vm.network "public_network"

  # Share an additional folder to the guest VM. The first argument is
  # the path on the host to the actual folder. The second argument is
  # the path on the guest to mount the folder. And the optional third
  # argument is a set of non-required options.
  if not Dir.exists?("X2CRM")
      puts "Please clone the X2CRM repo before proceeding!"
      exit
  end
  Dir.mkdir("workdir") if not Dir.exists?("workdir")
  config.vm.synced_folder "workdir", "/var/www/html", owner: 'www-data'

  # Provider-specific configuration so you can fine-tune various
  # backing providers for Vagrant. These expose provider-specific options.
  # Example for VirtualBox:
  #
  config.vm.provider "virtualbox" do |vb|
  #   # Display the VirtualBox GUI when booting the machine
  #   vb.gui = true
  #
  #   # Customize the amount of memory on the VM:
      vb.memory = "1024"
  end
  #
  # View the documentation for the provider you are using for more
  # information on available options.

  # Define a Vagrant Push strategy for pushing to Atlas. Other push strategies
  # such as FTP and Heroku are also available. See the documentation at
  # https://docs.vagrantup.com/v2/push/atlas.html for more information.
  # config.push.define "atlas" do |push|
  #   push.app = "YOUR_ATLAS_USERNAME/YOUR_APPLICATION_NAME"
  # end

  # Enable provisioning with a shell script. Additional provisioners such as
  # Puppet, Chef, Ansible, Salt, and Docker are also available. Please see the
  # documentation for more information about their specific syntax and use.
  config.vm.provision "shell", inline: <<-SHELL
    # Install dependencies and set up database
    sudo apt-get update
    sudo DEBIAN_FRONTEND=noninteractive apt-get install -y git rsync apache2 mysql-server php5 php5-mysql php5-gd php5-curl php5-mcrypt phpunit phpunit-selenium xvfb openjdk-7-jre chromium
    sudo ln -s /usr/bin/chromium /usr/local/bin/google-chrome # Fake it for the default Selenium config
    mysqladmin -u root password x2crm
    mysqladmin -u root -px2crm create x2crm
    mysql -u root -px2crm -e 'create user x2crm@localhost identified by "x2crm";'
    mysql -u root -px2crm -e 'grant all on x2crm.* to x2crm@localhost;'
    mysqladmin -u root -px2crm flush-privileges

    # Configure virtual host
    grep X2 /etc/apache2/sites-enabled/000-default.conf
    if [ $? -ne 0 ]; then
        sed -i '/DocumentRoot/ s/html/html\\/X2CRM/' /etc/apache2/sites-enabled/000-default.conf
        sudo chown www-data /var/www
        sudo service apache2 restart
    fi

    # Set up environment and aliases
    grep x2 /home/vagrant/.bashrc
    if [ $? -ne 0 ]; then
        cat >> /home/vagrant/.bashrc <<-BASHCONFIG
export DISPLAY=:22
export GITDIR="/vagrant"
export WORKINGDIR="/var/www/html"
export INSTALLEDDIR="/var/www/html"
export MYSQLUSER="x2crm"
export MYSQLPASS="x2crm"
export MYSQLDATABASE="x2crm"
export INSTALLREMOTE=0
export REMOTEUSER="username"
export REMOTESERVER="remoteserver.com"
export REMOTEWEBROOT="public_html"
alias x2util=/vagrant/x2util
alias x2test=/home/vagrant/x2test.sh
_x2testing() {
    local cur=\\${COMP_WORDS[COMP_CWORD]}
    COMPREPLY=( \\$(compgen -W "\\$(find /var/www/html/X2CRM/x2engine/protected/tests/ | sed 's|/var/www/html/X2CRM/x2engine/protected/tests/||')" -- \\$cur) )
}
complete -F _x2testing x2test
BASHCONFIG
    fi

    # Create testing script
    if [ ! -f /home/vagrant/x2test.sh ]; then
        cat >> /home/vagrant/x2test.sh <<-TESTSCRIPT
#!/bin/bash
if [ -n "\\$1" ]; then
    TEST="x2engine/protected/tests/\\${1}"
else
    TEST="x2engine/protected/tests/unit"
fi

cd /var/www/html/X2CRM
sudo -u www-data phpunit --config x2engine/protected/tests/phpunit.xml \\$TEST
cd
TESTSCRIPT
        chmod +x /home/vagrant/x2test.sh
    fi

    # Configure Selenium for functional testing
    if [ ! -f selenium-server-standalone-2.48.2.jar ]; then
        wget https://selenium-release.storage.googleapis.com/2.48/selenium-server-standalone-2.48.2.jar
    fi
    if [ ! -f /etc/init.d/selenium ]; then
        cat >> /etc/init.d/selenium <<-SELENIUMSCRIPT
#!/bin/sh
export DISPLAY=:22
su vagrant -c 'Xvfb -fp /usr/share/fonts/X11/misc/ :22 -screen 0 1024x768x16 2>&1 &'
su vagrant -c 'java -jar /home/vagrant/selenium-server-standalone-2.48.2.jar -browserSessionReuse -singlewindow &'
SELENIUMSCRIPT
        chmod +x /etc/init.d/selenium
        ln -s /etc/init.d/selenium /etc/rc2.d/S99selenium
        /etc/init.d/selenium
    fi
  SHELL
end
