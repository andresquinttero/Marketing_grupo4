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

# Separar géneros de cada pelicula 

genres=movies['genres'].str.split('|') 
te = TransactionEncoder() 
genres = te.fit_transform(genres) 
genres = pd.DataFrame(genres, columns = te. columns_) 
genres.columns
genres['(no genres listed)'].value_counts()
genres[genres['(no genres listed)']]

movies = pd.concat([movies, genres], axis=1)
movies = movies.drop('genres', axis=1)
movies
print(movies)
movies['(no genres listed)'].value_counts()
movies[movies['(no genres listed)']]

# # Eliminamos las 34 peliculas que no tienen calificación de género
# movies = movies.drop(movies.loc[movies['(no genres listed)'] == 1].index)
# movies = movies.drop('(no genres listed)', axis=1)
# print(movies)


##### Descripción base de movie_ratings

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

#### filtrar usuarios con más de 50 libros calificados (para tener calificaion confiable) y los que tienen mas de mill porque pueden ser no razonables

rating_users2=pd.read_sql(''' SELECT userId AS user_id,
                         COUNT(*) AS rating_count
                         FROM ratings
                         GROUP BY userId
                         HAVING rating_count >=50 and rating_count <=1000
                         ORDER BY rating_count asc
                         ''',conn )

### ver distribucion despues de filtros,ahora se ve mas razonables
rating_users2.describe()


### graficar distribucion despues de filtrar datos
fig  = px.histogram(rating_users2, x= 'rating_count', title= 'Histograma calificación por usuario')
fig.show() 

#### verificar cuantas calificaciones tiene cada libro
rating_movies=pd.read_sql(''' select movieId ,
                         count(*) as rating_count
                         from ratings
                         group by movieId
                         HAVING rating_count >= 15
                         order by rating_count desc
                         ''',conn )

### analizar distribucion de calificaciones por libro
rating_movies.describe()

### graficar distribucion

fig  = px.histogram(rating_movies, x= 'rating_count', title= 'Hist calificación para cada peli')
fig.show()  