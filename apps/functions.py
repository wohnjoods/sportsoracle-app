import urllib
import pyodbc
from sqlalchemy import exc
from sqlalchemy import create_engine
import configparser
import pandas as pd

def read_sql_query(db, query, params=[]):
    result = None
    cnxn = connect_sql(db)
    if params is None:
        result = pd.read_sql(query, cnxn)
    else:
        if type(params) is not list:
            params = [params]
        result = pd.read_sql(query, cnxn, params=params)
    close_sql(cnxn)
    return result


def connect_sql(db):

    config = configparser.ConfigParser()
    config.read('config.ini')
    if db == 'ncaab':
        db = 'dev_ncaab_db'
    server = config[db]['server']
    database = config[db]['database']
    username = config[db]['username']
    password = config[db]['password']
    #params = urllib.parse.quote_plus('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' +
    #                                 server+';DATABASE='+database+';UID='+username+';PWD=' + password)

    cnxn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' +
                          server+';DATABASE='+database+';UID='+username+';PWD=' + password)

    #cursor = cnxn.cursor()
    print('connected to ', server, database)
    return cnxn


def close_sql(cnxn):
    cnxn.close()
