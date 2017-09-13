# MANUAL DEPLOYMENT

## 1. Install requirements

Server software requirements:

* Python (under user www-data)

```text
sudo chown -R www-data:www-data /var/www
sudo chown -R www-data:www-data /<project_folder>
su -s /bin/bash www-data
wget https://repo.continuum.io/archive/Anaconda3-4.3.1-Linux-x86_64.sh
bash Anaconda3-4.3.1-Linux-x86_64.sh 
source /var/www/.bashrc
conda update --all
```

* JavaJDK
* Elastic Search

```text
sudo apt install default-jdk
sudo apt install curl
curl -O https://download.elastic.co/elasticsearch/release/org/elasticsearch/distribution/deb/elasticsearch/2.4.1/elasticsearch-2.4.1.deb
sudo dpkg -i elasticsearch-2.4.1.deb
sudo update-rc.d elasticsearch defaults 95 10
sudo /etc/init.d/elasticsearch start
```

* Memcached

```text
sudo apt install memcached
```
* Nginx

```text
sudo apt install nginx
```

* Mysql

```text
sudo apt install mysql-server
sudo mysql_secure_installation
```

* Other

```text
sudo apt install gcc libmysqlclient-dev
```

* Project

```text
cd <project_folder>
pip install -r requirements.txt
```

## 2. Create (MySQL) db:

```text
CREATE DATABASE <db_name> CHARACTER SET utf8 COLLATE utf8_general_ci;
CREATE USER '<user>'@'<host>' IDENTIFIED BY '<password>';
GRANT ALL ON <db_name>.* to '<user>'@'<host>';
FLUSH PRIVILEGES;
```

## 3. Configure Nginx/ uWSGI/ SSL.

* Nginx

```text
ln /home/<project_folder>/nginx.conf /etc/nginx/sites-enabled/
service nginx reload
```

* uWSGI

```text
mkdir /var/www/uwsgi
ln /home/<project_folder>/uwsgi.ini /var/www/uwsgi
```

* uWSGI Emperor service

Create the file:

```text
sudo touch /etc/systemd/system/uwsgi.service
sudo nano /etc/systemd/system/uwsgi.service
```

... with following contents:

```text
[Unit]
Description=uwSGI

[Service]
WorkingDirectory=/home/<project>
User=root
Group=root
Type=forking
ExecStart=/bin/bash /home/<project>/uwsgi.sh

[Install]
WantedBy=multi-user.target```

Ant then start the service, check the status:

```text
systemctl start uwsgi.service
systemctl status uwsgi.service
```

* SSL

```text
cd /usr/local/sbin
sudo wget https://dl.eff.org/certbot-auto
sudo chmod a+x /usr/local/sbin/certbot-auto
./certbot-auto certonly -a webroot --agree-tos --renew-by-default --webroot-path=/home/<project_folder> -d <domain>
./certbot-auto certonly -a webroot --agree-tos --renew-by-default --webroot-path=/home/<project_folder> -d www.<domain>
```

* Diffie–Hellman key for SSL.

```text
sudo openssl dhparam -out /etc/ssl/certs/dhparam.pem 4096
```

## 4. Create Facebook, Twitter apps and pages. Create FeedBurner.

## 5. Make logo named {LOGO_HANDLE} (define this in /qprob/settings.py)

## 6. Make appropriate changes inside app settings (/qprob/settings.py)

## 7. Migrate, etc.

```text
cd /<project_folder>
python manage.pu makemigrations
python manage.py migrate
python manage.py createsuperuser
```

## 8. Put some sources into Sources via admin panel.

## 9. Schedule parser cronjobs.

```text
1 1 * * * python /home/<project_folder>/manage.py parser
40 1 * * * python /home/<project_folder>/manage.py twitter
50 1 * * * python /home/<project_folder>/manage.py update_index
```

## 10. Review book categories to enable what to show on the page.

## 11. Configure some additional security.

* Firewall.

```text
sudo apt install ufw
ufw allow https
ufw allow http
ufw enable
```
