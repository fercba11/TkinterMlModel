import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
import sqlite3
import os
import tensorflow as tf
import tensorflow_hub as hub
import numpy as np
import io


# Crear y conectar a la base de datos SQLite
conn = sqlite3.connect('image_database.db')
c = conn.cursor()

# Crear la tabla para almacenar la información de las imágenes
c.execute('''CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                label TEXT,
                probability REAL,
                image BLOB
             )''')
conn.commit()



# Cargar el modelo de clasificación
model_url = "https://tfhub.dev/google/tf2-preview/mobilenet_v2/classification/4"
model = tf.keras.Sequential([
    hub.KerasLayer(model_url, input_shape=(224, 224, 3))
])

def validate_image_format(func):
    def wrapper(image_path, target_size=(224, 224)):
        if image_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            return func(image_path, target_size)
        else:
            messagebox.showerror("Error de formatos", "Solo se permiten cargar imagenes en formatio .jpg, .jpeg o .png \n Vuelva a cargar la imagen con el formato correcto.")
            # raise ValueError("Unsupported image format. Only .jpg and .png are allowed.")
    return wrapper

@validate_image_format
def preprocess_image(image_path, target_size=(224, 224)):
    image = Image.open(image_path)
    
    # Calcula la nueva dimensión manteniendo el ratio original
    width, height = image.size
    aspect_ratio = width / height
    new_width = target_size[0]
    new_height = int(new_width / aspect_ratio)

    # Asegura que la imagen redimensionada tenga al menos 224x224 y luego recorta si es necesario
    if new_height < target_size[1]:
        new_height = target_size[1]
        new_width = int(new_height * aspect_ratio)

    image = image.resize((new_width, new_height))
    
    # Recorta la imagen si es más grande que el tamaño objetivo
    left = (new_width - target_size[0]) // 2
    top = (new_height - target_size[1]) // 2
    right = left + target_size[0]
    bottom = top + target_size[1]
    image = image.crop((left, top, right, bottom))
    
    image = np.array(image) / 255.0
    return np.expand_dims(image, axis=0)


def classify_image(image_path):
    preprocessed_image = preprocess_image(image_path)
    predictions = model.predict(preprocessed_image)
    # Cargamos las etiquetas de clasificación del modelo
    labels_path = tf.keras.utils.get_file('ImageNetLabels.txt', 'https://storage.googleapis.com/download.tensorflow.org/data/ImageNetLabels.txt')
    with open(labels_path) as f:
        labels = f.read().strip().split('\n')

    label_index = np.argmax(predictions)
    label = labels[label_index]
    probability = predictions[0][label_index]

    return label, probability


def insert_into_database(name, label, probability, image_path):
    with open(image_path, 'rb') as f:
        image_data = f.read()
    c.execute('''INSERT INTO images (name, label, probability, image) VALUES (?, ?, ?, ?)''',
              (name, label, probability, image_data))
    conn.commit()
    show_all_images()
    on_image_select(None)


def show_image(image_path, label, probability):
    image = Image.open(image_path)
    image = image.resize((300, 300))
    photo = ImageTk.PhotoImage(image)

    image_label.config(image=photo)
    image_label.image = photo

    info_label.config(text=f"Label: {label}\nProbability: {probability:.2f}")
    info_progress.step(probability)


def get_all_images():
    c.execute('''SELECT * FROM images''')
    return c.fetchall()


def show_all_images():
    image_list.delete(0, tk.END)
    for image_data in get_all_images():
        image_list.insert(tk.END, image_data[1])


def open_image():
    file_path = filedialog.askopenfilename()
    if file_path:
        label, probability = classify_image(file_path)
        insert_into_database(os.path.basename(file_path), label, probability, file_path)
        show_image(file_path, label, probability)

def delete_image(image_id):
    c.execute("DELETE FROM images WHERE id=?", (image_id,))
    conn.commit()
    show_all_images()

def delete_selected_image():
    index = image_list.curselection()
    if index:
        image_data = get_all_images()[index[0]]
        image_id = image_data[0]
        delete_image(image_id)
        clear_image_details()

def edit_image_name(image_id, new_name):
    c.execute("UPDATE images SET name=? WHERE id=?", (new_name, image_id))
    conn.commit()
    show_all_images()

def edit_selected_image_name():
    index = image_list.curselection()
    new_name = edit_entry.get()  # Obtener el nuevo nombre del Entry widget
    if index and new_name:
        image_data = get_all_images()[index[0]]
        image_id = image_data[0]
        edit_image_name(image_id, new_name)
        edit_entry.delete(0, tk.END)  # Limpiar el Entry widget
        clear_image_details()

def clear_image_details():
    image_label.config(image=None)
    info_label.config(text="Label: Unknown\nProbability: 0.00")


def on_image_select(event):
    index = image_list.curselection()
    if index:
        image_data = get_all_images()[index[0]]
        image = Image.open(io.BytesIO(image_data[4]))
        temp_file = "temp_image.jpg"  # Crear un archivo temporal para mostrar la imagen
        image.save(temp_file, format='JPEG')
        show_image(temp_file, image_data[2], image_data[3])
        os.remove(temp_file)



app = tk.Tk()
app.title("Image Recognition App")
app.geometry("800x900")

# Configurar el centrado de filas y columnas
for i in range(17):
    app.grid_rowconfigure(i, weight=1)
for i in range(3):
    app.grid_columnconfigure(i, weight=1)


# Interfaz gráfica

image_label = tk.Label(app)
image_label.grid(row=1, column=1, rowspan= 10, columnspan= 2)

open_button = tk.Button(app, text="Open Image", command=open_image)
open_button.grid(row=11 , column=1)
# open_button.pack(pady=10)

delete_button = tk.Button(app, text="Delete Image", command=delete_selected_image)
delete_button.grid(row=11, column=2)
# delete_button.pack(pady=10)

edit_entry = tk.Entry(app)
edit_entry.grid(row=12, column=1)
# edit_entry.pack(pady=5)

edit_button = tk.Button(app, text="Edit Name", command=edit_selected_image_name)
edit_button.grid(row=12, column=2)
# edit_button.pack(pady=5)

info_label = tk.Label(app, text="Label: Unknown\nProbability: 0.00")
info_label.grid(row=13,column=1, columnspan=2, rowspan=2)
# info_label.pack(pady=10)

info_progress = ttk.Progressbar(maximum=10)
info_progress.grid(row= 15, column=1, columnspan=2)
# info_progress.pack(pady=10)

image_list = tk.Listbox(app)
image_list.grid(row=16, column=1, rowspan=5, columnspan= 2)
image_list.bind("<<ListboxSelect>>", on_image_select)

show_all_images()

app.mainloop()