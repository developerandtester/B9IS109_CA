
import os

class Config:

    MYSQL_DATABASE_HOST = os.getenv('MYSQL_DATABASE_HOST', 'localhost')
    MYSQL_DATABASE_PORT = os.getenv('MYSQL_DATABASE_PORT', '3306')
    MYSQL_DATABASE_USER = os.getenv('MYSQL_DATABASE_USER', 'root')
    MYSQL_DATABASE_PASSWORD = os.getenv('MYSQL_DATABASE_PASSWORD', 'pass')
    MYSQL_DATABASE_DB = os.getenv('MYSQL_DATABASE_DB', 'pract_database')


