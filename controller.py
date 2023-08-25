import tkinter as tk
from tkinter import filedialog
from view import Vista
from model import Image, CRUD
import numpy as np
import tensorflow as tf
import tensorflow_hub as hub
from PIL import Image as PILImage, ImageTk
import observador

def load_labels(file_path):
    with open(file_path, "r") as f:
        labels = f.read().splitlines()
    return labels

class ImageController:

    def __init__(self, parent):
        self.parent = parent
        self.view = Vista(self.parent, self)
        self.image_model = CRUD()
        self.current_image = None
        self.labels = load_labels('ImageNetLabels.txt')
        self.load_model()
        self.update_image_list()
        self.observador = observador.ConcreteObserverA(self.view.base)

    def load_model(self):
        model_url = "https://tfhub.dev/google/tf2-preview/mobilenet_v2/classification/4"
        self.model = tf.keras.Sequential([
            hub.KerasLayer(model_url),
            tf.keras.layers.Softmax()
        ])

    def show_image(self, file_path):
        image = PILImage.open(file_path)
        self.current_image = image
        processed_image = self.preprocess_image(image)
        self.update_image_label(processed_image)
        label, probability = self.classify_image(processed_image)
        self.update_info_label(label, probability)

    def update_image_label(self, processed_image):
        # Convierte la imagen NumPy en formato PIL
        pil_image = PILImage.fromarray(np.uint8(processed_image * 255))

        # Crea un objeto PhotoImage a partir de la imagen PIL
        photo_image = ImageTk.PhotoImage(pil_image)

        # Configura la imagen en el label de la vista
        self.view.image_label.config(image=photo_image)
        self.view.image_label.image = photo_image

    def preprocess_image(self, image, target_size=(224, 224)):
        processed_image = image.resize(target_size)

        width, height = image.size
        aspect_ratio = width / height

        if width > height:
            new_width = target_size[0]
            new_height = int(new_width / aspect_ratio)
        else:
            new_height = target_size[1]
            new_width = int(new_height * aspect_ratio)

        image = image.resize((new_width, new_height))
        
        left = (new_width - target_size[0]) // 2
        top = (new_height - target_size[1]) // 2
        right = left + target_size[0]
        bottom = top + target_size[1]
        image = image.crop((left, top, right, bottom))
        
        image = image.resize(target_size)  # Redimensiona a las dimensiones finales
        image_array = np.array(processed_image) / 255.0
        return image_array

    def classify_image(self, image_array):
        if image_array is not None:
            image_array = image_array.reshape((1, 224, 224, 3))  # Agrega una dimensión de lote
            predictions = self.model.predict(image_array)

            label_index = np.argmax(predictions)
            label = self.labels[label_index]
            probability = predictions[0][label_index]
            return label, probability
        else:
            return "Unknown", 0.0
 
    def open_image(self, file_path):
        if file_path:
            self.show_image(file_path)
            image_array = self.preprocess_image(self.current_image)
            label, probability = self.classify_image(image_array)
            image_data = self.read_image_data(file_path)
            self.image_model.insert_image(name=file_path, label=label, probability=probability, image_data=image_data)
            self.update_info_label(label, probability)
            self.update_image_list()
            # self.view.update_treeview(image_data)

            return label,probability

    def read_image_data(self, file_path):
        with open(file_path, "rb") as f:
            image_data = f.read()
        return image_data

    def update_info_label(self, label, probability):
        self.view.info_label.config(text=f"Label: {label}\nProbability: {probability:.2f}")
        self.view.var_label.set(label)

    def update_image_list(self):
        images = Image.select()
        self.view.update_treeivew(images)
        # image_data = [(str(image.id), image.name, image.label, f"{image.probability:.2f}") for image in Image.get_all_images()]
        # self.view.update_treeview(image_data)
    
    def delete_image(self, item_id):
        try:
            image = Image.get_by_id(item_id)
            image.delete_instance()
            self.update_image_list()
        except Image.DoesNotExist:
            print("Error", "La imagen no se encontró en la base de datos.")
    
    def edit_image_name(self, item_id, new_name):
        try:
            image = Image.get_by_id(item_id)
            image.name = new_name
            image.save()
            self.update_image_list()
        except Image.DoesNotExist:
            print("Error", "La imagen no se encontró en la base de datos.")


def main():
    root = tk.Tk()
    root.title("Image Recognition app")
    root.geometry("450x600")

    crud = CRUD()
    app = Image(root)
    controller = ImageController(root)

    # for i in range(17):
    #     root.grid_rowconfigure(i, weight=1)
    # for i in range(3):
    #     root.grid_columnconfigure(i, weight=1)

    root.mainloop()

if __name__ == '__main__':
    main()