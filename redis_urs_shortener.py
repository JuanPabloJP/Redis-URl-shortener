#!/usr/bin/env python3

import tkinter as tk
from tkinter import ttk
from tkinter import *
import redis
import hashlib 

# step 2: define our connection information for Redis
# Replaces with your configuration information
redis_host = "localhost"
redis_port = 6379
redis_password = ""

def hello_redis():

    try:
        r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)
   
        # step 4: Set the hello message in Redis
        r.set("msg:hello", "Hello Redis!!!")

        # step 5: Retrieve the hello message from Redis
        msg = r.get("msg:hello")
        print(msg)        
   
    except Exception as e:
        print(e)

r = redis.StrictRedis(host=redis_host, port=redis_port, password=redis_password, decode_responses=True)

def md5_gen(url):  

    """
    Aplica un hash md5 a una URL y nos quedamos con los primeros 8 elementos para poder acortar
    la URL.
    
    >>> md5_gen("https://redis-py.readthedocs.io/en/latest/#")
    py.mentel/a8f1df4d
    
    """

    result = hashlib.md5(url.encode()) 
  
    recortada = "py.mentel/" + str(result.hexdigest())[0:8]
    
    return recortada
    
    
def f_create_user(user):

    """
    Crea un usuario en caso de que no exista y lo agrega a la lista "users".
    """

    existe = r.get("user:"+user)
    if not existe:
        r.set("user:"+user,user)
        r.lpush("users", user)

def f_shorten_url(url, user, priv = "False", categorias=[]):

    """
    Acorta la URL, crea al usuario 'user' (en caso de que no exista) y crea (o agrega) otras 	
    pares llave:valor. 
    """
    acortado=md5_gen(url)
    f_create_user(user)	
    r.set(acortado, url)
    r.set("isprivate:"+acortado, priv)
    r.set("owner:"+acortado,user)
    
    for c in categorias:
        r.sadd("urlcat:"+acortado,c)
        r.sadd("usrcat:"+user,c)
    
    r.lpush("urls:"+user,url)
	
    return acortado

def f_lenghten_url(short):
    return r.get(short)

def f_add_to_wishlist(url,user, priv ="False", categorias=[]):

    """
    Agrega la URl acortada correspondiente al usuario 'user' a su wishlist, la cual por defecto 
    se marca como pública, se le puede agregar categorías a la URL.
    """
    short = f_shorten_url(url,user,priv,categorias)
    r.lrem("wishlist:"+user, 1, short)
    r.lpush("wishlist:"+user,short)
	
def f_rem_from_wishlist(user,short):
    """
    Elimina una determinada URL (acortada) del usuario 'user'.
    """
    r.lrem("wishlist:"+user,1,short)
	
def f_intersect_interests(usr1,usr2):
    """
    Saca las categorías comunes de dos usuarios.
    """
    return r.sinter("usrcat:"+usr1,"usrcat:"+usr2)
	
	
def f_is_private_url(short):

    """
    Verifica si la URL(recortada) es pública o privada.
    """
    return r.get("isprivate:"+short) == "True"
	
def f_return_wishlist(user):

    """
    Consulta la wishlist del usuario 'user'
    """
    return r.lrange("wishlist:"+user, 0,-1)


hello_redis()
f_shorten_url("https://redis-py.readthedocs.io/en/latest/", user = "Jason", priv = "False", categorias=["Academico"])
print("Maria")
f_create_user("Maria G")
f_create_user("Jason A")
f_add_to_wishlist("https://redis-py.readthedocs.io/en/latest/","Jason A", priv ="True", categorias=["Videos", "Comedia"])
f_add_to_wishlist("https://www.reddit.com/","Maria G", priv ="False", categorias=["Memes", "Videos"])
f_add_to_wishlist("https://www.youtube.com/?hl=es-419&gl=MX","Jason A", priv ="False", categorias=["Memes", "Comedia"])
f_add_to_wishlist("https://www.wikipedia.org/","Jason G", priv ="False", categorias=["Enciclopedia", "Academico", "Historia"])
    
print(f_intersect_interests("Jason A", "Maria G"))
print(f_is_private_url("987e52fb"))
f_rem_from_wishlist("Jason A","987e52fb")
print("Jason A")
print(f_return_wishlist("Jason A"))
print('#####')
print(md5_gen("https://redis-py.readthedocs.io/en/latest/#"))


def set_usuario():
    usuario = ent_usuario.get()
    lbl_result["text"] = " Usuario: {}".format(usuario)

def show_wishlist():
    usuario = ent_usuario.get()
    items = f_return_wishlist(usuario)    

    top = Tk()  
  
    top.geometry("200x250")  
    
    lbl = Label(top,text = "Wishlist de {}".format(usuario))  
    
    listbox = Listbox(top)  
    for i,item in enumerate(items):    
        listbox.insert(i,item)  

    lbl.pack()  
    listbox.pack()  
    
    top.mainloop()

def show_wishlist_comp():
    usuario_izq = ent_usuario_izq.get()
    usuario_der = ent_usuario_der.get()
    items = f_intersect_interests(usuario_izq, usuario_der)    

    top = Tk()  
  
    top.geometry("200x250")  
    
    lbl = Label(top,text = "Wishlist de {} y {}".format(usuario_izq, usuario_der))  
    
    listbox = Listbox(top)  
    for i,item in enumerate(items):    
        listbox.insert(i,item)  

    lbl.pack()  
    listbox.pack()  
    
    top.mainloop()   

