# [START dockerfile]
FROM gcr.io/google_appengine/python

# Install the fortunes binary from the debian repositories.
RUN apt-get update && apt-get install -y fortunes
RUN apt-get install -y libsm6 libxrender1 libfontconfig1 libXext6

# Change the -p argument to use Python 2.7 if desired.
RUN virtualenv /env -p python3.5

# Set virtualenv environment variables. This is equivalent to running
# source /env/bin/activate.
ENV VIRTUAL_ENV /env
ENV PATH /env/bin:$PATH
#ENV CLOUDSQL_CONNECTION_NAME snout-cloud:us-central1:snoutscandb
#ENV CLOUDSQL_USER app
#ENV CLOUDSQL_PASSWORD Pbn6u8Ew1xAiCJh7
ENV SQLALCHEMY_DATABASE_URI mysql+pymysql://root:Pbn6u8Ew1xAiCJh7@/snoutscan?unix_socket=/cloudsql/snout-cloud:us-central1:snoutscandb

ADD requirements.txt /app/
RUN pip install -r requirements.txt
ADD . /app/

CMD gunicorn main:app -b :$PORT
#CMD gunicorn main:app -D -b :443 --certfile=ssl_cert/cert.crt --keyfile=ssl_cert/cert.key

# [END dockerfile]
