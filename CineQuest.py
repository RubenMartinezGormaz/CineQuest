import tkinter as tk
from tkinter import ttk
import tkinter.filedialog as filedialog #Abrir archivos (usuario_0)
from tkinter import messagebox
from tkinter import *
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestRegressor
import nltk
#nltk.download('punkt') ##Descarga para tokenizar solo lo usaremos una vez
from nltk.tokenize import word_tokenize

movies_df = pd.read_csv('csv/movies.csv')

#cargado de películas
def peliculas_csv():
    df = pd.read_csv("csv/movies.csv")
    return list(df["title"])

#Recomendación de películas según su género
def RecomendarGenero():
    pelicula_selec = movie_combo.get()
    df = pd.read_csv("csv/movies.csv")
    peliculas_recomen = df[df["genres"] == df.loc[df["title"] == pelicula_selec, "genres"].values[0]]
   
    for i, movie in peliculas_recomen.iterrows():
        tabla_pelicula.insert("", "end", values=(movie["title"], movie["genres"]))
        
#Recomendación de películas según su sinopsis
def RecomendarSinopsis(title):
    sinopsis_df = pd.read_csv("csv/sinopsis.csv")
    movies_df = pd.read_csv("csv/movies.csv")
    resultado_df = pd.merge(movies_df, sinopsis_df, left_index=True, right_index=True)
    resultado_df = resultado_df.rename(columns={"sinopsis_x": "sinopsis", "sinopsis_y": "sinopsis"})
    movies_df = resultado_df
    movies_df["tokens"] = movies_df["sinopsis"].apply(word_tokenize)

    cv = CountVectorizer(stop_words='english')
    matriz_term = cv.fit_transform(movies_df["sinopsis"])
    sim_coseno = cosine_similarity(matriz_term)
    idx = movies_df[movies_df["title"] == title].index
    if len(idx)>0:
        idx = idx[0]
    else:
        print("No se ha encontrado la película")
        return

   
    pelicula_sim = list(enumerate(sim_coseno[idx]))
    pelicula_sim = sorted(pelicula_sim, key=lambda x: x[1], reverse=True)
    pelicula_sim = pelicula_sim[1:11]
    movie_indices = [i[0] for i in pelicula_sim]

    return movies_df.iloc[movie_indices]

#Recomendación de 10 películas al usuario que o haya visto y coincidan con sus géneros favoritos
def RecomendarUsuario():
       
        movies_df = pd.read_csv("csv/movies.csv")
        ratings_df = pd.read_csv(fichero_usuario)
        ratings_usuario = ratings_df["movieId"].tolist()
        peliculas_norating = movies_df[~movies_df["movieId"].isin(ratings_usuario)]
        peliculas_recomendadas = peliculas_norating.head(10)

        for index, movie in peliculas_recomendadas.iterrows(): 
            genre = movie["genres"].split("|")[0]
            table.insert("", "end", values=(movie["title"], genre))

#Predicción de la nota de una película dado un usuario
def PredecirRating():
    
    usuario = pd.read_csv(fichero_usuario)
    movies = pd.read_csv("csv/movies.csv")
   

   
    peliculas_vistas = usuario[["movieId","rating"]]
    peliculas_vistas = pd.merge(peliculas_vistas, movies, on='movieId')

   
    vectorizer = CountVectorizer()


    X = vectorizer.fit_transform(peliculas_vistas[["title","genres"]].apply(lambda x: ' '.join(x), axis=1))
    y = peliculas_vistas["rating"]
    model = RandomForestRegressor().fit(X, y)
    
    peliculas_novistas = movies[movies["title"]==peliculas_novistas_combobox.get()].iloc[0]
    peliculas_novistas_vectorized = vectorizer.transform(peliculas_novistas[["title","genres"]].apply(lambda x: ' '.join(x)))
    predicted_rating = model.predict(peliculas_novistas_vectorized)
    
    resultados_treeview.insert("", "end", values=(peliculas_novistas_combobox.get(), predicted_rating))

