"""Postges setup with pugsql"""
import os
import dotenv
dotenv.load_dotenv()
import pugsql
import sqlite3

#db_connection_string = os.getenv("DB_CONNECTION_STRING")
db_connection_string="sqlite:///data/db.sqlite"
assert db_connection_string is not None

queries = pugsql.module("sancho/sql/")
queries.connect(db_connection_string)
#TODO: drop pugsql and sqlalchemy
connection = sqlite3.connect("data/db.sqlite")
connection.row_factory = sqlite3.Row
