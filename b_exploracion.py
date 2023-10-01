import sqlite3 as sql 
import pandas as pd
import a_funciones as a_funciones 
import plotly.graph_objs as go ### para gráficos
import plotly.express as px
from mlxtend.preprocessing import TransactionEncoder 

# conectarse a la base de datos
conn = sql.connect('databases/db_movies')

# Crear el cursor
cur = conn.cursor()

# Para ver las tablas
cur.execute("SELECT name FROM sqlite_master where type='table' ")
cur.fetchall() 

############ traer tablas de BD a python ####

movies= pd.read_sql("""SELECT *  FROM movies""", conn)
movie_ratings = pd.read_sql('SELECT * FROM ratings', conn)

#####Exploración inicial #####

### Identificar campos de cruce y verificar que estén en mismo formato ####
### verificar duplicados

movies.info()
movies.head()
movies.duplicated().sum() 

movie_ratings.info()
movie_ratings.head()
movie_ratings.duplicated().sum()

# Descripción base de movies
movies

##### Descripción base de movie_ratings

# Convertirmos el timestamp de movie_ratings a formato fecha
movie_ratings['timestamp'] = pd.to_datetime(movie_ratings['timestamp'], unit='s')
movie_ratings



###calcular la distribución de calificaciones
cr = pd.read_sql("""SELECT 
                          rating AS rating, 
                          COUNT(*) AS conteo 
                          FROM ratings
                          GROUP BY rating
                          ORDER BY conteo DESC""", conn)

cr

data  = go.Bar( x=cr.rating,y=cr.conteo, text=cr.conteo, textposition="outside")
layout=go.Layout(title="Conteo de los ratings",xaxis={'title':'Rating'},yaxis={'title':'Conteo'})

go.Figure(data,layout) # La mayoría de las calificaciones fueron de 4 y de 3

### Cuántas películas calificó cada usuario 
rating_users=pd.read_sql(''' SELECT userId AS user_id,
                         COUNT(*) AS rating_count
                         FROM ratings
                         GROUP BY userId
                         ORDER BY rating_count asc
                         ''',conn )

fig  = px.histogram(rating_users, x= 'rating_count', title= 'Histograma calificación por usuario')
fig.show() # La mayoría de los usuarios califica entre 0 y 100 peliculas

rating_users.describe()
rating_users.tail(10)
#### filtrar usuarios con más de 20 y menos de 750 peliculas calificadas (para tener calificaion confiable) y los que tienen mas de mil, porque pueden ser no razonables

rating_users2=pd.read_sql(''' SELECT userId AS user_id,
                         COUNT(*) AS rating_count
                         FROM ratings
                         GROUP BY userId
                         HAVING rating_count >=20 and rating_count <=750
                         ORDER BY rating_count asc
                         ''',conn )

### Ver distribucion despues de filtros, ahora se ve mas razonables
rating_users2.describe()


### Graficar distribucion despues de filtrar datos
fig  = px.histogram(rating_users2, x= 'rating_count', title= 'Histograma calificación por usuario')
fig.show() 

#### Verificar cuantas calificaciones tiene cada pelicula
rating_movies=pd.read_sql(''' select title ,
                         count(*) as rating_count
                         from movies inner join ratings on
                         movies.movieID = ratings.movieID
                         group by title
                         order by rating_count desc
                         ''',conn )

### Analizar distribucion de calificaciones por pelicula
rating_movies
rating_movies.describe()

###  Graficar distribucion

fig  = px.histogram(rating_movies, x= 'rating_count', title= 'Hist calificación para cada peli')
fig.show()  

# Peliculas con 5 o más calificaciones
rating_movies2=pd.read_sql(''' select title ,
                         count(*) as rating_count
                         from movies inner join ratings on
                         movies.movieID = ratings.movieID
                         group by title
                         having rating_count >=5
                         order by rating_count desc
                         ''',conn )

# Analizar distribucion de calificaciones por pelicula
rating_movies2
rating_movies2.describe()

# Graficar distribución
fig  = px.histogram(rating_movies2, x= 'rating_count', title= 'Hist calificación para cada peli')
fig.show()


# Ejecutamos el archivo preprocesamiento.sql para limpiar la base de datos
a_funciones.ejecutar_sql('preprocesamiento.sql', cur)

cur.execute("select name from sqlite_master where type='table' ")
cur.fetchall()

# Base de datos limpia
final = pd.read_sql("""SELECT *  FROM final""", conn)
final

# Separar géneros de cada pelicula 

genres=final['genres'].str.split('|') 
te = TransactionEncoder() 
genres = te.fit_transform(genres) 
genres = pd.DataFrame(genres, columns = te. columns_) 

# Unimos la base de géneros con la base de películas
final = pd.concat([final, genres], axis=1)
final = final.drop('genres', axis=1)
final

# Vemos la lista de peliculas que no tienen calificación de género
final[final['(no genres listed)']]

# Extraemos el año de la columna title en otra columna 
final['year'] = final['title'].str.extract('.*\((.*)\).*', expand=True)
final
# Borramos el texto de los paréntesis de la columna title
final['title'] = final['title'].str.replace(r'\s*\([^()]*\)', '', regex=True)
final

# Reemplazamos en los géneros el false por 0 y el true por 1
final[genres.columns] = final[genres.columns].replace({False: 0, True: 1})
final

# Guardamos la base final en sql
final.to_sql('final', conn, if_exists='replace', index=False)
