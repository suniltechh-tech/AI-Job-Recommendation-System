import MySQLdb

try:
    conn = MySQLdb.connect(
        host="localhost",
        user="root",
        passwd="Mohitkumar.3380",
        db="job_ai"
    )

    print("✅ Connected Successfully!")

    conn.close()

except Exception as e:
    print(e)