import psycopg

with psycopg.connect("dbname=test user=postgres") as conn:
    with conn.cursor() as cur:
        cur.execute("""
                   CREATE TABLE test (
                       id serial PRIMARY KEY,
                       num integer,
                       data text)
                   """)
        cur.execute("INSERT INTO test (num, data) VALUES (%s, %s)", (100, "abc'def"))

        # Query the database and obtain data as Python objects.
        cur.execute("SELECT * FROM test")
        print(cur.fetchone())
        # will print (1, 100, "abc'def")

        # You can use `cur.executemany()` to perform an operation in batch
        cur.executemany("INSERT INTO test (num) values (%s)", [(33,), (66,), (99,)])

        # You can use `cur.fetchmany()`, `cur.fetchall()` to return a list
        # of several records, or even iterate on the cursor
        cur.execute("SELECT id, num FROM test order by num")
        for record in cur:
            print(record)

        # Make the changes to the database persistent
        conn.commit()
