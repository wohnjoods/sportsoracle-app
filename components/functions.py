import urllib
import pyodbc
from sqlalchemy import exc
from sqlalchemy import create_engine
import datetime
import configparser
import math
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
    if db == 'ncaab-test':
        db = 'dev_ncaab_db'
    else:
        db = 'ncaab_db'
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


def convertYearToSeasonDateTime(self):
    Season = self.year
    if(self.month <= 12 and self.month >= 11):
        Season = self.year+1
    return Season
def getDayNumDateTime(date):
    #convert date to season value for getting date of 1st game
    seasonDate = date.convertYearToSeasonDateTime()
    db = 'ncaab'  # connects to local db
    query = 'SELECT * FROM season'
    season = read_sql_query(db, query)
    season = season[['Season', 'DayZero']]
    ZeroDate = season[(season['Season'] == seasonDate)].DayZero
    ZeroDate = ZeroDate.values[0]
    GameDate = date
    #GameDate = datetime.datetime(self.Year, self.Month, self.Day)
    ZeroDate = datetime.datetime.strptime(ZeroDate, '%m/%d/%Y')
    DayNum = GameDate-ZeroDate
    DayNum = DayNum.days
    return DayNum
#round to weekly dayNum


def getRoundedDayNum(date):
    dayNum = getDayNumDateTime(date)
    base = 7
    if dayNum % 7 == 0:
        roundDay = dayNum + 7
    else:
        roundDay = base * math.ceil(dayNum/base)
    return roundDay


def dateConversion(row):
    if isinstance(row, pd.Series):
        date = str(row.Date)
    else:
        date = row

    if date == 'NaT':
        date = None
    elif type(date) is str:
        #convert to datetime, then back to string
        date = stringToDatetime(date)
        date = datetimeToString(date)
    elif isinstance(date, datetime.datetime) or isinstance(date, datetime.date):
        date = datetimeToString(date)
    elif np.isnat(date) == False:
        #convert to datetime, then to string
        date = datetime64ToDatetime(date)
        date = datetimeToString(date)
    else:
        print("can't convert ", date, " to date")

    if isinstance(row, pd.Series):
        row.Date = date
        return row
    else:
        return date


def stringToDatetime(date):
    try:
        datetimeDate = datetime.datetime.strptime(date, '%m/%d/%Y')
    except:
        try:
            datetimeDate = datetime.datetime.strptime(date, '%Y-%m-%d')
        except:
            try:
                datetimeDate = datetime.datetime.strptime(
                    date, '%y-%m-%d')
            except:
                try:
                    datetimeDate = datetime.datetime.strptime(
                        date, '%m-%d-%y')
                except:
                    try:
                        datetimeDate = datetime.datetime.strptime(
                            date, '%m-%d-%Y')
                    except:
                        try:
                            datetimeDate = datetime.datetime.strptime(
                                date, '%y/%m/%d')
                        except:
                            try:
                                datetimeDate = datetime.datetime.strptime(
                                    date, '%Y/%m/%d')
                            except:
                                try:
                                    datetimeDate = datetime.datetime.strptime(
                                        date, '%m/%d/%y')
                                except:
                                    try:
                                        datetimeDate = datetime.datetime.strptime(
                                            date, '%Y-%m-%d %H:%M:%S')
                                    except:
                                        print("can't convert ",
                                              date, " to date")
    return datetimeDate


def datetime64ToDatetime(date):
    try:
        datetimeDate = datetime.datetime.utcfromtimestamp(
            date.tolist()/1e9)
    except:
        try:
            datetimeDate = datetime.datetime.utcfromtimestamp(date)
        except:
            try:
                datetimeDate = date.astype(datetime.datetime)
            except:
                pass

    return datetimeDate


def datetimeToString(date):
    stringDate = datetime.datetime.strftime(date, '%m/%d/%Y')
    return stringDate
