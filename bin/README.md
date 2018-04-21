# SnoupScan web app for Google App Engine Flexible


## Setup

Before you can run or deploy the app, you will need to do the following:

1. Create a [Second Generation Cloud SQL](https://cloud.google.com/sql/docs/create-instance) instance. You can do this from the [Cloud Console](https://console.developers.google.com) or via the [Cloud SDK](https://cloud.google.com/sdk). To create it via the SDK use the following command:

        $ gcloud sql instances create YOUR_INSTANCE_NAME \
            --activation-policy=ALWAYS \
            --tier=db-n1-standard-1

1. Set the root password on your Cloud SQL instance:

        $ gcloud sql instances set-root-password YOUR_INSTANCE_NAME --password YOUR_INSTANCE_ROOT_PASSWORD

1. Create a [Service Account](https://cloud.google.com/sql/docs/external#createServiceAccount) for your project. You'll use this service account to connect to your Cloud SQL instance locally.

1. Download the [Cloud SQL Proxy](https://cloud.google.com/sql/docs/sql-proxy).

1. Run the proxy to allow connecting to your instance from your machine.

    $ cloud_sql_proxy \
        -dir /tmp/cloudsql \
        -instances=YOUR_PROJECT_ID:us-central1:YOUR_INSTANCE_NAME=tcp:3306 \
        -credential_file=PATH_TO_YOUR_SERVICE_ACCOUNT_JSON

1. Use the MySQL command line tools (or a management tool of your choice) to create a [new user](https://cloud.google.com/sql/docs/create-user) and [database](https://cloud.google.com/sql/docs/create-database) for your application:

    $ mysql -h 127.0.0.1 -u root -p
    mysql> create database YOUR_DATABASE;
    mysql> create user 'YOUR_USER'@'%' identified by 'PASSWORD';
    mysql> grant all on YOUR_DATABASE.* to 'YOUR_USER'@'%';
    
    Note:  This is currently automated in the "create_db.sh" script.  You can just run that instead.

1. Set the connection string environment variable. This allows the app to connect to your Cloud SQL instance through the proxy:

    export SQLALCHEMY_DATABASE_URI=mysql+pymysql://USER:PASSWORD@127.0.0.1/YOUR_DATABASE

1. Run ``create_tables.py`` to ensure that the database is properly configured and to create the tables needed for the sample.

1. Update the connection string in ``app.yaml`` with your configuration values. These values are used when the application is deployed.

## Running locally

Refer to the [top-level README](../README.md) for instructions on running and deploying.

It's recommended to follow the instructions above to run the Cloud SQL proxy. You will need to set the following environment variables via your shell before running the sample:

    $ export SQLALCHEMY_DATABASE_URI=[your connection string]
    $ python runserver.py
    
## Running using docker:
    # Make a local copy of make_env, the file that holds all variables that can be different from system to system:
        cp make_env.dist make_env
    # Edit make_env accordingly. 
    # Create the docker container (when needed) and run it using make:
        make run
    # Go to http://localhost:8000/ to view the site.
    # It should work, but should give a database connection error.
    # Set up a sql connection either throught the cloud or locally.  Here's how to do it locally:
        Install mysql-server, run create_db.sh and edit Dockerifile to run create_tables.py instead of gunicorn.  Then run the docker container one more time and then revert it. TODO:  Automate this.  It's a big cludgey.
    # Now run the following again and the db connection should work:
        make run
        