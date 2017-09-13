#!/bin/bash

SOURCES=/home/sources

if [ ! -d "$SOURCES" ]; then
    mkdir $SOURCES
fi

if [ -d "$SOURCES/QProb" ]; then
    cd $SOURCES/QProb
    git fetch --all
    git reset --hard origin/master
else
    cd $SOURCES
    git clone https://github.com/xenu256/QProb
fi

/usr/local/anaconda/bin/python /home/qprob/scripts/devops.py --nginx

for PROJECT in bsnssnws entreprnrnws parameterless qprob realestenews stckmrkt webdnl
do
        cp -R $SOURCES/QProb/. /home/$PROJECT/
        cd /home/$PROJECT
        source /usr/local/anaconda/bin/activate $PROJECT
        /usr/local/anaconda/envs/$PROJECT/bin/pip install -r requirements.txt
        /usr/local/anaconda/envs/$PROJECT/bin/python manage.py makemigrations
        /usr/local/anaconda/envs/$PROJECT/bin/python manage.py migrate
        /usr/local/anaconda/envs/$PROJECT/bin/python \
                /home/$PROJECT/scripts/devops.py --cron $PROJECT
        /usr/local/anaconda/envs/$PROJECT/bin/python \
                /home/$PROJECT/scripts/devops.py --nginx $PROJECT
        /bin/chmod +x /home/$PROJECT/cron.sh
        /bin/chmod +x /home/$PROJECT/week_cron.sh
        source /usr/local/anaconda/bin/deactivate
        chown -R www-data:www-data  /home/$PROJECT
        stop $PROJECT
        start $PROJECT
done
