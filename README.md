# Create microSD card with raspi-image
* Choose Raspbian 32b with desktop
* login pi / pwd raspberry (by default)
```
sudo raspi-config
    French board
    enable SSH
    timezone Paris
```
* Activate wifi DHCP
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
* Need to put SSH key in Github in order to avoid username/password connection
    * Generate a SSH keys pair on raspberry pi:
    ```
    cd ~
    ssh-keygen -t rsa
    ```
    * In Web GitHub repository, go to settings and click 'add SSH key'.
    Copy the contents of ~/.ssh/id_rsa.pub into the field labeled 'Key'.
    
    * tell on raspberry to use SH connection:
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
## AUTOMATIC start-up of teleinfo logger (after raspberry start-up)
DO NOT EDIT /etc/rc.local to start python script because user is root
USE crontab:
```
crontab -e
@reboot /usr/bin/python2.7 /home/pi/partage/teleinfo/logger/Teleinfo_Logger.py -o /home/pi/partage/teleinfo/log/log.csv &
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
	
	
	
Create Django application: ledstrip
	python manage.py startapp ledstrip

Configure Django project
	nano ~/webpi/settings.py
		Add application:
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
			ALLOWED_HOSTS = ["192.168.0.19", "raspberrypi"]
		
		Add at the end of the file:
			STATIC_ROOT = os.path.join(BASE_DIR, "static/")

	python manage.py makemigrations
	python manage.py migrate

Fill application
	nano ~/webpi/urls.py
	nano ~/ledstrip/views.py

Create a superuser
	python manage.py createsuperuser
		pi / Unchained69!
	python manage.py collectstatic

Run server in development mode
	source ~/webpienv/bin/activate
	python manage.py runserver 192.168.0.19:8000
	Browse http://192.168.0.19:8000/
	Browse http://192.168.0.19:8000/admin

Installing Apache
	deactivate
	sudo apt-get install apache2 -y
	Browse http://192.168.0.19
	sudo apt-get install apache2-dev -y
	sudo apt-get install libapache2-mod-wsgi-py3

Configuring Apache to serve Django Pages using WSGI
	sudo nano /etc/apache2/sites-available/000-default.conf
	Add:
	Alias /static /home/pi/static
		<Directory /home/pi/static> 
			Require all granted
		</Directory>
	  
		<Directory /home/pi/webpi>
			<Files wsgi.py>
				Require all granted
			</Files>
		</Directory>
	  
		WSGIDaemonProcess webpi python-path=/home/pi python-home=/home/pi/webpienv
		WSGIProcessGroup webpi
		WSGIScriptAlias / /home/pi/webpi/wsgi.py

	Granting ownership of db.sqlite3 file and its parent directory (thereby write access also) to the user using chown
	chmod g+w ~/db.sqlite3
	sudo chown :www-data ~/db.sqlite3
	chmod g+w ~
	sudo chown :www-data ~
	chmod g+w ~/webpi
	sudo chown :www-data ~/webpi


Restart server now accessible on normal port 80
	sudo apache2ctl restart
	cat /var/log/apache2/error.log
	Browse http://raspberrypi/
	Browse http://raspberrypi/admin


apache2ctl -S

read error
	apache2ctl -t

source ~/webpienv/bin/activate
python manage.py runserver 192.168.0.19:8000
sudo shutdown -h now

Add permission to www-data to access SPI bus
  sudo nano /etc/group
      spi:x:999:pi,www-data
      i2c:x:998:pi,www-data

autotart apache
	sudo systemctl enable --now apache2
	ServerName localhost
	
=> besoin d'une première requete pour démarrer le serveur !!!!!!!!!!!
=> cela démarre l'appli ! je veux la démarrer tout le temps