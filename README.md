# Alpha-i Detection Service for Wind farms

ADS for Wind farms is the ADS core product declined for a wind farm operation use case. You can find a tour of its
functionalities in [the product overview screencast](https://vimeo.com/302043603).

## Setup

First set the docker compose setup. This will spin up a complete environment with all the moving pieces you'll need. Namely:

- A postgres database
- A rabbitmq queue
- An elastisearch cluster
- A grafana instance
- A worker instance
- A web frontend instance 

`docker-compose up -d`

Once everything has run correctly, run the database migration with

```bash
alembic upgrade head
```

Then follow the instructions on the PROVISIONING section.

## Run

Once you have your dockerised environment up and running, you can connect to localhost:5000. Log in by using the default credentials detailed in build.env. 


PROVISIONING
------------
*This is valid only on a fresh installation of the platform with all migration executed*


- Activate the virtual environment and export your app config
```bash
$ export APP_CONFIG=environments/local.env
```

#### create users

From the root of the project run

```bash
$ bash provisioning/ads/provision.sh
```

#### populate healthscore database

This will populate the local database with some (fake) data 

connect to the instance of postgres
```bash
$ psql -h localhost -U postgres
```

connect to the appropriate database
```bash
\c anomaly
```

### Provision grafana
From the root of the project run

```bash
$ bash provisioning/grafana/provision.sh
```


OVERVIEW
--------

ADS is roughly divided in two parts: the web server and the worker. The division is reflected in the two different
processes that are brought up by docker-compose.

- The web server talks to the database and the data lake, also with the queue in order to schedule a prediction.
Data shown is fetched from elasticsearch and postgres, and shown on the web interface accordingly.

- The latest WF model is under the `models` module. Specifically, it's the `models.chunkycnn.ChunkyCNN` class.
