#!/bin/bash

export LD_LIBRARY_PATH=/usr/local/anaconda/lib:$LD_LIBRARY_PATH

for PROJECT in bsnssnws entreprnrnws parameterless qprob realestenews stckmrkt webdnl, celebs
do
    source /usr/local/anaconda/bin/activate $PROJECT && cd /home/$PROJECT && \
        /usr/local/anaconda/envs/$PROJECT/bin/python /home/$PROJECT/manage.py weekly

    source /usr/local/anaconda/bin/deactivate
done