#Selección de usuario_0.csv desde la pestaña de Recomendar Usuario
def SeleccionarUsuarioRecomendar():
    global fichero_usuario
    fichero_usuario = filedialog.askopenfilename(initialdir = ".", title = "Seleccione el archivo CSV del usuario", filetypes = (("CSV files", "*.csv"), ("all files", "*.*")))
    if not fichero_usuario:
        messagebox.showerror("Error", "Por favor seleccione un archivo.")
        return
    if not fichero_usuario.endswith('.csv'):
        messagebox.showerror("Error", "Por favor seleccione un archivo CSV válido.")
    
    with open(fichero_usuario, 'r') as file:
        primera_linea = file.readline()
        
    if not all(col in primera_linea for col in ['movieId', 'title', 'rating']):
        messagebox.showerror("Error", "El archivo seleccionado no contiene los parámetros que tendría un usuario.")
        return
    else:
        with open(fichero_usuario, 'r') as file:
            label_fichero.config(text=fichero_usuario)
            
#Selección de usuario_0.csv desde la pestaña de Probabilidad de gustar
def SeleccionarUsuarioRating():
    global fichero_usuario
    fichero_usuario = filedialog.askopenfilename(initialdir = ".", title = "Seleccione el archivo CSV del usuario", filetypes = (("CSV files", "*.csv"), ("all files", "*.*")))
    if not fichero_usuario:
        messagebox.showerror("Error", "Por favor seleccione un archivo.")
        return
    if not fichero_usuario.endswith('.csv'):
        messagebox.showerror("Error", "Por favor seleccione un archivo CSV válido.")
    
    with open(fichero_usuario, 'r') as file:
        primera_linea = file.readline()
        
    if not all(col in primera_linea for col in ['movieId', 'title', 'rating']):
        messagebox.showerror("Error", "El archivo seleccionado no contiene los parámetros que tendría un usuario.")
        return
    else:
        usuario = pd.read_csv(fichero_usuario)
        with open(fichero_usuario, 'r') as file:
            label_fichero.config(text=fichero_usuario)
             # Leer el archivo CSV del usuario
            label_ruta_usuario.config(text=fichero_usuario)
            # Filtrar las películas vistas por el usuario
            peliculas_vistas = usuario[["movieId"]]
            # Obtener una lista de películas no vistas
            unpeliculas_vistas = movies_df[~movies_df["movieId"].isin(peliculas_vistas["movieId"])]
            # Asignar las películas no vistas a la combobox
            peliculas_novistas_combobox["values"] = list(unpeliculas_vistas["title"])
    
#Mostrar las recomendaciones de la pestaña de Recomendar por sinopsis   
def mostrar_recomendaciones():
    title = title_combobox.get()
    recomendaciones = RecomendarSinopsis(title)
    recomendaciones_list.delete(0, tk.END)
    for i, row in recomendaciones.iterrows():
        recomendaciones_list.insert(tk.END, row['title'])

#Actualización de combobox según lo que se escriba en busqueda
def actualizar_combobox_sinopsis(event):
    buscar_termino = entrada_busqueda.get()
    terminos_encontrados = [title for title in movies_df['title'].tolist() if buscar_termino.lower() in title.lower()]
    title_combobox['values'] = terminos_encontrados

def actualizar_combobox_genero(event):
    buscar_termino2 = entrada_busqueda2.get()
    terminos_encontrados2 = [title2 for title2 in movies_df['title'].tolist() if buscar_termino2.lower() in title2.lower()]
    movie_combo['values'] = terminos_encontrados2
    
root = tk.Tk()
root.title("CineQuest")
root.resizable(False, False)


#Fijar tamaño del root
root.geometry("625x400")



notebook = ttk.Notebook(root)
notebook.grid(column=0, row=0, padx=10, pady=10)
root.iconbitmap('img/icon.ico')


#Frames para las pestañas
tab1 = ttk.Frame(notebook)
tab2 = ttk.Frame(notebook)
tab3 = ttk.Frame(notebook)
tab4 = ttk.Frame(notebook)

#Fondo de las distintas pestañas

img= PhotoImage(file='img/bgSSII.png', master= tab1)
img_label= Label(tab1,image=img)
img_label.place(x=0, y=0)

img1= PhotoImage(file='img/bgSSII.png', master= tab2)
img_label1= Label(tab2,image=img1)
img_label1.place(x=0, y=0)

img2= PhotoImage(file='img/bgSSII.png', master= tab3)
img_label2= Label(tab3,image=img2)
img_label2.place(x=0, y=0)

img3= PhotoImage(file='img/bgSSII.png', master= tab4)
img_label3= Label(tab4,image=img3)
img_label3.place(x=0, y=0)



