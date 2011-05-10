#!/bin/bash -x

sudo apt-get install python-virtualenv virtualenvwrapper python-imaging python-lxml git

source /etc/bash_completion.d/virtualenvwrapper
mkdir ~/.virtualenvs
mkvirtualenv zookeepr

# source /usr/local/bin/virtualenvwrapper.sh
# printf "\nsource /usr/local/bin/virtualenvwrapper.sh\n" >> ~/.bashrc
# printf "# workon zookeepr\n" >> ~/.bashrc

git clone git://github.com/CarlFK/zookeepr.git
cd zookeepr
pip install -r requirements.txt

cp zookeepr/config/lca_info.py.sample zookeepr/config/lca_info.py

python setup.py develop
paster make-config zookeepr config.ini
paster setup-app config.ini
paster serve --reload config.ini

