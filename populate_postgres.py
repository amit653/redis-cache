from fastapi import FastAPI
import psycopg2
import redis
import hashlib
import json
app=FastAPI()
conn=psycopg2.connect("dbname=testdb user=postgres password=postgres host=localhost port=5432")
cur=conn.cursor()
cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        name TEXT,
        age INT,
        city TEXT
    )
""")
conn.commit()
# Insert a record
cur.execute("""INSERT INTO users (id,name, age, city)  select generate_series(1,10000), 'test',20,'delhi'""")
conn.commit()
# Fetch record
cur.execute("SELECT id, name, age, city FROM users WHERE name = %s order by id desc limit 1", ("test",) )
user_row = cur.fetchone()
print("Postgres row:", user_row[0])

# --- Connect to Redis ---
r = redis.Redis(host="localhost", port=6379, db=0)
#Store the same user in Redis hash
user_id = user_row[0]
r.hset(f"user:{user_id}",mapping={
    "name":user_row[1],
     "age": user_row[2],
    "city": user_row[3]
})
r.set(f"user_index:{user_row[1]}", user_id)
# fetch from redis
user_data=r.hgetall(f"user:{user_id}")
print(user_data) # redis stores and returns byte strings {b'name': b'Amit', b'age': b'20', b'city': b'delhi'}

# decode  byte to string
#decode manually or use r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)
print("Redis hash:", {k.decode(): v.decode() for k, v in user_data.items()})

#val = r.get("foo")
#print(val)        # b'bar'
#print(type(val))  # <class 'bytes'>

# Cleanup
cur.close()
conn.close()