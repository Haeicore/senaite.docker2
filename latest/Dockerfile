# Plone 6 + Python 3.11 em Debian estável (recomendado)
FROM python:3.11-slim-bookworm

LABEL maintainer="Thiago Haeitmann"
LABEL email="ceo@haeicore.com.br"

ENV DEBIAN_FRONTEND=noninteractive \
    TZ=America/Sao_Paulo \
    PLONE_VERSION=6.0.7 \
    SENAITE_HOME=/home/senaite \
    SENAITE_USER=senaite \
    SENAITE_DATA=/data \
    INSTANCE_DIR=/data/instance \
    HTTP_PORT=8080 \
    ADMIN_USER=admin \
    ADMIN_PASSWORD=admin

# Dependências nativas comuns pro Plone/Zope/Pillow/lxml/WeasyPrint etc.
# (Se faltar algo, adiciona aqui — mas isso já cobre 90% dos casos)
RUN apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl wget git \
      build-essential \
      libssl-dev libffi-dev \
      zlib1g-dev libjpeg62-turbo-dev libpng-dev \
      libxml2-dev libxslt1-dev \
      libpq-dev \
      locales \
    && rm -rf /var/lib/apt/lists/*

# Usuário não-root
RUN useradd --system -m -d ${SENAITE_HOME} -U -u 500 ${SENAITE_USER} \
    && mkdir -p ${SENAITE_DATA} \
    && chown -R ${SENAITE_USER}:${SENAITE_USER} ${SENAITE_HOME} ${SENAITE_DATA}

# pip sane (sem inventar moda, mas também sem deixar velho demais)
RUN python -m pip install --no-cache-dir \
  "pip==23.2" "setuptools==68.0.0" "wheel==0.40.0"

# Instala Plone 6.0.7 via pip (caminho moderno)
# Isso traz Zope/Werkzeug/Waitress/etc conforme o stack do Plone.
RUN python -m pip install --no-cache-dir "Plone==${PLONE_VERSION}"

# Entry point
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh \
    && chown ${SENAITE_USER}:${SENAITE_USER} /docker-entrypoint.sh

VOLUME ["/data"]
EXPOSE 8080
USER ${SENAITE_USER}

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["start"]
