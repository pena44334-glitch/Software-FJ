# Software-FJ.py
# Fase 4 problema 1 Software FJ
import datetime
import os
from abc import ABC, abstractmethod

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
# CLASE ABSTRACTA SERVICIO
class Servicio(ABC):
    def __init__(self, codigo: str, nombre: str, tarifa_base: float, disponible: bool = True):
        self.codigo = codigo
        self.nombre = nombre
        self.__tarifa_base = tarifa_base  # Encapsulación de la tarifa
        self.disponible = disponible
        self.validar_parametros()

    @property
    def tarifa_base(self) -> float:
        return self.__tarifa_base

    def validar_parametros(self):
        """Valida que los datos base del servicio sean coherentes."""
        if not self.codigo or not self.nombre:
            LoggerSistema.registrar("ERROR", "Intento de crear servicio sin código o nombre.")
            raise ServicioNoDisponibleError("El servicio debe tener código y nombre válidos.")
        if self.__tarifa_base <= 0:
            LoggerSistema.registrar("ERROR", f"Tarifa inválida ({self.__tarifa_base}) en servicio {self.nombre}.")
            raise ServicioNoDisponibleError("La tarifa base debe ser mayor a cero.")

    @abstractmethod
    def calcular_costo(self, duracion: int, impuesto: float = 0.19, descuento: float = 0.0) -> float:
        """Método abstracto con parámetros opcionales (sobrecarga) para calcular el total."""
        pass

    @abstractmethod
    def describir(self) -> str:
        """Método abstracto que cada servicio hijo sobrescribe (polimorfismo)."""
        pass

# CLASES DERIVADAS DE SERVICIO (Herencia y Polimorfismo)
class ReservaSala(Servicio):
    def __init__(self, codigo: str, nombre: str, tarifa_base: float, capacidad: int, disponible: bool = True):
        self.capacidad = capacidad
        super().__init__(codigo, nombre, tarifa_base, disponible)

    def validar_parametros(self):
        super().validar_parametros()
        if self.capacidad <= 0:
            LoggerSistema.registrar("ERROR", f"Capacidad inválida ({self.capacidad}) en sala {self.nombre}.")
            raise ServicioNoDisponibleError("La capacidad de la sala debe ser mayor a 0 personas.")

    def calcular_costo(self, duracion: int, impuesto: float = 0.19, descuento: float = 0.0) -> float:
        if duracion <= 0:
            raise ReservaError("La duración de reserva de sala debe ser al menos 1 hora.")
        subtotal = self.tarifa_base * duracion
        total_descuento = subtotal * descuento
        subtotal_con_desc = subtotal - total_descuento
        return round(subtotal_con_desc * (1 + impuesto), 2)

    def describir(self) -> str:
        return f"[Sala] {self.nombre} (Cód: {self.codigo}) - Capacidad: {self.capacidad} personas - ${self.tarifa_base}/hora"


class AlquilerEquipo(Servicio):
    def __init__(self, codigo: str, nombre: str, tarifa_base: float, tipo_equipo: str, disponible: bool = True):
        self.tipo_equipo = tipo_equipo
        super().__init__(codigo, nombre, tarifa_base, disponible)

    def validar_parametros(self):
        super().validar_parametros()
        if not self.tipo_equipo or len(self.tipo_equipo.strip()) < 2:
            LoggerSistema.registrar("ERROR", f"Tipo de equipo inválido en {self.nombre}.")
            raise ServicioNoDisponibleError("Debe especificar un tipo de equipo válido.")

    def calcular_costo(self, duracion: int, impuesto: float = 0.19, descuento: float = 0.0) -> float:
        if duracion <= 0:
            raise ReservaError("Los días/horas de alquiler deben ser mayores a 0.")
        # Los equipos incluyen un recargo fijo de $10 por póliza de mantenimiento
        poliza = 10.0
        subtotal = (self.tarifa_base * duracion) + poliza
        subtotal_con_desc = subtotal - (subtotal * descuento)
        return round(subtotal_con_desc * (1 + impuesto), 2)

    def describir(self) -> str:
        return f"[Equipo] {self.nombre} ({self.tipo_equipo}) - ${self.tarifa_base}/día + póliza"


