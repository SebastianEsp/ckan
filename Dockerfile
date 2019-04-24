# See CKAN docs on installation from Docker Compose on usage
FROM debian:jessie
MAINTAINER Open Knowledge

# Install required system packages
RUN apt-get -q -y update \
    && DEBIAN_FRONTEND=noninteractive apt-get -q -y upgrade \
    && apt-get -q -y install \
        python-dev \
        python-pip \
        python-virtualenv \
        python-wheel \
        libpq-dev \
        libxml2-dev \
        libxslt-dev \
        libgeos-dev \
        libssl-dev \
        libffi-dev \
        postgresql-client \
        build-essential \
        git-core \
        vim \
        wget \
        dos2unix \
        supervisor \
        cron \
    && apt-get -q clean \
    && rm -rf /var/lib/apt/lists/*

# Define environment variables
ENV CKAN_HOME /usr/lib/ckan
ENV CKAN_VENV $CKAN_HOME/venv
ENV CKAN_CONFIG /etc/ckan
ENV CKAN_STORAGE_PATH=/var/lib/ckan

# Build-time variables specified by docker-compose.yml / .env
ARG CKAN_SITE_URL

# Create ckan user
RUN useradd -r -u 900 -m -c "ckan account" -d $CKAN_HOME -s /bin/false ckan

# Setup virtual environment for CKAN
RUN mkdir -p $CKAN_VENV $CKAN_CONFIG $CKAN_STORAGE_PATH && \
    virtualenv $CKAN_VENV && \
    ln -s $CKAN_VENV/bin/pip /usr/local/bin/ckan-pip &&\
    ln -s $CKAN_VENV/bin/paster /usr/local/bin/ckan-paster

# Setup CKAN
ADD . $CKAN_VENV/src/ckan/
RUN ckan-pip install -U pip && \
    ckan-pip install --upgrade --no-cache-dir -r $CKAN_VENV/src/ckan/requirement-setuptools.txt && \
    ckan-pip install --upgrade --no-cache-dir -r $CKAN_VENV/src/ckan/requirements.txt && \
    ckan-pip install -e $CKAN_VENV/src/ckan/ && \
    ln -s $CKAN_VENV/src/ckan/ckan/config/who.ini $CKAN_CONFIG/who.ini && \
    cp -v $CKAN_VENV/src/ckan/contrib/docker/ckan-entrypoint.sh /ckan-entrypoint.sh && \
    chmod +x /ckan-entrypoint.sh && \
    chown -R ckan:ckan $CKAN_HOME $CKAN_VENV $CKAN_CONFIG $CKAN_STORAGE_PATH && \
    ckan-pip install -e git+https://github.com/ckan/ckanext-harvest.git#egg=ckanext-harvest && \
    ckan-pip install --upgrade --no-cache-dir -r $CKAN_VENV/src/ckanext-harvest/pip-requirements.txt && \
    ckan-pip install -e git+https://github.com/ckan/ckanext-spatial.git#egg=ckanext-spatial && \
    ckan-pip install -r $CKAN_VENV/src/ckanext-spatial/pip-requirements.txt && \
    ckan-pip install -e git+https://github.com/ckan/ckanext-dcat.git#egg=ckanext-dcat && \
    ckan-pip install --upgrade --no-cache-dir -r $CKAN_VENV/src/ckanext-dcat/requirements.txt && \
    ckan-pip install ckanext-geoview && \
    ckan-pip install -e git+https://github.com/geosolutions-it/ckanext-geonetwork.git#egg=ckanext-geonetwork && \
    ckan-pip install -e git+https://github.com/ckan/ckanext-pages.git#egg=ckanext-pages && \
    ckan-pip install lxml && \
    ckan-pip install OWSLib==0.9.1 && \
    ckan-pip install -e git+https://github.com/ckan/ckanext-viewhelpers.git#egg=ckanext-viewhelpers && \
    ckan-pip install -e git+https://github.com/ckan/ckanext-basiccharts.git#egg=ckanext-basiccharts && \
    ckan-pip install ckanapi && \
    dos2unix /ckan-entrypoint.sh && \
    cp -v $CKAN_VENV/src/ckan/supervisor/ckan_harvesting.conf /etc/supervisor/conf.d/ckan_harvesting.conf && \
    ls /etc/supervisor/conf.d/ && \
    cp -v $CKAN_VENV/src/ckan/supervisor/crontab.txt /crontab.txt && \
    chmod +x /crontab.txt

RUN mkdir -p /var/lib/ckan/storage/uploads/group

COPY ./import-themes-and-orgs.py $CKAN_VENV/src
COPY ./theme-img/ /var/lib/ckan/storage/uploads/group
COPY ./pages-header.html /src/ckanext-pages/ckanext/pages/themes/templates_main/header.html
COPY ./ckanext-digstdk/ckanext/digstdk/templates/ckanext/stats/index.html $CKAN_VENV/src/ckan/ckanext/stats/templates/ckanext/stats/index.html
COPY ./ckanext-dcat $CKAN_VENV/src/ckanext-dcat
COPY ./ckanext-digstdk $CKAN_VENV/src/ckanext-digstdk

WORKDIR $CKAN_VENV/src/ckanext-digstdk
RUN python setup.py develop

ENTRYPOINT ["/ckan-entrypoint.sh"]

WORKDIR $CKAN_VENV/src/ckan

USER ckan
EXPOSE 5000

VOLUME [ "/var/lib/ckan" ]
VOLUME [ "/usr/lib/ckan" ]
VOLUME [ "/etc/ckan" ]

CMD ["ckan-paster","serve","/etc/ckan/production.ini"]
