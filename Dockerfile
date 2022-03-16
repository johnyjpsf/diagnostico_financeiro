FROM nginx

RUN apt-get update
RUN apt-get install -y python3-pip python3-dev nano

WORKDIR /app

COPY ./app/requirements.txt /
COPY ./app.conf /etc/nginx/sites-available/app
RUN mkdir -p /etc/nginx/sites-enabled/
RUN ln -s /etc/nginx/sites-available/app /etc/nginx/sites-enabled/

RUN pip install --no-cache-dir -r /requirements.txt
