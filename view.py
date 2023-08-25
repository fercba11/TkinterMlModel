import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk
from model import CRUD
from decorador import *
import os
import socket


class Vista(tk.Frame):

    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.grid(row=0, column=0, sticky="nsew")

        self.var_imagen = tk.StringVar()
        self.var_label = tk.StringVar()
        self.var_probability = tk.IntVar()
        self.base = CRUD()

        self.image_label = tk.Label(self)
        self.image_label.grid(row=1, column=1, rowspan=10, columnspan=2)

        self.open_button = tk.Button(self, text="Open Image", command=self.open_image)
        self.open_button.grid(row=11, column=1)

        self.delete_button = tk.Button(self, text="Delete Image", command=self.delete_selected_image)
        self.delete_button.grid(row=11, column=2)

        self.edit_entry = tk.Entry(self, textvariable=self.var_label)
        self.edit_entry.grid(row=12, column=1)

        self.edit_button = tk.Button(self, text="Edit Name", command=self.edit_selected_image_name)
        self.edit_button.grid(row=12, column=2)

        self.info_label = tk.Label(self, text="Label: Unknown\nProbability: 0.00")
        self.info_label.grid(row=13, column=1, columnspan=2, rowspan=2)
        self.info_progress = ttk.Progressbar(self, maximum=10)
        self.info_progress.grid(row=15, column=1, columnspan=2)

        self.treeview = ttk.Treeview(self, columns=("id","name", "label", "probability"))
        self.treeview.heading("id", text='ID')
        self.treeview.heading("name", text='Nombre')
        self.treeview.heading("label", text='Label')
        self.treeview.heading("probability", text='Probability')
        self.treeview.column("#0", width=0, stretch=tk.NO)
        self.treeview.column("id", width=50, minwidth=50, anchor="w")
        self.treeview.column("name", width=120, minwidth=100, anchor="w")
        self.treeview.column("label", width=200, minwidth=100, anchor="w")
        self.treeview.column("probability", width=50, minwidth=50, anchor="w")
        self.treeview.grid(row=16, column=1, rowspan=5, columnspan=2)

    @decorador_registro("abrir imagen")
    def open_image(self, target_size=(224, 224)):
        file_path = filedialog.askopenfilename()
        if file_path:
            if self.is_valid_image(file_path):
                label, probability = self.controller.open_image(file_path) 
                self.show_image(file_path, label, probability) 
                send_image_data_to_server(file_path)
            else:
                messagebox.showerror('Error', 'No es un formato de imagen válida.')

    def update_treeivew(self, image_data):
        self.treeview.delete(*self.treeview.get_children())
        for item in image_data:
            self.treeview.insert("", "end", values=(item.id, item.name, item.label, item.probability))

    @decorador_registro("eliminar imagen")
    def delete_selected_image(self):
        selected_item = self.treeview.selection()[0]
        item_id = int(self.treeview.item(selected_item, "values")[0])
        self.controller.delete_image(item_id)

    @decorador_registro("editar imagen")
    def edit_selected_image_name(self):
        selected_item = self.treeview.selection()[0]
        item_id = int(self.treeview.item(selected_item, "values")[0])
        new_label = self.var_label.get()
        self.controller.edit_image_name(item_id, new_label)
    

    def show_image(self, file_path, label, probability):
        image = Image.open(file_path)  # Carga la imagen usando PIL
        resized_image = image.resize((224, 224), Image.ANTIALIAS)  # Reescala la imagen al tamaño deseado
        processed_image = ImageTk.PhotoImage(resized_image)  # Convierte la imagen en PhotoImage
        self.image_label.config(image=processed_image)
        self.image_label.image = processed_image

        self.info_label.config(text=f"Label: {label}\nProbability: {probability:.2f}")
        self.var_label.set(label)
    
    def is_valid_image(self, file_path):
        _, extension = os.path.splitext(file_path)
        return extension.lower() in ['.jpg', '.png']
    
def check_server_status(host, puerto):
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        clientsocket.connect((host, puerto))
        clientsocket.close()
        return True
    except ConnectionRefusedError:
        return False

def send_image_data_to_server(file_path):
    host = 'localhost'
    puerto = 9999

    if check_server_status(host, puerto):
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        mensaje = f'Imagen seleccionada: {file_path}'.encode('utf-8')
        clientsocket.sendto(mensaje, (host, puerto))
        print("Datos de imagen enviados al servidor")
        clientsocket.close()
        print("Cliente cerrado")
    else:
        print("El servidor no está disponible")

