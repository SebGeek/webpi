Goal:
Whilst Django has it’s own built-in “development” server for playing around with, the favoured production http server appears to be Apache.

Web server (LAMP server on port 80) -> gunicorn (WSGI server) -> Django (on port 8000)

https://mikesmithers.wordpress.com/2017/02/21/configuring-django-with-apache-on-a-raspberry-pi/

Install virtualenv to run django
	pip3 install virtualenv

Create virtual environment
	virtualenv ~/webpienv
Activate virtual environment: now python default interpreter is python3
	source ~/webpienv/bin/activate

Install Django
	pip3 install django

Configure path
	nano .bashrc
		export PATH=$PATH:/home/pi/.local/bin

Create Django project: webpi
	django-admin startproject webpi .
	
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

AH00558: apache2: Could not reliably determine the server's fully qualified domain name, using 127.0.1.1. Set the 'ServerName' directive globally to suppress this message

- mettre sur raspberry pi 3 dans un sous répertoire de /pi

=> besoin d'une première requete pour démarrer le serveur !!!!!!!!!!!

autotart apache
	sudo systemctl enable --now apache2
	ServerName localhost
	
il faut une première requete pour voir le sapin
=> cela démarre l'appli ! je veux la démarrer tout le temps