class AsesoriaEspecializada(Servicio):
    def __init__(self, codigo: str, nombre: str, tarifa_base: float, especialidad: str, disponible: bool = True):
        self.especialidad = especialidad
        super().__init__(codigo, nombre, tarifa_base, disponible)

    def validar_parametros(self):
        super().validar_parametros()
        if not self.especialidad:
            LoggerSistema.registrar("ERROR", f"Asesoría sin especialidad definida: {self.nombre}.")
            raise ServicioNoDisponibleError("La asesoría requiere una especialidad definida.")

    def calcular_costo(self, duracion: int, impuesto: float = 0.19, descuento: float = 0.0) -> float:
        if duracion <= 0:
            raise ReservaError("La duración de la asesoría debe ser mayor a 0 horas.")
        # Si la asesoría dura más de 5 horas, aplica automáticamente un 5% de descuento adicional
        descuento_total = descuento + (0.05 if duracion > 5 else 0.0)
        subtotal = self.tarifa_base * duracion
        subtotal_con_desc = subtotal * (1 - descuento_total)
        return round(subtotal_con_desc * (1 + impuesto), 2)

    def describir(self) -> str:
        return f"[Asesoría] {self.nombre} - Área: {self.especialidad} - ${self.tarifa_base}/hora"  

# CLASE RESERVA (Integración y Manejo Avanzado de Excepciones)
class Reserva:
    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio, duracion: int):
        if not isinstance(cliente, Cliente):
            LoggerSistema.registrar("ERROR", f"Reserva {id_reserva}: Cliente inválido.")
            raise ReservaError("La reserva debe asociarse a un objeto Cliente válido.")
        if not isinstance(servicio, Servicio):
            LoggerSistema.registrar("ERROR", f"Reserva {id_reserva}: Servicio inválido.")
            raise ReservaError("La reserva debe asociarse a un objeto Servicio válido.")
        if not servicio.disponible:
            LoggerSistema.registrar("ERROR", f"Reserva {id_reserva}: Servicio '{servicio.nombre}' no disponible.")
            raise ServicioNoDisponibleError(f"El servicio '{servicio.nombre}' no está disponible actualmente.")
        if duracion <= 0:
            LoggerSistema.registrar("ERROR", f"Reserva {id_reserva}: Duración inválida ({duracion}).")
            raise ReservaError("La duración de la reserva debe ser mayor a 0.")

        self.id_reserva = id_reserva
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "PENDIENTE"
        self.costo_total = 0.0

    def procesar_calculo(self, impuesto: float = 0.19, descuento: float = 0.0) -> float:
        """Calcula el costo aplicando encadenamiento de excepciones ante fallos."""
        try:
            if descuento < 0 or descuento >= 1:
                raise ValueError(f"Porcentaje de descuento fuera de rango: {descuento}")
            self.costo_total = self.servicio.calcular_costo(self.duracion, impuesto, descuento)
            return self.costo_total
        except (ValueError, TypeError, SoftwareFJError) as e:
            LoggerSistema.registrar("ERROR", f"Fallo en cálculo de reserva {self.id_reserva}: {e}")
            # Encadenamiento de excepciones (exige la guía)
            raise ReservaError(f"No se pudo calcular el costo de la reserva {self.id_reserva}") from e

    def confirmar(self, impuesto: float = 0.19, descuento: float = 0.0):
        """Confirma la reserva usando try / except / else."""
        try:
            if self.estado != "PENDIENTE":
                raise ReservaError(f"No se puede confirmar una reserva en estado '{self.estado}'.")
            if not self.servicio.disponible:
                raise ServicioNoDisponibleError(f"El servicio '{self.servicio.nombre}' ya fue ocupado.")
            
            self.procesar_calculo(impuesto, descuento)
            self.servicio.disponible = False
        except SoftwareFJError as e:
            LoggerSistema.registrar("ERROR", f"Error al confirmar reserva {self.id_reserva}: {e}")
            raise
        else:
            # Se ejecuta únicamente si no ocurrió ninguna excepción en el bloque try
            self.estado = "CONFIRMADA"
            LoggerSistema.registrar(
                "INFO",
                f"Reserva {self.id_reserva} CONFIRMADA | Cliente: {self.cliente.nombre} | "
                f"Servicio: {self.servicio.nombre} | Total: ${self.costo_total}"
            )

    def cancelar(self):
        """Cancela la reserva usando try / except / finally."""
        try:
            if self.estado == "CANCELADA":
                raise ReservaError(f"La reserva {self.id_reserva} ya se encuentra cancelada.")
            if self.estado == "CONFIRMADA":
                self.servicio.disponible = True  # Libera el servicio nuevamente
            self.estado = "CANCELADA"
            LoggerSistema.registrar("INFO", f"Reserva {self.id_reserva} CANCELADA correctamente.")
        except ReservaError as e:
            LoggerSistema.registrar("WARNING", f"Intento fallido de cancelación en {self.id_reserva}: {e}")
            raise
        finally:
            # Se ejecuta siempre, ocurra o no un error
            LoggerSistema.registrar("AUDITORIA", f"Proceso de cancelación finalizado para reserva {self.id_reserva}.")

