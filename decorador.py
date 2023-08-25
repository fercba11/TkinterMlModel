import datetime

def decorador_registro(actividad):
    def decorator(func):
        def wrapper(*args, **kwargs):
            retorno = func(*args, **kwargs)
            # print('Se ha guardado el registro en el archivo de registros.')
            fecha = str(datetime.datetime.now())

            archivo = open('archivo_registro.txt', 'a')
            archivo.write(f"Se ha registrado la actividad {actividad} en el dia y horario: {fecha}. \n")
            archivo.close()

            return retorno

        return wrapper

    return decorator
