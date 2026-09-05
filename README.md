# redis caching for postgres table
```
--populate postgres and redis indexing for recent record inserted in postgres
python populate_postgres.py
Postgres row: 10000
{b'name': b'test', b'age': b'20', b'city': b'delhi'}
Redis hash: {'name': 'test', 'age': '20', 'city': 'delhi'}

-- cache hit 
python .\get_user.py              
user_data {b'name': b'test', b'age': b'20', b'city': b'delhi'}
Cache hit!
User: {'name': 'test', 'age': '20', 'city': 'delhi'}

-- Delete record from redis cache
127.0.0.1:6379> HGETALL user:10000
1) "name"
2) "test"
3) "age"
4) "20"
5) "city"
6) "delhi"
127.0.0.1:6379> DEL user:10000
(integer) 1
127.0.0.1:6379> HGETALL user:10000
(empty array)

--- and simulate postgres call
python .\get_user.py
Cache miss, querying Postgres...
10000
{'id': 10000, 'name': 'test', 'age': 20, 'city': 'delhi'}
User: {'id': 10000, 'name': 'test', 'age': 20, 'city': 'delhi'}

-- Now subsequent run will again hit redis cache until the TTL time 20 secs expires
 python .\get_user.py     
 ```
Cache hit!
User: {'name': 'test', 'age': '20', 'city': 'delhi'}
``
