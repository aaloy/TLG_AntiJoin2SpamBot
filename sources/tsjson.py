# -*- coding: utf-8 -*-
"""
Script:
    tsjson.py
Description:
    Thread-Safe json files read/write library.
Author:
    Jose Rios Rubio
Creation date:
    20/07/2017
Last modified date:
    25/08/2017
Version:
    1.2.0
"""

####################################################################################################

# Modulos importados ###

import os
import json
from collections import OrderedDict
from filelock import Timeout, FileLock
from pathlib import Path

####################################################################################################
import logging

log = logging.getLogger(__name__)

try:
    import config
except ImportError as error:
    print("""You need to create and configure the config.py module. """)
    print(
        """The config.py module contains the configuration parameter the bot
needs to work properly. Please refer to the README file for more information."""
    )


class TSjson(object):
    """
    Thread-Safe json files read/write library
    """

    def __init__(self, file_name):
        """Creates the lock engine"""
        self.lock = FileLock("{}.lock".format(file_name))
        self.file_name = file_name

    def read(self):
        """Reads a json file in thread safe mode and puts its contents in
        an ordered dict. The file must be in utf-8 encoding.
        """
        try:
            with self.lock.acquire(timeout=getattr(config, "LOCK_TIMEOUT", 10)):
                arx = Path(self.file_name)
                if arx.exists() and arx.is_file() and arx.stat().st_size:
                    with arx.open(mode="r", encoding="utf-8") as f:
                        content = json.load(f, object_pairs_hook=OrderedDict)
                else:
                    content = {}
        except Timeout:
            log.error("Error adquiring lock for file {}".format(self.file_name))
            content = None
        return content

    def _ensure_dir(self):
        """Ensures that the directory exists"""
        directory = Path(self.file_name)
        if not directory.parent.exists():
            directory.mkdir(parents=True, exist_ok=True)

    def write(self, data):
        """Writes the json file to disk"""
        self._ensure_dir()
        try:
            with self.lock.acquire(timeout=getattr(config, "LOCK_TIMEOUT", 10)):
                with open(self.file_name, "w", encoding="utf-8") as f:
                    # Escribimos en el archivo los datos json asegurando todos
                    # los caracteres ascii, codificacion utf-8 y una "indentacion" de 4 espacios
                    json.dump(data, fp=f, ensure_ascii=False, indent=4)
        except Timeout:
            log.error(
                "Unable to get lock for {}, configuration not saved".format(
                    self.file_name
                )
            )

    def read_content(self):
        """Funcion para leer el contenido de un archivo json (datos json)"""
        read = self.read()
        if read != {}:
            return read["Content"]
        else:
            return read

    def write_content(self, data):
        """Funcion para añadir al contenido de un archivo json, nuevos datos json"""
        self._ensure_dir()
        try:  # Intentar abrir el archivo
            if data:
                content = self.read()
                if not content.get("Content"):
                    content["Content"] = list()
                content["Content"].append(data)
                self.write(content)
        except IOError as e:
            log.error("I/O error({0}): {1}".format(e.errno, e.strerror))
        except ValueError:
            log.error("Data conversion error")

    def is_in(self, data):
        """Funcion para determinar si el archivo json contiene un dato json concreto"""
        found = False  # Dato inicialmente no encontrado
        file_data = self.read()  # Leer todo el archivo json
        for _data in file_data["Content"]:  # Para cada dato en el archivo json
            if data == _data:  # Si el contenido del json tiene dicho dato
                found = True  # Marcar que se ha encontrado la posicion
                break  # Interrumpir y salir del bucle
        return found

    def is_in_position(self, data):
        """Funcion para determinar si el archivo json contiene un dato json
        concreto y la posicion de este"""
        file_data = self.read()
        position = 0
        items = file_data["Content"]
        try:
            position = items.index(data)
            found = True
        except ValueError:
            found = False
        return found, position

    def remove_by_uide(self, element_value, uide):
        """
        Funcion para eliminar un dato json concreto dentro del archivo json a
        partir de un elemento identificador unico (uide)
        [Nota: Cada dato json necesita al menos 1 elemento identificador
        unico (uide), si no es asi, la eliminacion se producira en el primer
        dato con dicho elemento uide que se encuentre]"""
        file_content = self.read_content()  # Leer el contenido del archivo json
        for data in file_content:  # Para cada dato json contenido
            if data[uide] == element_value:  # Si el dato coincide con el buscado
                file_content.remove(data)  # Eliminamos el dato
                break  # Interrumpir y salir del bucle
        self.clear_content()  # Eliminamos el contenido del archivo
        if file_content:  # Si hay algun dato en el contenido modificado
            self.write_content(
                file_content[0]
            )  # Write the modified content (without the item)

    def search_by_uide(self, element_value, uide):
        """
        Funcion para buscar un dato json concreto dentro del archivo json a
        partir de un elemento identificador unico (uide)
        [Nota: Cada dato json necesita al menos 1 elemento identificador unico
        (uide), si no es asi, la actualizacion se producira en el primer dato
        con dicho elemento uide que se encuentre]"""

        result = dict()  # Diccionario para el resultado de la busqueda
        result["found"] = False  # Dato inicialmente no encontrado
        result["data"] = None  # Dato encontrado inicialmente con ningun valor
        file_data = self.read()  # Leer todo el archivo json
        for element in file_data["Content"]:  # Para cada elemento en el archivo json
            if element:  # Si el contenido no esta vacio
                if (
                    element_value == element[uide]
                ):  # Si el dato json tiene el UIDE buscado
                    result["found"] = True  # Marcar que se ha encontrado la posicion
                    result["data"] = element  # Obtenemos el dato encontrado
                    break  # Interrumpir y salir del bucle
        return result  # Devolver si se ha encontrado o no y el dato encontrado

    def update(self, data, uide):
        """
        Funcion para actualizar datos de un archivo json
        [Nota: Cada dato json necesita al menos 1 elemento identificador unico 
        (uide), si no es asi, la actualizacion se producira en el primer dato 
        con dicho elemento uide que se encuentre]
        """
        file_data = self.read()  # Leer todo el archivo json
        # Buscar la posicion del dato en el contenido json
        found = 0
        i = 0
        for msg in file_data["Content"]:  # Para cada dato json en el archivo json
            if data[uide] == msg[uide]:  # Si el dato json tiene el UIDE buscado
                found = 1  # Marcar que se ha encontrado la posicion
                break  # Interrumpir y salir del bucle
            i = i + 1  # Incrementar la posicion del dato
        if found:  # Si se encontro en el archivo json datos con el UIDE buscado
            file_data["Content"][i] = data
            self.write(file_data)  # Escribimos el dato actualizado en el archivo json
        else:  # No se encontro ningun dato json con dicho UIDE
            log.error("Error: UIDE no encontrado en el archivo, o el archivo no existe")

    def update_twice(self, data, uide1, uide2):
        """
        Funcion para actualizar datos de un archivo json
        [Nota: Cada dato json necesita al menos 1 elemento identificador unico 
        (uide), si no es asi, la actualizacion se producira en el primer 
        elemento que se encuentre]
        """
        file_data = self.read()  # Leer todo el archivo json

        # Buscar la posicion del dato en el contenido json
        found = 0  # Posicion encontrada a 0
        i = 0  # Posicion inicial del dato a 0
        for msg in file_data["Content"]:  # Para cada dato json en el archivo json
            if (data[uide1] == msg[uide1]) and (
                data[uide2] == msg[uide2]
            ):  # Si el dato json tiene el UIDE buscado
                found = 1  # Marcar que se ha encontrado la posicion
                break  # Interrumpir y salir del bucle
            i = i + 1  # Incrementar la posicion del dato

        if found:  # Si se encontro en el archivo json datos con el UIDE buscado
            file_data["Content"][i] = data
            self.write(file_data)
        else:
            log.error("Error: UIDE no encontrado en el archivo, o el archivo no existe")

    def clear_content(self):
        """Reset all data in json file to an empty dict"""
        data = OrderedDict()
        data["Content"] = list()
        self.write(data)

    def delete(self):
        """Funcion para eliminar un archivo json"""
        with self.lock.adquire(timeout=getattr(config, "LOCK_TIMEOUT", 10)):
            if os.path.exists(self.file_name):  # Si el archivo existe
                os.remove(self.file_name)  # Eliminamos el archivo
            self.lock.release()  # Abrimos (liberamos) el mutex
