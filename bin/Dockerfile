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
ADD requirements.txt /app/
RUN pip install -r requirements.txt
ADD . /app/

# #For creating the tables:
# CMD python create_tables.py

#For running the site:
CMD gunicorn main:app -b :$PORT
#CMD gunicorn main:app -D -b :443 --certfile=ssl_cert/cert.crt --keyfile=ssl_cert/cert.key

# [END dockerfile]
