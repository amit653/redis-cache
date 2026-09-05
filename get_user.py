from fastapi import FastAPI
import psycopg2
import redis
import hashlib
import json
app=FastAPI()
conn=psycopg2.connect("dbname=testdb user=postgres password=postgres host=localhost port=5432")
cur=conn.cursor()

r = redis.Redis(host="localhost", port=6379, db=0)
def get_user_by_name(name:str): # ->str:
    #key = "user_cache:" + name # OR
    user_id = r.get(f"user_index:{name}")
    if user_id: 
    # 1. Try Redis cache first
        cache_key=f"user:{user_id.decode()}"
        #print("cache key",cache_key,type(cache_key))
        user_data=r.hgetall(cache_key)
        #print("user_data",user_data)
        if user_data:
            print("Cache hit!")
            return {k.decode(): v.decode() for k, v in user_data.items()}

    print("Cache miss, querying Postgres...")
    cur.execute("SELECT a.* FROM users a WHERE a.name = %s AND a.id=(select max(c.id) from users c,users d ) order by id desc ", (name,))
    row = cur.fetchone()
    #print (row)

    if row:
        user_id, name, age, city = row
        print(user_id)
        user_data = {"id": user_id, "name": name, "age": age, "city": city}
        print(user_data)
        #SET builds the index, and HSET builds the record.it persists unless you add a TTL.
        r.hset(f"user:{user_id}", mapping={"name": name, "age": age, "city": city})
        r.set(f"user_index:{name}", user_id)
        r.expire(f"user:{user_id}", 20)  # expire in 20 seconds verify from cli HGETALL user:9 , delete latest rec -DEL user:100
        return user_data
    return None
    
# --- Example usage ---
user = get_user_by_name("test")
print("User:", user)
# Call again -> should hit Redis
#user = get_user_by_name("test")
#print("User:", user)

# Cleanup
cur.close()
conn.close()

#simulate cache hit manually from cli , 127.0.0.1:6379> DEL user:10000 and run python get_user.py
