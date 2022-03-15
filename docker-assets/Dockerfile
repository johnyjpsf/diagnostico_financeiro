FROM nginx

RUN apt-get update
RUN apt-get install python3-pip python3-dev

# VOLUME app /usr/share/nginx/html
WORKDIR /usr/share/nginx/html

COPY docker-assets/app /etc/nginx/sites-available/app
RUN ln -s /etc/nginx/sites-available/app /etc/nginx/sites-enabled/
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
RUN gunicorn --workers 3 --bind unix:/usr/share/nginx/html/app.sock -m 777 wsgi:app
