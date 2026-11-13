# Software-FJ.py
# Fase 4 problema 1 Software FJ
import datetime
import os

# SISTEMA DE REGISTRO (LOGS)
class LoggerSistema:
    """Clase encargada de registrar eventos y errores en un archivo de texto."""
    _archivo_log = "software_fj.log"

    @classmethod
    def registrar(cls, nivel: str, mensaje: str):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entrada = f"[{timestamp}] [{nivel.upper()}] {mensaje}\n"
        try:
            with open(cls._archivo_log, "a", encoding="utf-8") as f:
                f.write(entrada)
        except Exception as e:
            print(f"Error crítico al escribir en el log: {e}")

# EXCEPCIONES PERSONALIZADAS
class SoftwareFJError(Exception):
    """Excepción base para todos los errores personalizados del sistema."""
    pass

class ClienteInvalidoError(SoftwareFJError):
    """Se lanza cuando los datos del cliente no cumplen con las validaciones."""
    pass

class ServicioNoDisponibleError(SoftwareFJError):
    """Se lanza cuando se intenta contratar un servicio inactivo o erróneo."""
    pass

class ReservaError(SoftwareFJError):
    """Se lanza ante fallos en la creación, confirmación o cancelación de reservas."""
    pass

# CLASE CLIENTE (Encapsulación y Validaciones)

class Cliente:
    def __init__(self, nombre: str, identificacion: str, correo: str):
        self.nombre = nombre
        self.__identificacion = identificacion  # Atributo privado (Encapsulación)
        self.__correo = correo                  # Atributo privado (Encapsulación)
        self.validar_datos()

    def validar_datos(self):
        """Valida que los datos del cliente sean correctos."""
        if not self.nombre or len(self.nombre.strip()) < 3:
            LoggerSistema.registrar("ERROR", f"Intento de registro con nombre inválido: {self.nombre}")
            raise ClienteInvalidoError("El nombre del cliente es muy corto o está vacío.")
        
        if not self.__identificacion or not self.__identificacion.isdigit():
            LoggerSistema.registrar("ERROR", f"Identificación inválida: {self.__identificacion}")
            raise ClienteInvalidoError("La identificación debe contener solo números.")
            
        if "@" not in self.__correo or "." not in self.__correo:
            LoggerSistema.registrar("ERROR", f"Correo electrónico inválido: {self.__correo}")
            raise ClienteInvalidoError("El formato del correo electrónico no es válido.")

    # Getters para acceder a los atributos privados de forma segura
    @property
    def identificacion(self):
        return self.__identificacion

    @property
    def correo(self):
        return self.__correo

    def __str__(self):
        return f"Cliente: {self.nombre} (ID: {self.__identificacion})"

## Mañana retomamos exactamente desde este mismo punto para construir la Clase Abstracta Servicio, sus herencias (salas, equipos y asesorías) y la lógica de reservas paso a paso con su debida explicación.