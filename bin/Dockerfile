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

#This adds a symbolic link that allows us to point to project files using a common
# path if run with docker or conda.
RUN ln -s /home/vmagent /.condaUser

#Adds the current directory into the docker container as the /app directory:
ADD . /app/

# #For creating the tables:
# CMD python create_tables.py
