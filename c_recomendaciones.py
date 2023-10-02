import sqlite3 as sql 
import pandas as pd
import a_funciones as a_funciones 
import plotly.graph_objs as go 
import plotly.express as px
from sklearn.preprocessing import MinMaxScaler
from sklearn import neighbors
from ipywidgets import interact

# Recomendaciones por popularidad

# conectarse a la base de datos
conn = sql.connect('databases/db_movies')

# Crear el cursor
cur = conn.cursor()

# Año de las peliculas más populares
sql1 = pd.read_sql('''  SELECT year, count(title) AS numberOfMovies 
                 FROM final 
                 GROUP BY year 
                 ORDER BY numberOfMovies DESC
                         ''',conn )
# Graficamos el año de las peliculas más populares
fig = px.bar(sql1, x='year', y='numberOfMovies', title='Cantidad de peliculas por año')
fig.show()

# Peliculas con más géneros
sql2 = pd.read_sql('''  SELECT title, (Action + Adventure + Animation + Children + Comedy + Crime + Documentary + 
                          Drama + Fantasy + 'Film-Noir' + Horror + IMAX + Musical + Mystery + 
                          Romance + 'Sci-Fi' + Thriller + War + Western) AS total_genres 
                      FROM final
                      GROUP BY title
                      HAVING total_genres IN (6, 7)
                      ORDER BY total_genres desc''',conn )

fig = px.bar(sql2, x='title', y='total_genres', title='Cantidad de géneros por pelicula')
fig.show()

# Géneros más populares
sql3 = pd.read_sql('''   SELECT 
    SUM(Action) AS Action, 
    SUM(Adventure) AS Adventure, 
    SUM(Animation) AS Animation,
    SUM(Children) AS Children,
    SUM(Comedy) AS Comedy,
    SUM(Crime) AS Crime,
    SUM(Documentary) AS Documentary,
    SUM(Drama) AS Drama,
    SUM(Fantasy) AS Fantasy,
    SUM("Film-Noir") AS "Film-Noir",
    SUM(Horror) AS Horror,
    SUM(IMAX) AS IMAX,
    SUM(Musical) AS Musical,
    SUM(Mystery) AS Mystery,
    SUM(Romance) AS Romance,
    SUM("Sci-Fi") AS "Sci-Fi",
    SUM(Thriller) AS Thriller,
    SUM(War) AS War,
    SUM(Western) AS Western 
    FROM final; ''',conn )

# Gráfico de barras con los géneros más populares
genres = ['Action', 'Adventure', 'Animation', 'Children', 'Comedy', 'Crime', 'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'IMAX', 'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']
counts = [sql3[genre][0] for genre in genres]

fig = go.Figure(data=[go.Bar(x=genres, y=counts)])
fig.update_layout(title='Géneros más populares')
fig.show()

# Peliculas más populares
sql4 = pd.read_sql(''' SELECT movieId, title, AVG(rating) AS average_rating
FROM final
GROUP BY movieId, title
HAVING AVG(rating) >= 4.5
ORDER BY average_rating DESC;
''',conn )

# Gráfico de barras
fig = go.Figure(data=[go.Bar(x=sql4['title'], y=sql4['average_rating'])])
fig.update_layout(title='Calificación promedio por peli >= 4.5')
fig.show()

# Peliculas mejor calificadas que han visto varias veces
sql5 = pd.read_sql("""SELECT title,
            AVG(rating) AS avg_rat,
            COUNT(*) AS view_num
            FROM final
            GROUP BY title
            HAVING view_num >= 5
            ORDER BY avg_rat DESC
            LIMIT 10
            """, conn)

# Gráfico
fig = go.Figure(data=[go.Bar(x=sql5['title'], y=sql5['avg_rat'])])
fig.update_layout(title='Top 10 Películas con Mejor Calificación Promedio (con al menos 5 vistas)',
                  xaxis_title='Película',
                  yaxis_title='Calificación Promedio')
fig.show()

# Pelicula con la mejor calificación por género
sql6 = pd.read_sql(""" SELECT genero, title, MAX(rating) AS mejor_calificacion
FROM (
    SELECT title,
           CASE
               WHEN Action = 1 THEN 'Accion'
               WHEN Adventure = 1 THEN 'Aventura'
               WHEN Animation = 1 THEN 'Animacion'
               WHEN Children = 1 THEN 'Infantil'
               WHEN Comedy = 1 THEN 'Comedia'
               WHEN Crime = 1 THEN 'Crimen'
               WHEN Documentary = 1 THEN 'Documental'
               WHEN Drama = 1 THEN 'Drama'
               WHEN Fantasy = 1 THEN 'Fantasia'
               WHEN Horror = 1 THEN 'Horror'
               WHEN IMAX = 1 THEN 'Imax'
               WHEN Musical = 1 THEN 'Musical'
               WHEN Mystery = 1 THEN 'Misterio'
               WHEN Romance = 1 THEN 'Romance'
               WHEN Thriller = 1 THEN 'Thrill'
               WHEN War = 1 THEN 'Guerra'
               WHEN Western = 1 THEN 'Occidental'
               WHEN "Sci-Fi" = 1 THEN 'Ciencia ficcion'
               WHEN "Film-Noir" = 1 THEN 'Cine negro'
           END as genero,
           rating
    FROM final
) AS generos
GROUP BY genero;
 """, conn)

# Peliculas mejor calificas por año de lanzamiento
sql7 = pd.read_sql('''SELECT title, year, AVG(rating) AS average_rating
                      FROM final
                      GROUP BY year, title
                      ORDER BY year, average_rating DESC''', conn)

fig = px.bar(sql7, x='year', y='average_rating', color='title', title='Peliculas mejor calificas por año de lanzamiento')
fig.update_layout(
    autosize=False,
    width=1000,
    height=600,
    margin=dict(l=50, r=50, b=100, t=100, pad=4)
)
fig.show()


# Recomendaciones basadas en el contenido de un producto
# Cargar los datos del DataFrame 'final'
final = pd.read_sql_query('SELECT * FROM final', conn) 



# Base de datos con Titulo, rating, generos y año de las peliculas
final= final.loc[:,~final.columns.isin(['userId','movieId'])]
final

final.to_sql('final2', conn, if_exists='replace', index=False)

# agrupacion de la base Final2 por titulo y año
final1 = pd.read_sql("""select *, avg(rating) as avg_rat
                      from final2
                      group by year, title
                      order by year desc, avg_rat desc""", conn)
final1

# convertir columna 'year' a tipo entero y escalarlo
final1['year']=final1.year.astype('int')
sc=MinMaxScaler()
final1[["year1"]]=sc.fit_transform(final1[['year']])

# borrar variables innecesarias: el año sin escalar y ratings
final2=final1.drop(columns=['year','rating','avg_rat'])
final2

# convertir a dummies el nombre de las peliculas
final3=pd.get_dummies(final2,columns=['title'])
final3

# recomendacion de las primeras 10 peliculas con mayor similitud en contenido

def recomendacion(movie=list(final1['title'])[0]):
    ind_movie = final1[final1['title'] == movie].index.values.astype(int)[0]
    similar_movie = final3.corrwith(final3.iloc[ind_movie, :], axis=1)
    similar_movie = similar_movie.sort_values(ascending=False)
    top_similar_movie = similar_movie.to_frame(name="correlación").iloc[0:11, ]
    top_similar_movie['title'] = final1["title"]

    return top_similar_movie

interact(recomendacion)