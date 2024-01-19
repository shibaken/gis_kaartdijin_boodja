# Prepare the base environment.
FROM ubuntu:22.04 as builder_base_gis_kaartdijin_boodja
MAINTAINER asi@dbca.wa.gov.au
ENV DEBIAN_FRONTEND=noninteractive
ENV DEBUG=True
ENV TZ=Australia/Perth
ENV PRODUCTION_EMAIL=True
ENV SECRET_KEY="ThisisNotRealKey"
ENV SITE_DOMAIN='dbca.wa.gov.au'
ENV BPAY_ALLOWED=False

# Use Australian Mirrors
RUN sed 's/archive.ubuntu.com/au.archive.ubuntu.com/g' /etc/apt/sources.list > /etc/apt/sourcesau.list
RUN mv /etc/apt/sourcesau.list /etc/apt/sources.list
# Use Australian Mirrors

RUN apt-get clean
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install --no-install-recommends -y curl wget git libmagic-dev gcc binutils python3 python3-setuptools python3-dev python3-pip tzdata cron gpg-agent 
RUN apt-get install --no-install-recommends -y libpq-dev patch
RUN apt-get install --no-install-recommends -y postgresql-client mtr systemd
RUN apt-get install --no-install-recommends -y vim postgresql-client ssh htop
RUN apt-get install --no-install-recommends -y rsyslog
RUN apt-get install --no-install-recommends -y software-properties-common 
RUN add-apt-repository ppa:deadsnakes/ppa -y
RUN apt update
RUN apt-get install --no-install-recommends -y  python3.10

# Install GDAL
RUN add-apt-repository ppa:ubuntugis/ubuntugis-unstable
RUN apt update
RUN apt-get install --no-install-recommends -y gdal-bin python3-gdal

RUN update-ca-certificates
# install node 18
RUN touch install_node.sh
RUN curl -fsSL https://deb.nodesource.com/setup_18.x -o install_node.sh
RUN chmod +x install_node.sh && ./install_node.sh
RUN apt-get install -y nodejs
RUN ln -s /usr/bin/python3.10 /usr/bin/python
RUN pip install --upgrade pip
RUN wget -O /tmp/GDAL-3.8.3-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl https://github.com/girder/large_image_wheels/raw/wheelhouse/GDAL-3.8.3-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl#sha256=e2fe6cfbab02d535bc52c77cdbe1e860304347f16d30a4708dc342a231412c57
RUN pip install /tmp/GDAL-3.8.3-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
# Install Python libs using pyproject.toml and poetry.lock
FROM builder_base_gis_kaartdijin_boodja as python_libs_gis_kaartdijin_boodja

WORKDIR /app
ENV POETRY_VERSION=1.3.2
RUN curl -sSL https://install.python-poetry.org | python -
RUN ln -s /root/.local/bin/poetry /usr/bin/poetry
RUN poetry config virtualenvs.create false
COPY pyproject.toml poetry.lock ./
RUN poetry install --only main --no-interaction --no-ansi
RUN rm -rf /var/lib/{apt,dpkg,cache,log}/ /tmp/* /var/tmp/*

# Install the project (ensure that frontend projects have been built prior to this step).
FROM python_libs_gis_kaartdijin_boodja
COPY timezone /etc/timezone
ENV TZ=Australia/Perth
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

COPY cron /etc/cron.d/dockercron
COPY startup.sh /
#RUN service rsyslog start
RUN chmod 0644 /etc/cron.d/dockercron
RUN crontab /etc/cron.d/dockercron
RUN touch /var/log/cron.log
RUN service cron start
RUN chmod 755 /startup.sh
COPY gunicorn.ini manage.py ./
RUN touch /app/.env
COPY .git ./.git
COPY govapp ./govapp
RUN cd /app/govapp/frontend; npm install
RUN cd /app/govapp/frontend; npm run build
RUN python manage.py collectstatic --noinput
RUN apt-get install --no-install-recommends -y python3-pil
RUN apt-get install --no-install-recommends -y postgis 
EXPOSE 8080
HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:8080/"]
CMD ["/startup.sh"]
LABEL org.opencontainers.image.source="https://github.com/dbca-wa/gis_kaartdijin_boodja"
