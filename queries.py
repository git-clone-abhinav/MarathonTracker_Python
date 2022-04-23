import os
import mysql.connector as mysql
from mysql.connector import Error
import logger
from dotenv import load_dotenv
import asyncio

load_dotenv()
host = os.getenv('host')
user = os.getenv('user')
password = os.getenv('pass')
database = os.getenv('db')

def connectServer():
    try: # try connecting to server
        conn = mysql.connect(host=host, user=user, password=password,database=database)
        return conn
    except Error as e: # if connection fails
        logger.logit(f"Error while connecting to MySQL: {e}")
        return None

def testQuery(query):# test query - Development only
    conn = connectServer()
    if conn is not None:
        logger.logit(f"Server Connected, Testing query... `{query}`")
        try:# try running query
            cursor = conn.cursor()
            logger.logit("Succesfull **Cursor**")
            cursor.execute(query)
            logger.logit(f"Succesfull **Query** - `{query}`")
            result = cursor.fetchall()
            logger.logit("Succesfull **Fetch**")
            cursor.close()
            logger.logit("Succesfull **Cursor Closure**")
            conn.close()
            logger.logit("Succesfull **Connection Closure**")
            logger.logit(result)
            return result
        except Error as e: # if query fails
            logger.logit(f"Error while executing query: `{e}`")
        finally:
            if conn.is_connected():
                try:
                    cursor.close()
                    logger.logit("Succesfull **Cursor Closure**")
                    conn.close()
                    logger.logit("Succesfull **Connection Closure**")
                except:
                    logger.logit("Error while Closing Connection")
                finally:
                    return None

def runQuery(query,data,queryType): # run query - Production only
    conn = connectServer()
    if conn is not None:
        try:# try running query
            if queryType == "DML":
                cursor = conn.cursor()
                cursor.execute(query,data)
                conn.commit() # remove this comment later
                cursor.close()
                conn.close()
                # logger.logit(f"Succesfull **DML Query** - `{query}`")
                return True
            elif queryType == "many":
                cursor = conn.cursor()
                cursor.executemany(query,data)
                conn.commit()
                cursor.close()
                conn.close()
                # logger.logit(f"Successfull {cursor.rowcount} row insertions")
                # logger.logit(f"Succesfull **INSERT Many Query** - `{query}`")
                return True
            else:
                cursor = conn.cursor()
                cursor.execute(query,data)
                result = cursor.fetchall()
                cursor.close()
                conn.close()
                # logger.logit(f"Succesfull **Non-DML Query** - `{query}`")
                return result
        except Error as e: # if query fails
            logger.logit(f"Failure **Query** - `{query}` - `{e}`")
        finally:
            if conn.is_connected():
                try:
                    cursor.close()
                    # logger.logit(f"Succesfull **Cursor Closure**")
                    conn.close()
                    # logger.logit(f"Succesfull **Connection Closure**")
                except:
                    logger.logit("Error while closing cursor")
                finally:
                    return None

if __name__ == "__main__":
    testQuery("SELECT * FROM `users`")