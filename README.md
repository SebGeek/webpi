# Create microSD card with raspi-image
* Choose Raspbian 32b with desktop
* login pi / pwd raspberry (by default)
```
sudo raspi-config
    French board
    enable SSH
    timezone Paris
```
* Activate Wifi DHCP
```
sudo nano /etc/network/interfaces
<<
auto lo
iface lo inet loopback

iface eth0 inet manual

allow-hotplug wlan0
auto wlan0
iface wlan0 inet dhcp
wpa-ssid *****
wpa-psk *****
>>
sudo reboot (sudo ifdown wlan0 / sudo ifup wlan0 ne marche pas la toute première fois)
```
* Update
```
sudo apt-get update
sudo apt-get upgrade
```
## Connection avec SSH par clef
* il faut copier la clef publique du client sur le raspberry
* Auparavant sur le client il faut générer un couple clef privée/publique (avec Putty)
* La clef privée reste sur le PC client
* La clef publique doit être ajoutée dans le fichier authorized_keys du raspberry
```
cd ~
mkdir -p .ssh
chmod 700 .ssh
nano .ssh/authorized_keys
```
y coller la clef publique précédée du texte ssh-rsa: <<ssh-rsa AAAAB...pQ==>>

* To avoid slow SSH connection, disable the SSH function: reverse DNS lookup of the client's connecting hostname for security reasons
```
sudo nano /etc/ssh/sshd_config
Set: UseDNS no
```
## SAMBA (partage répertoire Windows)
```
sudo apt-get install samba samba-common-bin

sudo nano /etc/samba/smb.conf
<<
[pi]
comment = Sharing pi home directory
path = /home/pi
browseable = yes
writeable = yes
printable = no
valid users = pi
>>

sudo smbpasswd -a pi
   password ****

sudo systemctl restart smbd.service
```
## Clone GIT repository from GitHub
```
sudo apt-get install git
cd ~/partage
git clone https://github.com/SebGeek/teleinfo.git
git remote set-url origin git+ssh://git@github.com/SebGeek/teleinfo.git
```
* Need to put SSH key in Github in order to avoid a username/password connection
    * Generate an SSH keys pair on raspberry pi:
    ```
    cd ~
    ssh-keygen -t rsa
    ```
    * In Web GitHub repository, go to settings and click 'add SSH key'.
    Copy the contents of ~/.ssh/id_rsa.pub into the field labeled 'Key'.
    
    * tell the Raspberry to use SSH connection:
    ```
    git remote set-url origin git@github.com:SebGeek/teleinfo.git
    ```
## Pour éviter les problèmes de corruption de la carte SD
* suppression du swap sur la carte SD
```
sudo apt-get remove dphys-swapfile
sudo apt-get autoremove
sudo rm -f /var/swap
```
* Utilisation de tmpfs
```
sudo nano /etc/fstab
<<
tmpfs    /tmp    tmpfs    defaults,noatime,nosuid,size=10m    0 0
tmpfs    /var/tmp    tmpfs    defaults,noatime,nosuid,size=10m    0 0
tmpfs    /var/log    tmpfs    defaults,noatime,nosuid,mode=0755,size=10m    0 0
>>
```
# Activer liaison série /dev/ttyAMA0
```
- sudo raspi-config
    disable serial login
- sudo nano /boot/cmdline.txt
    dwc_otg.lpm_enable=0 console=tty1 root=/dev/mmcblk0p2 rootfstype=ext4 elevator=deadline fsck.repair=yes rootwait
- sudo nano /boot/config.txt
    enable_uart=1
    dtoverlay=pi3-disable-bt
- sudo systemctl disable bluetooth.service
- sudo nano /etc/rc.local
    Add in the file just before "exit 0":
    stty -F /dev/ttyAMA0 1200 sane evenp parenb cs7 -crtscts
    To configure the serial link to 1200 bauds, data 7 bits, 1 even bit, 1 stop bit
```
* Add rights to open serial link from user pi
```
sudo usermod -a -G dialout pi
```
## AUTOMATIC start-up of teleinfo logger (after Raspberry start-up)
DO NOT EDIT /etc/rc.local to start python script because user is root
USE crontab:
```
crontab -e
@reboot /usr/bin/python3 /home/pi/partage/teleinfo/logger/Teleinfo_Logger.py -o /home/pi/partage/teleinfo/log/log.csv &
```
# Django
Web server (LAMP server on port 80) -> gunicorn (WSGI server) -> Django (on port 8000)

https://mikesmithers.wordpress.com/2017/02/21/configuring-django-with-apache-on-a-raspberry-pi/

