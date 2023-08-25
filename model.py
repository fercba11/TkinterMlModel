from peewee import Model, SqliteDatabase, TextField, FloatField, BlobField, IntegerField
from PIL import Image as PILImage
from observador import Observer

# Modelo
db = SqliteDatabase('image_database.db')

class BaseModel(Model):
    class Meta:
        database = db

class Image(BaseModel):
    id = IntegerField(primary_key=True)
    name = TextField()
    label = TextField()
    probability = FloatField()
    image = BlobField()

db.connect()
db.create_tables([Image])


class CRUD(Observer):

    def __init__(self):
        self.observadores = []
    
    
    def agregar(self, observador):
        self.observadores.append(observador)

    def quitar(self, observador):
        self.observadores.remove(observador)

    def notificar(self, *args):
        for observador in self.observadores:
            observador.update(args)


    # @staticmethod
    def insert_image(self, name, label, probability, image_data):
        with db:
            # Image.create_table()
            Image.create(name=name, label=label, probability=probability, image=image_data)
            self.notificar("insert_image", name, label, probability, image_data)

    # @staticmethod
    def get_all_images(self):
        return Image.select()

    # @staticmethod
    def delete_image(self, image_id):
        with db:
            image = Image.get(Image.id == image_id)
            image.delete_instance()
            self.notificar("delete_image", image_id)

    def update(self, *args):
        operation = args[0]  # El primer argumento es el tipo de operación (ejemplo: "insert_image")
        if operation == "insert_image":
            print("Imagen insertada:", args[1:])  # Imprime los demás argumentos
        elif operation == "delete_image":
            print("Imagen eliminada:", args[1])
