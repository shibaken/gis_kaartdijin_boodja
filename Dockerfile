# Prepare the base environment.
# NOTE: Using ubuntu:26.04 for your personal GitHub Actions test. 
# Switch back to ghcr.io/dbca-wa/docker-apps-dev:ubuntu_2604_base_python for the final PR.
FROM ubuntu:26.04 AS builder_base_gis_kaartdijin_boodja
LABEL maintainer="asi@dbca.wa.gov.au"

ENV DEBIAN_FRONTEND=noninteractive
ENV DEBUG=True
ENV TZ=Australia/Perth
ENV PRODUCTION_EMAIL=True
ENV SECRET_KEY="ThisisNotRealKey"
ENV SITE_DOMAIN='dbca.wa.gov.au'
ENV BPAY_ALLOWED=False

# UPDATE: Ubuntu 24.04+ uses DEB822 format for sources
RUN sed -i 's/archive.ubuntu.com/en.archive.ubuntu.com/g' /etc/apt/sources.list.d/ubuntu.sources

RUN apt-get clean
RUN apt-get update
RUN apt-get upgrade -y
RUN apt-get install --no-install-recommends -y curl wget git libmagic-dev gcc binutils python3 python3-setuptools python3-dev python3-pip tzdata cron gpg-agent
RUN apt-get install --no-install-recommends -y libpq-dev patch virtualenv
RUN apt-get install --no-install-recommends -y postgresql-client mtr systemd
RUN apt-get install --no-install-recommends -y vim ssh htop
RUN apt-get install --no-install-recommends -y software-properties-common 
 
RUN apt-get install --no-install-recommends -y python3-pil
RUN apt-get install --no-install-recommends -y postgis 

# Install GDAL (System libraries)
RUN apt-get install --no-install-recommends -y gdal-bin python3-gdal libgdal-dev build-essential

RUN update-ca-certificates

# UPDATE: Node.js 18 is EOL in 2026. Upgrading to Node 22 (LTS).
RUN curl -fsSL https://deb.nodesource.com/setup_22.x | bash -
RUN apt-get install -y nodejs

# Install Python libs stage
FROM builder_base_gis_kaartdijin_boodja AS python_libs_gis_kaartdijin_boodja

RUN groupadd -g 5000 oim
RUN useradd -g 5000 -u 5000 oim -s /bin/bash -d /app
RUN usermod -a -G sudo oim
RUN mkdir /app 
RUN chown -R oim.oim /app

COPY timezone /etc/timezone
ENV TZ=Australia/Perth
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Default Scripts
RUN wget https://raw.githubusercontent.com/dbca-wa/wagov_utils/main/wagov_utils/bin/default_script_installer.sh -O /tmp/default_script_installer.sh
RUN chmod 755 /tmp/default_script_installer.sh
RUN /tmp/default_script_installer.sh

COPY startup.sh /
RUN chmod 755 /startup.sh

WORKDIR /app
USER oim
RUN virtualenv /app/venv
ENV PATH=/app/venv/bin:$PATH
RUN git config --global --add safe.directory /app

# --- GDAL FIX (Ledger Style) ---
# Set paths for GDAL headers
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Pre-install specific GDAL wheel for Ubuntu 26.04 (Python 3.14)
# This prevents the "Failed to build GDAL" error.
RUN pip install --upgrade pip setuptools wheel && \
    wget -O /tmp/GDAL-3.10.1-cp314-cp314-manylinux_2_17_x86_64.manylinux2014_x86_64.whl https://github.com/girder/large_image_wheels/raw/wheelhouse/GDAL-3.10.1-cp314-cp314-manylinux_2_17_x86_64.manylinux2014_x86_64.whl && \
    pip install /tmp/GDAL-3.10.1-cp314-cp314-manylinux_2_17_x86_64.manylinux2014_x86_64.whl

COPY requirements.txt ./
# IMPORTANT: Ensure GDAL is removed or commented out in your requirements.txt
RUN pip install -r requirements.txt

# Final Stage
FROM python_libs_gis_kaartdijin_boodja

COPY --chown=oim:oim gunicorn.ini manage.py ./
RUN touch /app/.env
COPY .git ./.git
COPY --chown=oim:oim govapp ./govapp
COPY python-cron ./
RUN python manage.py collectstatic --noinput

USER root
RUN rm -rf /var/lib/{apt,dpkg,cache,log}/ /tmp/* /var/tmp/*
USER oim

EXPOSE 8080
HEALTHCHECK --interval=1m --timeout=5s --start-period=10s --retries=3 CMD ["wget", "-q", "-O", "-", "http://localhost:8080/"]
CMD ["/startup.sh"]
LABEL org.opencontainers.image.source="https://github.com/dbca-wa/gis_kaartdijin_boodja"
