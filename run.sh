#!/bin/bash
# for run flask app
source ~/anaconda3/etc/profile.d/conda.sh
conda activate tgweb
echo 'success activate anaconda tgweb'
echo 'ready to start tg_flask app...'
/root/anaconda3/envs/tgweb/bin/python /home/sean/flaskWeb/app.py