#!/usr/bin/env python
# coding: utf-8
import pandas as pd
import os
import argparse
from time import time
from sqlalchemy import create_engine


def main(params):
    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name = params.table_name
    url = params.url
    if url.endswith('.csv.gz'):
        csv_name = 'output.csv.gz'
    else:
        csv_name = 'output.csv'
    
    os.system(f"wget {url} -O {csv_name}")
    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db}")
    engine.connect()
    df_iter = pd.read_csv(csv_name, iterator=True, chunksize= 100000, low_memory= False)
    df = next(df_iter);

    df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime)
    df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime)

    df.head(0).to_sql(name = table_name, con = engine, if_exists= "replace")
    df.to_sql(name=table_name, con=engine, if_exists='append')

    while True:
        try:
            time_start = time();
            df = next(df_iter);
            df.tpep_pickup_datetime = pd.to_datetime(df.tpep_pickup_datetime);
            df.tpep_dropoff_datetime = pd.to_datetime(df.tpep_dropoff_datetime);
            time_end = time();
            print("Inserted another chunk, cost: %.3f seconds" %(time_end - time_start));
        except StopIteration:
            print("Finished ingesting data into the postgres database")
            break

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Ingest CSV data to Postgres")

    parser.add_argument("--user", help="username for postgres")
    parser.add_argument("--password", help="password for postgres")
    parser.add_argument("--host", help="host for postgres")
    parser.add_argument("--port", help="port for postgres")
    parser.add_argument("--db", help="db name for postgres")
    parser.add_argument("--table_name", help=" table name for postgres")
    parser.add_argument("--url", help="csv URL for db")

    params = parser.parse_args();
    main(params)
        
        