def set_url_short():
    if privado_var.get():
        privado = "True"
    else:
        privado = "False"
    categoria = ent_cat.get().split(",")
    url = ent_url.get()
    usuario = ent_usuario.get()
    acortado = f_shorten_url(url, usuario, privado, categoria)
    lbl_url["text"] = acortado

def set_url_back():
    corto = ent_short.get()
    enlongado = f_lenghten_url(corto)
    lbl_short["text"] = enlongado

def anadir_wishlist():
    if privado_var.get():
        privado = "True"
    else:
        privado = "False"
    categoria = ent_cat.get().split(",")
    url = ent_url.get()
    usuario = ent_usuario.get()
    f_add_to_wishlist(url, usuario, privado, categoria)

# Set-up the window
window = tk.Tk()
window.title("URL shortener")
window.resizable(width=False, height=False)

# Create the Fahrenheit entry frame with an Entry
# widget and label in it
frm_entry = tk.Frame(master=window)
ent_usuario = tk.Entry(master=frm_entry)

ent_usuario.grid(row=0, column=0, sticky="e")

# Create the conversion Button and result display Label
btn_convert = tk.Button(
    master=window,
    text="Set",
    command=set_usuario,
    highlightbackground="blue"
)
lbl_result = tk.Label(master=window, text="Sin Usuario")

# Set-up the layout using the .grid() geometry manager
tk.Label(window, text="Usuario: ").grid(row=0, column=0, padx=10)
frm_entry.grid(row=0, column=1, padx=10)
btn_convert.grid(row=0, column=2, pady=10)
lbl_result.grid(row=0, column=3, padx=10)

################## Pedir categorias

cat_entry = tk.Frame(master=window)
ent_cat = tk.Entry(master=cat_entry)

# Layout the temperature Entry and Label in frm_entry
# using the .grid() geometry manager
ent_usuario.grid(row=1, column=0, sticky="e")


# Set-up the layout using the .grid() geometry manager
tk.Label(window, text="Categorias: ").grid(row=1, column=0, padx=10)
cat_entry.grid(row=1, column=1, padx=10)
ent_cat.grid(row=1, column=2, pady=10)


############ Acortar URL

url_entry = tk.Frame(master=window)
ent_url = tk.Entry(master=url_entry)

# Layout the temperature Entry and Label in frm_entry
# using the .grid() geometry manager
ent_url.grid(row=2, column=0, sticky="e")

# Create the conversion Button and result display Label
btn_url = tk.Button(
    master=window,
    text="Acortar",
    command=set_url_short,
    highlightbackground="blue"
)

btn_wish = tk.Button(
    master=window,
    text="+wishlist",
    command=anadir_wishlist,
    highlightbackground="blue"
)

privado_var = BooleanVar()
priv_rl = Checkbutton(window, variable=privado_var)
lbl_privado = tk.Label(master=window, text="Privado")

lbl_url = tk.Label(master=window, text=" ")

# Set-up the layout using the .grid() geometry manager
tk.Label(window, text="URL: ").grid(row=2, column=0, padx=10)
url_entry.grid(row=2, column=1, padx=10)
btn_url.grid(row=2, column=2, pady=10)
btn_wish.grid(row=2, column=3, pady=10)
priv_rl.grid(row=2, column=4, padx=10)
lbl_privado.grid(row=2, column=5)

tk.Label(master=window, text="URL Acortado:").grid(row=3, column=0, padx=10)
lbl_url.grid(row=3, column=1, padx=10)



######## URL restore

short_entry = tk.Frame(master=window)
ent_short = tk.Entry(master=short_entry)

# Layout the temperature Entry and Label in frm_entry
# using the .grid() geometry manager
ent_short.grid(row=4, column=0, sticky="e")

# Create the conversion Button and result display Label
btn_short = tk.Button(
    master=window,
    text="Restaurar",
    command=set_url_back,
    highlightbackground="blue"
)

lbl_short = tk.Label(master=window, text=" ")

# Set-up the layout using the .grid() geometry manager
tk.Label(window, text="URL codificado: ").grid(row=4, column=0, padx=10)
short_entry.grid(row=4, column=1, padx=10)
btn_short.grid(row=4, column=2, pady=10)

tk.Label(master=window, text="URL:").grid(row=5, column=0, padx=10)
lbl_short.grid(row=5, column=1, padx=10)




######## Wishlist

btn_show = tk.Button(
    master=window,
    text="Mostrar wishlist",
    command=show_wishlist,
    highlightbackground="blue"
)

btn_show.grid(row=6, column=1)


######## Comparacion

izq_entry = tk.Frame(master=window)
der_entry = tk.Frame(master=window)
ent_usuario_izq = tk.Entry(master=izq_entry, width=12)
ent_usuario_der = tk.Entry(master=der_entry, width=12)
ent_usuario_izq.grid(row=7, column=0, sticky="e")
ent_usuario_der.grid(row=7, column=0, sticky="e")
# Create the conversion Button and result display Label
btn_convert = tk.Button(
    master=window,
    text="Comparar",
    command=show_wishlist_comp,
    highlightbackground="blue"
)
lbl_result = tk.Label(master=window, text="Sin Usuario")

# Set-up the layout using the .grid() geometry manager
tk.Label(window, text="Comparación: ").grid(row=7, column=0, padx=10)
izq_entry.grid(row = 7, column=1, padx=10)
der_entry.grid(row = 7, column=2, padx=10)
btn_convert.grid(row = 7, column=3, pady=10)


# Run the application
    
window.mainloop()
