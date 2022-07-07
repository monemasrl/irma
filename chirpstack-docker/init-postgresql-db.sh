#!/bin/bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL

    CREATE ROLE chirpstack_ns WITH login password 'chirpstack_ns';
    CREATE DATABASE chirpstack_ns WITH owner chirpstack_ns;

    CREATE ROLE chirpstack_as WITH login password 'chirpstack_as';
    CREATE DATABASE chirpstack_as WITH owner chirpstack_as;

    \c chirpstack_as
    create extension pg_trgm;
    create extension hstore;
	
EOSQL