# GESTOR DEL SISTEMA (Listas internas, sin BD)
class SistemaGestionFJ:
    def __init__(self):
        self.clientes: list[Cliente] = []
        self.servicios: list[Servicio] = []
        self.reservas: list[Reserva] = []
        LoggerSistema.registrar("INFO", "Sistema Integral Software FJ iniciado correctamente.")

    def registrar_cliente(self, identificacion: str, nombre: str, correo: str, telefono: str):
        try:
            # Validar que no exista identificación duplicada
            if any(c.identificacion == identificacion for c in self.clientes):
                raise ClienteInvalidoError(f"Ya existe un cliente con identificación {identificacion}.")
            nuevo_cliente = Cliente(identificacion, nombre, correo, telefono)
            self.clientes.append(nuevo_cliente)
            LoggerSistema.registrar("INFO", f"Cliente registrado: {nombre} ({identificacion}).")
            print(f"[OK] Cliente registrado: {nuevo_cliente}")
            return nuevo_cliente
        except SoftwareFJError as e:
            print(f"[ERROR CONTROLADO - CLIENTE] {e}")
            return None

    def agregar_servicio(self, servicio: Servicio):
        try:
            if any(s.codigo == servicio.codigo for s in self.servicios):
                raise ServicioNoDisponibleError(f"El código de servicio {servicio.codigo} ya existe.")
            self.servicios.append(servicio)
            LoggerSistema.registrar("INFO", f"Servicio agregado: {servicio.describir()}")
            print(f"[OK] Servicio agregado: {servicio.describir()}")
            return servicio
        except SoftwareFJError as e:
            print(f"[ERROR CONTROLADO - SERVICIO] {e}")
            return None

    def procesar_reserva(self, id_reserva: str, cliente: Cliente, servicio: Servicio,
                         duracion: int, impuesto: float = 0.19, descuento: float = 0.0):
        try:
            reserva = Reserva(id_reserva, cliente, servicio, duracion)
            reserva.confirmar(impuesto=impuesto, descuento=descuento)
            self.reservas.append(reserva)
            print(f"[OK] Reserva {id_reserva} confirmada. Total a pagar: ${reserva.costo_total}")
            return reserva
        except SoftwareFJError as e:
            print(f"[ERROR CONTROLADO - RESERVA {id_reserva}] {e}")
            return None

    def cancelar_reserva(self, reserva: Reserva):
        try:
            if reserva is None:
                raise ReservaError("No se puede cancelar una reserva inexistente (None).")
            reserva.cancelar()
            print(f"[OK] Reserva {reserva.id_reserva} cancelada y servicio liberado.")
        except SoftwareFJError as e:
            print(f"[ERROR CONTROLADO - CANCELACIÓN] {e}")

    def mostrar_resumen(self):
        print("\n" + "=" * 55)
        print("RESUMEN FINAL DEL SISTEMA - SOFTWARE FJ")
        print("=" * 55)
        print(f"Total Clientes válidos registrados : {len(self.clientes)}")
        print(f"Total Servicios en catálogo      : {len(self.servicios)}")
        print(f"Total Reservas procesadas        : {len(self.reservas)}")
        for r in self.reservas:
            print(f"  -> {r.id_reserva} | Cliente: {r.cliente.nombre} | "
                  f"Servicio: {r.servicio.nombre} | Estado: {r.estado} | Total: ${r.costo_total}")
        print("=" * 55)

