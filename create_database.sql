DROP DATABASE IF EXISTS translink;
CREATE DATABASE translink;
DROP USER IF EXISTS translink;
CREATE USER translink WITH PASSWORD 'translink';
\c translink
GRANT ALL PRIVILEGES ON DATABASE translink to translink;
CREATE TABLE vehicles(
	id TEXT NOT NULL,
	timestamp INT NOT NULL,
	label TEXT NOT NULL,
	lat DOUBLE PRECISION,
	lon DOUBLE PRECISION,
	PRIMARY KEY (id, timestamp)
);
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO translink;
