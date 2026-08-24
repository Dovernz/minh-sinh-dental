from django.db import connection
cursor = connection.cursor()

try:
    cursor.execute("SELECT count(*) FROM booking_clinic")
    print("booking_clinic exists")
except Exception as e:
    print("booking_clinic does not exist", e)

cursor = connection.cursor()
try:
    cursor.execute("SELECT count(*) FROM db_table_clinic")
    print("db_table_clinic exists")
except Exception as e:
    print("db_table_clinic does not exist", e)