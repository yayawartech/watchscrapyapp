from django.db import migrations, models
import os
import sqlite3
from sqlite3 import Error
from datetime import datetime

def load_history_data(apps, schema_editor):
    GoldH = apps.get_model("goldapp", "GoldHistory")
    PlatinumH = apps.get_model("goldapp", "PlatinumHistory")
    SilverH = apps.get_model("goldapp", "SilverHistory")
    PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    database = os.path.join(PARENT_DIR,"res/sqlite.db")

    # create a database connection
    conn = create_connection(database)
    with conn:
        gold_data = get_gold_price(conn)
        print("Loading Gold History Data.......")
        for i in range(len(gold_data)):
            date = datetime.fromtimestamp(int(gold_data[i][0]))
            row = GoldH(id=i+1,date=date,price=gold_data[i][1])
            row.save()
        
        print("Loading Silver History Data")
        silver_data = get_silver_price(conn)
        for i in range(len(silver_data)):
            date = datetime.fromtimestamp(int(silver_data[i][0]))
            row = SilverH(id=i+1,date=date,price=silver_data[i][1])
            row.save()

        print("Loading Platinum History Data")
        platinum_data = get_platinum_price(conn)
        for i in range(len(platinum_data)):
            date = datetime.fromtimestamp(int(platinum_data[i][0]))
            row = PlatinumH(id=i+1,date=date,price=platinum_data[i][1])
            row.save()
        

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by the db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn

def get_silver_price(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM silver_price")
    rows = cur.fetchall()
    return rows

def get_gold_price(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM gold_price")
    rows = cur.fetchall()
    return rows

def get_platinum_price(conn):
    """
    Query all rows in the tasks table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute("SELECT * FROM platinum_price")
    rows = cur.fetchall()
    return rows

class Migration(migrations.Migration):
    dependencies = [
        ('goldapp', 'load_coins_information'),
    ]
    operations = [
        migrations.RunPython(load_history_data)
    ]