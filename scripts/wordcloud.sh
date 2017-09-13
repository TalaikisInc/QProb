#!/bin/bash

export LD_LIBRARY_PATH=/usr/local/anaconda/lib:$LD_LIBRARY_PATH

for PROJECT in bsnssnws entreprnrnws parameterless qprob realestenews stckmrkt webdnl
do
        cd /home/$PROJECT
        source /usr/local/anaconda/bin/activate $PROJECT
        /usr/local/anaconda/envs/$PROJECT/bin/python manage.py wordcloud
        source /usr/local/anaconda/bin/deactivate
done
