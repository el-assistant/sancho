"""Postges setup with pugsql"""
import os
import dotenv
dotenv.load_dotenv()
import pugsql


db_connection_string = os.getenv("DB_CONNECTION_STRING")
assert db_connection_string is not None

queries = pugsql.module("sancho/sql/")
queries.connect(db_connection_string)
