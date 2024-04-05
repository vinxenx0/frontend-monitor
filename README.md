# frontend-monitor
front-end for web-monitor

# depenencies +
libapache2-mod-wsgi-py3
sudo apt-get install apache2 apache2-dev

# first start
FileNotFoundError: [Errno 2] No such file or directory: '/opt/moonitor/frontend-monitor/.logs/app.log'
(.venv) root@ciberpunk:/opt/moonitor/frontend-monitor# mkdir .logs
(.venv) root@ciberpunk:/opt/moonitor/frontend-monitor# touch .logs/app.log

mkdir .ssl
ln -s /usr/local/psa/var/modules/letsencrypt/etc/live/_plesk_domain/* /opt/moonitor/frontend-monitor/.ssl/

pip install google textstat

curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install v21.6.0
nvm use v21.6.0
npm install -g npm@10.2.4



npm install -g pa11y


# update
pip3 list --outdated --format=freeze | grep -v '^\-e' | cut -d = -f 1 | xargs -n1 pip3 install -U 
