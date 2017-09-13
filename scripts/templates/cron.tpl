#!/bin/bash

PROJECT={0}

export LD_LIBRARY_PATH=/usr/local/anaconda/lib:$LD_LIBRARY_PATH

source /usr/local/anaconda/bin/activate $PROJECT && cd /home/$PROJECT && \
  /usr/local/anaconda/envs/$PROJECT/bin/python /home/$PROJECT/manage.py  parser

source /usr/local/anaconda/bin/deactivate