* Install virtualenv to run django
```
pip3 install virtualenv
```
* Create virtual environment
```
virtualenv ~/webpienv
```
* Activate virtual environment: now python default interpreter is python3
```
source ~/webpienv/bin/activate

To deactivate type: deactivate
```
* Install Django
```
pip3 install django
```
* Configure path
```
nano .bashrc
	export PATH=$PATH:/home/pi/.local/bin
```
* Create Django project: webpi
```
django-admin startproject webpi
```
* Create Django application: ledstrip
```
python manage.py startapp ledstrip
```
* Configure Django project
```
nano ~/webpi/settings.py
	INSTALLED_APPS = (
		'django.contrib.auth',
		'django.contrib.contenttypes',
		'django.contrib.sessions',
		'django.contrib.sites',
		'django.contrib.messages',
		'django.contrib.staticfiles',
		'django.contrib.admin',
		'webpi',
		'ledstrip',
	)

	Update:
		ALLOWED_HOSTS = ["192.168.0.25", "raspberrypi"]

python manage.py makemigrations
python manage.py migrate
```
* Run server in development mode
```
source ~/webpienv/bin/activate
python manage.py runserver 192.168.0.25:8000
```
Browse http://192.168.0.25:8000/
* Installing Apache
```
deactivate
sudo apt-get install apache2 -y
sudo apt-get install apache2-dev -y
sudo apt-get install libapache2-mod-wsgi-py3
```
Browse http://192.168.0.25
* Configuring Apache to serve Django Pages using WSGI
```
sudo nano /etc/apache2/sites-available/000-default.conf
	Add some information at the end of the file (link to webpi):
		
<VirtualHost *:80>
    # The ServerName directive sets the request scheme, hostname and port that
    # the server uses to identify itself. This is used when creating
    # redirection URLs. In the context of virtual hosts, the ServerName
    # specifies what hostname must appear in the request's Host: header to
    # match this virtual host. For the default virtual host (this file) this
    # value is not decisive as it is used as a last resort host regardless.
    # However, you must set it for any further virtual host explicitly.
    ServerName 127.0.0.1
  
    ServerAdmin webmaster@localhost
    DocumentRoot /var/www/html
  
    # Available loglevels: trace8, ..., trace1, debug, info, notice, warn,
    # error, crit, alert, emerg.
    # It is also possible to configure the loglevel for particular
    # modules, e.g.
    #LogLevel info ssl:warn
  
    ErrorLog ${APACHE_LOG_DIR}/error.log
    CustomLog ${APACHE_LOG_DIR}/access.log combined
  
    # For most configuration files from conf-available/, which are
    # enabled or disabled at a global level, it is possible to
    # include a line for only one particular virtual host. For example the
    # following line enables the CGI configuration for this host only
    # after it has been globally disabled with "a2disconf".
    #Include conf-available/serve-cgi-bin.conf

    Alias /static /home/pi/webpi/static
    <Directory /home/pi/webpi/static>
            Require all granted
    </Directory>

    <Directory /home/pi/webpi/webpi>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>
  
    WSGIDaemonProcess webpi python-path=/home/pi/webpi python-home=/home/pi/webpienv
    WSGIProcessGroup webpi
    WSGIScriptAlias / /home/pi/webpi/webpi/wsgi.py
</VirtualHost>
```
* Add a line containing ServerName 127.0.0.1 to the end of the file
```
sudo nano /etc/apache2/apache2.conf

  # vim: syntax=apache ts=4 sw=4 sts=4 sr noet
  ServerName 127.0.0.1
```
* Granting ownership of db.sqlite3 file and its parent directory (thereby write access also) to the user using chown
```
chmod g+w db.sqlite3
sudo chown :www-data db.sqlite3
chmod g+w ~
sudo chown :www-data ~
chmod g+w ~/webpi
sudo chown :www-data ~/webpi
chmod g+w ~/webpi/webpi
sudo chown :www-data ~/webpi/webpi
```
* Restart server now accessible on normal port 80
```
sudo systemctl restart apache2

check for errors:
  cat /var/log/apache2/error.log

check syntax of configuration files:
  apache2ctl -t
```
Browse http://raspberrypi/
* Add permission to www-data to access SPI bus
```
sudo nano /etc/group
  spi:x:999:pi,www-data
  i2c:x:998:pi,www-data
```
* Besoin d'une première requete pour démarrer l'appli ledstrip
USE crontab:
```
crontab -e
@reboot sleep 30 && curl http://127.0.0.1
```
=> SSE

# Common commands
```
sudo systemctl restart apache2

source ~/webpienv/bin/activate
python manage.py runserver 192.168.0.25:8000

sudo shutdown -h now
```