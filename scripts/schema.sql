CREATE TABLE "video_catalog" (
    "id" INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY NOT NULL,
    "source" VARCHAR NOT NULL,
    "video_id" VARCHAR NOT NULL,
    "title" varchar NOT NULL,
    "description" varchar,
    "thumbails" JSONB NOT NULL,
    "published_at" timestamp NOT NULL,
    "duration_sec" BIGINT NOT NULL,
    "content_definition" VARCHAR NOT NULL,
    "privacy_status" varchar NOT NULL,
    "views_count" BIGINT DEFAULT 0,
    "like_count" BIGINT DEFAULT 0,
    "comment_count" BIGINT DEFAULT 0,
    "favourite_count" BIGINT DEFAULT 0,
    "ts_title" TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', title)) STORED,
    "ts_description" TSVECTOR GENERATED ALWAYS AS (to_tsvector('english', description)) STORED,
    "created_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE "auth_tokens" (
    "id" INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY NOT NULL,
    "vendor" VARCHAR NOT NULL,
    "method" VARCHAR NOT NULL,
    "status" VARCHAR NOT NULL,
    "config" JSONB NOT NULL,
    "created_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "updated_at" timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE "config" (
    "last_sync_time" timestamp DEFAULT null
);

CREATE UNIQUE INDEX ON "video_catalog" ("video_id");


CREATE INDEX ts_vc_title_index ON video_catalog USING GIN (ts_title);
CREATE INDEX ts_vc_description_index ON video_catalog USING GIN (ts_description);



-- ## Adhoc
ALTER TABLE "auth_tokens" ADD COLUMN "vendor" VARCHAR;
update auth_tokens set vendor = 'google' where id = 1;

INSERT INTO auth_tokens(method, status, config) VALUES('auth_token', 'active', '{"auth_token": "AIzaSyDFDUkNIYX2j-IPQnEU5FnEehzGqKcA4dY"}')