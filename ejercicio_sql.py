import sqlite3 as sql 
import pandas as pd

# conectarse a la base de datos
conn = sql.connect('databases/db_movies')

# Crear el cursor
cur = conn.cursor()

# Para ver las tablas
cur.execute("SELECT name FROM sqlite_master where type='table' ")
cur.fetchall() 

# Pregunta 1
pd.read_sql("""select *  from movies""", conn)
# Para ver que tiene la tabla de ratings
pd.read_sql("""select *  from ratings""", conn)

# Pregunta 2
pd.read_sql("SELECT COUNT(DISTINCT userId) FROM ratings", conn)

# Pregunta 3
pd.read_sql("SELECT AVG(rating) FROM ratings WHERE movieId = 1", conn)

# Pregunta 4
pd.read_sql("""SELECT movies.title
            FROM movies
            LEFT JOIN ratings ON movies.movieId = ratings.movieId
            WHERE ratings.rating IS NULL""", conn)

# Pregunta 5
pd.read_sql("""SELECT movies.title
            FROM movies
            LEFT JOIN ratings ON movies.movieId = ratings.movieId
            GROUP BY movies.movieId, movies.title
            HAVING COUNT(*) = 1""", conn)

# Cuáles y cuántas peliculas tienen más de una calificación
pd.read_sql("""SELECT movies.title, COUNT(ratings.rating) as cnt
            FROM movies
            LEFT JOIN ratings ON movies.movieId = ratings.movieId
            GROUP BY movies.title
            HAVING cnt > 1
            ORDER BY cnt DESC""", conn)

# Pregunta 6
pd.read_sql("""SELECT genres, count(*) as cantidad
            FROM movies
            GROUP BY genres
            ORDER BY cantidad DESC
            LIMIT 8, 1""", conn)