# Fra Bo's undervisning. 
import mysql.connector

def dbaccess() :
    return mysql.connector.connect(host='localhost',
        database='sugrp001',
        user='sugrp001',
        password='E24x000GRPx62484')