# SIMULACIÓN DE OPERACIONES (Mínimo 10 requeridas)
if __name__ == "__main__":
    print("=== INICIANDO SIMULACIÓN DE SOFTWARE FJ ===\n")
    sistema = SistemaGestionFJ()

    # OP 1: Registro válido de cliente 1
    c1 = sistema.registrar_cliente("1061789456", "Laura Gómez", "laura.gomez@email.com", "3104567890")

    # OP 2: Registro válido de cliente 2
    c2 = sistema.registrar_cliente("1061987321", "Carlos Méndez", "carlos.m@empresa.co", "3209876543")

    # OP 3: Registro INVÁLIDO de cliente (correo sin @ y cédula corta)
    c_invalido = sistema.registrar_cliente("12", "Pedro Error", "pedrocorreo.com", "123")

    # OP 4: Registro INVÁLIDO de cliente duplicado
    sistema.registrar_cliente("1061789456", "Laura Duplicada", "otra@email.com", "3112223344")

    # OP 5: Creación válida de Sala de Juntas
    sala1 = sistema.agregar_servicio(ReservaSala("S-01", "Sala Ejecutiva Norte", 50.0, capacidad=12))

    # OP 6: Creación válida de Alquiler de Equipo
    equipo1 = sistema.agregar_servicio(AlquilerEquipo("E-01", "Workstation Dell RTX", 35.0, tipo_equipo="Portátil Alto Rendimiento"))

    # OP 7: Creación válida de Asesoría Especializada
    asesoria1 = sistema.agregar_servicio(AsesoriaEspecializada("A-01", "Arquitectura Cloud", 80.0, especialidad="Infraestructura AWS"))

    # OP 8: Creación INVÁLIDA de servicio (tarifa negativa -> protegida con try/except)
    try:
        sala_mala = ReservaSala("S-99", "Sala Fantasma", -20.0, capacidad=5)
        sistema.agregar_servicio(sala_mala)
    except SoftwareFJError as e:
        print(f"[ERROR CONTROLADO - CREACIÓN SERVICIO] {e}")

    # OP 9: Reserva EXITOSA de Sala (3 horas, parámetros por defecto)
    r1 = sistema.procesar_reserva("RES-001", c1, sala1, duracion=3)

    # OP 10: Reserva FALLIDA de la misma Sala (ya está ocupada por RES-001)
    r2 = sistema.procesar_reserva("RES-002", c2, sala1, duracion=2)

    # OP 11: Reserva EXITOSA de Asesoría (6 horas -> aplica bono automático + 10% descuento)
    r3 = sistema.procesar_reserva("RES-003", c2, asesoria1, duracion=6, impuesto=0.19, descuento=0.10)

    # OP 12: Reserva FALLIDA por encadenamiento de excepciones (descuento inválido del 150%)
    r4 = sistema.procesar_reserva("RES-004", c1, equipo1, duracion=2, descuento=1.5)

    # OP 13: Cancelación EXITOSA de RES-001 (libera la sala) y segundo intento FALLIDO (auditoría con finally)
    sistema.cancelar_reserva(r1)
    sistema.cancelar_reserva(r1)

    # OP 14: Nueva reserva EXITOSA de la Sala tras haber sido liberada
    r5 = sistema.procesar_reserva("RES-005", c2, sala1, duracion=4)

    # Mostrar reporte final en consola
    sistema.mostrar_resumen()
