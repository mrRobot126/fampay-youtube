# Fampay-Youtube Client

## Following requirements are part of the project
1. Support Search Query on `title` and `description` fields
    - This is provided using `GIN indexes` constructed using `ts_vectors` in postgresQl
    - Also takes care of order of words in the query if considered as a phrase
2. Paginated API for the Video Catalog
3. Video Catalog Indexer which runs every 20 sec and adds new videos to the database [checkout](/app/core/indexer.py)

<br>

## Some other features
1. Key-Rotation is supported in case some API-Key reaches its quota. PS Its very hacky
2. Modular Structure to support different technologies at different layers [Example](/app/common/svc/video_catalog_db_svc.py)
3. Connection pooling at DB level to support well in async environments.
4. Idempotent operations to better handle duplicate ingestion cases [Example](/app/common/svc/impl/postgres/pg_vc_db_svc.py)


## Getting Started

### Pre-requisites
1. Install Docker on your device
2. Setup Postgres DB
    - Setup Locally
        ```
        docker pull postgres
        docker run --name fampay-postgres -e POSTGRES_PASSWORD=<your_password> -d postgres
        ```

    - Already have setup somewhere
      <br>Just Make sure your have the connection_string or username and password

3. Modify Config
    1. Update DATABASE_URL in [docker-compose.yml](/docker-compose.yml)

<br>

4. Setup DB
Using any convenient tool Eg. `psql`
    1. Create Database with name `fampay`
    2. Run all SQL commands present in [schema.sql](/scripts/schema.sql) to create the requred tables and indexes on the DB

<br>

### App can be ran in two ways 
- With docker
- Without docker

#### With docker

Install docker on your system. 

1. Build docker images using - `docker-compose build`
2. Run the app using `docker-compose up`
3. For running in background run using the command `docker-compose up -d`

<br>

#### Without docker
```
cd app
uvicorn main:app --reload --host 0.0.0.0
```

<br>

## API Docs

- Head to `/docs` url for Swagger docs 
- ### http://localhost:8000/docs

