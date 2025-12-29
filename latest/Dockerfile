FROM python:3.11-slim-bookworm

LABEL maintainer="Thiago Haeitmann"
LABEL email="ceo@haeicore.com.br"
LABEL stack="plone6-classic-buildout"

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=America/Sao_Paulo \
    SENAITE_HOME=/home/senaite \
    SENAITE_INSTANCE_HOME=/home/senaite/senaitelims \
    SENAITE_DATA=/data

# Usuário
RUN useradd --system -m -d $SENAITE_HOME -U -u 500 senaite

# Diretórios base
RUN mkdir -p \
    $SENAITE_INSTANCE_HOME \
    $SENAITE_DATA/blobstorage \
    $SENAITE_DATA/filestorage \
    $SENAITE_DATA/cache \
    $SENAITE_DATA/log \
    $SENAITE_DATA/zeoserver

# Dependências do SO
COPY build_deps.txt run_deps.txt /

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      $(grep -vE "^\s*#" /build_deps.txt | tr "\n" " ") \
      $(grep -vE "^\s*#" /run_deps.txt | tr "\n" " ") && \
    rm -rf /var/lib/apt/lists/*

# Buildout
WORKDIR $SENAITE_INSTANCE_HOME
COPY requirements.txt buildout.cfg ./

RUN pip install --no-cache-dir -r requirements.txt && \
    buildout

# Scripts
COPY docker-initialize.py docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh && \
    chown -R senaite:senaite /home/senaite /data

VOLUME ["/data"]

EXPOSE 8080 8100

ENTRYPOINT ["/docker-entrypoint.sh"]
