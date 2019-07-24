# Run this from the hoff-server directory

####################################################
# Builder image
####################################################
FROM python:2.7.15-alpine3.8 AS builder

# Needs compilers for C extensions
# - linux-headers = #include <linux/whatever.h>
# - ffi and openssl secure connections
# tzdata to ensure we have timezone support
# mariadb-dev for mysql client
RUN apk add build-base linux-headers libffi-dev tzdata mariadb-dev

# Run this from hemelb-hoff/hoff-server
COPY src /src
WORKDIR /src
ENV PATH=/opt/hoffserver/bin:$PATH

# Install python things to a prefix (in increasing order of likeliness
# to change)
RUN pip install --prefix /opt/hoffserver gunicorn uwsgi enum34
RUN pip install --prefix /opt/hoffserver -r requirements.txt
RUN pip install --prefix /opt/hoffserver .

####################################################
# Result image
####################################################
FROM python:2.7.15-alpine3.8 AS output

# We need to talk to the DB
RUN apk add mariadb-connector-c-dev

# Copy the hoff prefix into the output image
COPY --from=builder /opt/hoffserver/bin/* /usr/local/bin/
COPY --from=builder /opt/hoffserver/lib/python2.7/site-packages /usr/local/lib/python2.7/site-packages

# Make Radical CT utils happy
RUN mkdir -p /root/.radical/utils/

# Timezone stuff
COPY --from=builder /usr/share/zoneinfo/UTC /etc/localtime
RUN echo "UTC" > /etc/timezone

# Start up
COPY docker/flask-app-image/entrypoint.sh /entrypoint.sh
ENTRYPOINT ["sh", "/entrypoint.sh"]
