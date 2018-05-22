# [START dockerfile]
FROM gcr.io/google_appengine/python

#Upgrade.  I do this in the Docker container so we can use the cached result before running setup.
RUN apt-get update -y && apt-get upgrade -y

#Install sudo.  I do an update again in case we are using a cached version of the last update.
RUN apt-get update -y && apt-get install -y sudo

#Add just the setup script so we can still cache the results if that doesn't change:
COPY setup.sh /app/

RUN echo ''
RUN echo 'Running setup.sh'

#This is a script that sets up our python environment using anaconda:
RUN ./setup.sh

#This adds a symbolic link that allows us to point to project files using a common
# path if run with docker or conda.
RUN ln -s /home/vmagent /.condaUser


#Adds the current directory into the docker container as the /app directory
#This is done last so that it doesn't invalidate the setup cache:
COPY . /app/

# #For creating the tables:
# CMD python create_tables.py