# Agregado de las pestañas al Notebook
notebook.add(tab1, text="Recomendar por Sinopsis")
notebook.add(tab2, text="Recomendar por Genero")
notebook.add(tab3, text="Recomendar a Usuario")
notebook.add(tab4, text="Predicción de Película")

tituloSinopsis = ttk.Label(tab1, text='RECOMENDADOR POR SINOPSIS', font='Helvetica 18 bold')
tituloSinopsis.pack()
title_label = ttk.Label(tab1, text="Seleccione el título de una película:")
title_label.pack()

title_combobox = ttk.Combobox(tab1, state="readonly", values=movies_df['title'].tolist())
title_combobox.set("Toy Story (1995)")
title_combobox.pack()

label_busqueda = ttk.Label(tab1, text="Buscar:")
label_busqueda.pack()

entrada_busqueda = ttk.Entry(tab1)
entrada_busqueda.bind("<KeyRelease>", actualizar_combobox_sinopsis)
entrada_busqueda.pack()



recomendaciones_button = ttk.Button(tab1, text="Recomendar", command=mostrar_recomendaciones)
recomendaciones_button.pack()

recomendaciones_list = tk.Listbox(tab1)
recomendaciones_list.pack()


tituloGeneros = ttk.Label(tab2, text='RECOMENDADOR POR GENERO', font='Helvetica 18 bold')
tituloGeneros.pack()
title_label2 = ttk.Label(tab2, text="Seleccione el título de una película:")
title_label2.pack()

movie_combo = ttk.Combobox(tab2, state="readonly", values=peliculas_csv())
movie_combo.set("Toy Story (1995)")
movie_combo.pack()

label_busqueda = ttk.Label(tab2, text="Buscar:")
label_busqueda.pack()


entrada_busqueda2 = ttk.Entry(tab2)
entrada_busqueda2.bind("<KeyRelease>", actualizar_combobox_genero)
entrada_busqueda2.pack()





boton_recomendar = ttk.Button(tab2, text="Recomendar", command=RecomendarGenero)
boton_recomendar.pack()

# crear una tabla para mostrar las peliculas recomendadas
tabla_pelicula = ttk.Treeview(tab2, columns=("Title", "Genre"))
tabla_pelicula.heading("Title",text="Peliculas")
tabla_pelicula.pack()


tituloRecomUsuario = ttk.Label(tab3, text='RECOMENDADAR PELICULAS A USUARIO', font='Helvetica 18 bold')
tituloRecomUsuario.pack()

fichero_usuario_label = ttk.Label(tab3, text="Seleccione el archivo CSV del usuario:")
fichero_usuario_label.pack()


boton_seleccionarusuario = ttk.Button(tab3, text="Seleccionar", command=SeleccionarUsuarioRecomendar)
boton_seleccionarusuario.pack()


label_fichero = ttk.Label(tab3)
label_fichero.pack()


boton_recomendar = ttk.Button(tab3, text="Recomendar", command=RecomendarUsuario)
boton_recomendar.pack()

table = ttk.Treeview(tab3, columns=("pelicula", "genero"))
table.heading("pelicula", text="Pelicula")
table.pack()


tituloPredRating = ttk.Label(tab4, text='PREDECIR RATING USUARIO', font='Helvetica 18 bold')
tituloPredRating.pack()

fichero_usuario_label = ttk.Label(tab4, text="Seleccione el archivo CSV del usuario: ")
fichero_usuario_label.pack()

fichero_usuario_button = ttk.Button(tab4, text="Seleccionar archivo", command=SeleccionarUsuarioRating)
fichero_usuario_button.pack()

label_ruta_usuario = ttk.Label(tab4)
label_ruta_usuario.pack()

peliculas_novistas_label = ttk.Label(tab4, text="Seleccione la película no vista: ")
peliculas_novistas_label.pack()

peliculas_novistas_combobox = ttk.Combobox(tab4, state="readonly",values=list(movies_df["title"]))
peliculas_novistas_combobox.pack()

boton_predecir = ttk.Button(tab4, text="Predecir puntuación", command=PredecirRating)
boton_predecir.pack()

resultados_treeview = ttk.Treeview(tab4, columns=("Película", "Puntuación predecida"))
resultados_treeview.heading("#0")
resultados_treeview.heading("#1", text="Titulo")
resultados_treeview.heading("#2", text="Puntuación predecida")
resultados_treeview.pack()

root.mainloop()