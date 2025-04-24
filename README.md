# How to dev locally:
1) `python3 -m venv env` or `python -m venv env`
2) source env/bin/activate  # On Windows use `env\Scripts\activate`
3) `pip install -r requirements.txt`
4) python manage.py migrate
5) python manage.py runserver


# How to deploy Django:

first make sure that settings.py has `DEBUG = False` and `ALLOWED_HOSTS = ['*']`
1) ssh to the server
2) clone this project to folder forwarder-api
3) `cd forwarder-api`
4) ```
   sudo apt update
   sudo apt upgrade
   sudo apt install python3-pip
   pip install --upgrade pip 
   ```
5) `pip install virtualenv`
6) `virtualenv myenv`
7) `source myenv/bin/activate`
8) `pip install -r requirements.txt`
9) `python manage.py migrate`
10) create admin user `python manage.py createsuperuser`
11) `screen -dmS forwarder_api python manage.py runserver 0.0.0.0:8000`


# How to deploy Nginx:

1) create folder nginx in root
2) create file nginx.conf in folder nginx
3) paste this code to nginx.conf
```
server {
    listen 80;

    location / {
        proxy_pass http://172.17.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```
4) install docker on server `sudo apt install docker.io`
5) `docker run --name mynginx1 -p 80:80 -v $(pwd)/my_nginx.conf:/etc/nginx/conf.d/default.conf -d nginx`

NOTE: right now the nginx is running in docker container with ssl config and let's encrypt certificate 
and you need to do this for CORS and other errors, also it's safer

# How to deploy Telegram bot:

1) ssh to the server
2) cd to the project folder
3) create config.yml file using sample_config.yml
4) `screen -dmS forwarder_bot python manage.py run_telethon`

**DO NOT FORGET when deploying:**
1) change SECRET_KEY in settings.py for Django
2) set CORS_ORIGIN_WHITELIST in settings.py for Django the url where the requests are coming from


# Flow for updates

**Front-end**
1) build front-end with .env file having url of the api
2) deploy to s3 bucket
3) invalidate cache in cloudfront

**Back-end**
1) `cd forwarder-api/`
2) `source myenv/bin/activate`
3) `git pull`
4) `python manage.py migrate` (optional)
5) `screen -ls`
6) `screen kill forwarder_botPID`
7) `screen -dmS forwarder_bot python manage.py run_telethon`
8) `screen kill forwarder_apiPID`
9) `screen -dmS forwarder_api python manage.py runserver 0.0.0.0:8000` 
10) `screen kill forwarder_scraperPID`
11) `screen -dmS forwarder_scraper python manage.py run_scraper`
12) `screen kill forwarder_relayPID`
13) `screen -dmS forwarder_relay python manage.py run_relay`
14) `screen kill delegatorPID`
15) `cd /delegation_app`
16) `screen -dmS delegator python delegation.py`
17) test the bot
18) test the api

# How to update nginx cert in the server
1) ssh to the server
2) `docker ps` to get the container id of nginx
3) `docker kill {nginxId}`
4) `certbot certonly --force-renew -d {API_URL}`
5) go to nginx folder `docker-compose up -d`
