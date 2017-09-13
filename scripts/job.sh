#!/bin/bash

COM=$1

for PROJECT in bsnssnws entreprnrnws parameterless qprob realestenews stckmrkt webdnl
do
        cd /home/$PROJECT
        source /usr/local/anaconda/bin/activate $PROJECT
        /usr/local/anaconda/envs/$PROJECT/bin/python manage.py $COM
        source /usr/local/anaconda/bin/deactivate $PROJECT
done
