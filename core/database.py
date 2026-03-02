"""
My Lenguaje - Sistema de Base de Datos ORM (Fase 8)
ORM en español para gestión de bases de datos

Características:
- Conexión a SQLite/MySQL/PostgreSQL
- Modelos ORM en español
- Consultas tipo Query Builder
- Migraciones automáticas
- Transacciones
- Pool de conexiones
"""

import sqlite3
import json
import os
from typing import Any, Dict, List, Optional, Tuple, Type, Union, Callable
from dataclasses import dataclass, field, asdict
from contextlib import contextmanager
from datetime import datetime
import hashlib


class ErrorBaseDeDatos(Exception):
    """Excepción para errores de base de datos"""
    pass


@dataclass
class Campo:
    """Representa un campo de una tabla"""
    nombre: str
    tipo: str = "TEXT"
    nullable: bool = True
    unico: bool = False
    clave_primaria: bool = False
    clave_foranea: str = None
    defecto: Any = None
    indice: bool = False

    def sql(self) -> str:
        """Genera SQL para el campo"""
        partes = [self.nombre, self.tipo]
        
        if self.clave_primaria:
            partes.append("PRIMARY KEY")
            if self.tipo == "INTEGER":
                partes.append("AUTOINCREMENT")
        
        if not self.nullable and not self.clave_primaria:
            partes.append("NOT NULL")
        
        if self.unico:
            partes.append("UNIQUE")
        
        if self.defecto is not None:
            if isinstance(self.defecto, str):
                partes.append(f"DEFAULT '{self.defecto}'")
            else:
                partes.append(f"DEFAULT {self.defecto}")
        
        if self.clave_foranea:
            partes.append(f"REFERENCES {self.clave_foranea}")
        
        return " ".join(partes)


@dataclass
class Modelo:
    """Clase base para modelos ORM"""
    id: int = field(default=0, metadata={"campo": Campo("id", "INTEGER", clave_primaria=True)})
    
    @classmethod
    def obtener_tabla(cls) -> str:
        """Obtiene el nombre de la tabla"""
        return cls.__name__.lower() + "s"
    
    @classmethod
    def obtener_campos(cls) -> List[Campo]:
        """Obtiene los campos del modelo"""
        campos = []
        for nombre, valor in cls.__annotations__.items():
            if nombre in cls.__dataclass_fields__:
                campo_def = cls.__dataclass_fields__[nombre]
                metadata = campo_def.metadata.get("campo")
                if metadata:
                    campos.append(metadata)
                else:
                    campos.append(Campo(nombre, cls._mapear_tipo(valor)))
        return campos
    
    @classmethod
    def _mapear_tipo(cls, tipo_python: Type) -> str:
        """Mapea tipo Python a SQL"""
        mapa = {
            int: "INTEGER",
            float: "REAL",
            str: "TEXT",
            bool: "BOOLEAN",
            bytes: "BLOB",
        }
        return mapa.get(tipo, "TEXT")
    
    def a_dict(self) -> dict:
        """Convierte el modelo a diccionario"""
        return asdict(self)
    
    def a_json(self) -> str:
        """Convierte el modelo a JSON"""
        return json.dumps(self.a_dict(), default=str)
    
    @classmethod
    def desde_dict(cls, datos: dict):
        """Crea un modelo desde un diccionario"""
        return cls(**{k: v for k, v in datos.items() if k in cls.__annotations__})


class Conexion:
    """
    Gestor de conexión a base de datos
    
    Ejemplo:
        db = Conexion("mi_base.db")
        db.conectar()
    """
    
    def __init__(self, cadena_conexion: str, tipo: str = "sqlite"):
        self.cadena = cadena_conexion
        self.tipo = tipo
        self.conexion = None
        self.cursor = None
        self.pool: List[sqlite3.Connection] = []
        self.tamano_pool = 5
    
    def conectar(self):
        """Establece la conexión"""
        try:
            if self.tipo == "sqlite":
                self.conexion = sqlite3.connect(self.cadena, check_same_thread=False)
                self.conexion.row_factory = sqlite3.Row
                self.cursor = self.conexion.cursor()
            elif self.tipo == "mysql":
                import mysql.connector
                self.conexion = mysql.connector.connect(
                    host="localhost",
                    user="root",
                    password="",
                    database=self.cadena
                )
                self.cursor = self.conexion.cursor(dictionary=True)
            elif self.tipo == "postgresql":
                import psycopg2
                self.conexion = psycopg2.connect(self.cadena)
                self.cursor = self.conexion.cursor()
            
            self._inicializar_pool()
        except Exception as e:
            raise ErrorBaseDeDatos(f"Error al conectar: {e}")
    
    def _inicializar_pool(self):
        """Inicializa el pool de conexiones"""
        for _ in range(self.tamano_pool):
            if self.tipo == "sqlite":
                conn = sqlite3.connect(self.cadena, check_same_thread=False)
                conn.row_factory = sqlite3.Row
                self.pool.append(conn)
    
    def obtener_conexion(self) -> sqlite3.Connection:
        """Obtiene una conexión del pool"""
        if self.pool:
            return self.pool.pop()
        return self.conexion
    
    def liberar_conexion(self, conexion: sqlite3.Connection):
        """Libera una conexión al pool"""
        self.pool.append(conexion)
    
    def cerrar(self):
        """Cierra la conexión"""
        if self.cursor:
            self.cursor.close()
        if self.conexion:
            self.conexion.close()
        for conn in self.pool:
            conn.close()
    
    def ejecutar(self, sql: str, parametros: tuple = None) -> List[dict]:
        """Ejecuta una consulta SQL"""
        if not self.conexion:
            raise ErrorBaseDeDatos("No hay conexión activa")
        
        try:
            if parametros:
                self.cursor.execute(sql, parametros)
            else:
                self.cursor.execute(sql)
            
            if sql.strip().upper().startswith("SELECT"):
                resultados = self.cursor.fetchall()
                return [dict(row) for row in resultados]
            else:
                self.conexion.commit()
                return [{"filas_afectadas": self.cursor.rowcount}]
        except Exception as e:
            self.conexion.rollback()
            raise ErrorBaseDeDatos(f"Error al ejecutar: {e}")
    
    @contextmanager
    def transaccion(self):
        """Context manager para transacciones"""
        try:
            yield self
            self.conexion.commit()
        except Exception as e:
            self.conexion.rollback()
            raise e


class QueryBuilder:
    """
    Constructor de consultas SQL
    
    Ejemplo:
        qb = QueryBuilder(db, "usuarios")
        resultados = qb.seleccionar("*").donde("edad > 18").ejecutar()
    """
    
    def __init__(self, db: Conexion, tabla: str):
        self.db = db
        self.tabla = tabla
        self.columnas = ["*"]
        self.condiciones = []
        self.valores_condicion = []
        self.orden = None
        self.limite = None
        self.offset = None
        self.joins = []
        self.grupo = None
        self.having = None
    
    def seleccionar(self, *columnas) -> 'QueryBuilder':
        """Selecciona columnas"""
        self.columnas = list(columnas) if columnas else ["*"]
        return self
    
    def donde(self, condicion: str, *valores) -> 'QueryBuilder':
        """Agrega condición WHERE"""
        self.condiciones.append(condicion)
        self.valores_condicion.extend(valores)
        return self
    
    def ordenar_por(self, columna: str, ascendente: bool = True) -> 'QueryBuilder':
        """Ordena resultados"""
        direccion = "ASC" if ascendente else "DESC"
        self.orden = f"{columna} {direccion}"
        return self
    
    def limitar(self, limite: int, offset: int = 0) -> 'QueryBuilder':
        """Limita resultados"""
        self.limite = limite
        self.offset = offset
        return self
    
    def unir(self, tabla: str, condicion: str, tipo: str = "INNER") -> 'QueryBuilder':
        """Agrega JOIN"""
        self.joins.append(f"{tipo} JOIN {tabla} ON {condicion}")
        return self
    
    def agrupar_por(self, columna: str) -> 'QueryBuilder':
        """Agrega GROUP BY"""
        self.grupo = columna
        return self
    
    def teniendo(self, condicion: str) -> 'QueryBuilder':
        """Agrega HAVING"""
        self.having = condicion
        return self
    
    def _construir_sql(self) -> Tuple[str, tuple]:
        """Construye la consulta SQL"""
        columnas_sql = ", ".join(self.columnas)
        sql = f"SELECT {columnas_sql} FROM {self.tabla}"
        
        for join in self.joins:
            sql += f" {join}"
        
        if self.condiciones:
            sql += " WHERE " + " AND ".join(self.condiciones)
        
        if self.grupo:
            sql += f" GROUP BY {self.grupo}"
        
        if self.having:
            sql += f" HAVING {self.having}"
        
        if self.orden:
            sql += f" ORDER BY {self.orden}"
        
        if self.limite:
            sql += f" LIMIT {self.limite}"
            if self.offset:
                sql += f" OFFSET {self.offset}"
        
        return sql, tuple(self.valores_condicion)
    
    def ejecutar(self) -> List[dict]:
        """Ejecuta la consulta"""
        sql, valores = self._construir_sql()
        return self.db.ejecutar(sql, valores if valores else None)
    
    def primero(self) -> Optional[dict]:
        """Obtiene el primer resultado"""
        self.limite = 1
        resultados = self.ejecutar()
        return resultados[0] if resultados else None
    
    def obtener(self) -> List[dict]:
        """Obtiene todos los resultados"""
        return self.ejecutar()
    
    def contar(self) -> int:
        """Cuenta resultados"""
        self.columnas = ["COUNT(*) as total"]
        resultado = self.primero()
        return resultado.get("total", 0) if resultado else 0
    
    def insertar(self, datos: dict) -> int:
        """Inserta un registro"""
        columnas = ", ".join(datos.keys())
        placeholders = ", ".join(["?" for _ in datos])
        valores = tuple(datos.values())
        
        sql = f"INSERT INTO {self.tabla} ({columnas}) VALUES ({placeholders})"
        self.db.ejecutar(sql, valores)
        
        cursor = self.db.conexion.cursor()
        cursor.execute("SELECT last_insert_rowid()")
        return cursor.fetchone()[0]
    
    def actualizar(self, datos: dict) -> int:
        """Actualiza registros"""
        set_clausulas = ", ".join([f"{k} = ?" for k in datos.keys()])
        valores = list(datos.values()) + self.valores_condicion
        
        sql = f"UPDATE {self.tabla} SET {set_clausulas}"
        if self.condiciones:
            sql += " WHERE " + " AND ".join(self.condiciones)
        
        resultado = self.db.ejecutar(sql, tuple(valores))
        return resultado[0].get("filas_afectadas", 0)
    
    def eliminar(self) -> int:
        """Elimina registros"""
        sql = f"DELETE FROM {self.tabla}"
        if self.condiciones:
            sql += " WHERE " + " AND ".join(self.condiciones)
        
        resultado = self.db.ejecutar(sql, tuple(self.valores_condicion))
        return resultado[0].get("filas_afectadas", 0)


class ORM:
    """
    ORM principal para My Lenguaje
    
    Ejemplo:
        orm = ORM("mi_base.db")
        orm.registrar_modelo(Usuario)
        orm.crear_tablas()
    """
    
    def __init__(self, cadena_conexion: str, tipo: str = "sqlite"):
        self.db = Conexion(cadena_conexion, tipo)
        self.modelos: Dict[str, Type[Modelo]] = {}
        self.migraciones: List[str] = []
    
    def conectar(self):
        """Conecta a la base de datos"""
        self.db.conectar()
    
    def cerrar(self):
        """Cierra la conexión"""
        self.db.cerrar()
    
    def registrar_modelo(self, modelo: Type[Modelo]):
        """Registra un modelo"""
        self.modelos[modelo.obtener_tabla()] = modelo
    
    def crear_tablas(self):
        """Crea las tablas para todos los modelos"""
        for nombre, modelo in self.modelos.items():
            campos = modelo.obtener_campos()
            
            if not campos:
                campos = [Campo("id", "INTEGER", clave_primaria=True)]
            
            columnas_sql = ", ".join([c.sql() for c in campos])
            sql = f"CREATE TABLE IF NOT EXISTS {nombre} ({columnas_sql})"
            
            self.db.ejecutar(sql)
            self.migraciones.append(f"Tabla {nombre} creada")
    
    def tabla(self, nombre: str) -> QueryBuilder:
        """Obtiene un QueryBuilder para una tabla"""
        return QueryBuilder(self.db, nombre)
    
    def modelo(self, modelo: Type[Modelo]) -> 'ModeloManager':
        """Obtiene un manager para un modelo"""
        return ModeloManager(self, modelo)
    
    def ejecutar_consulta(self, sql: str, parametros: tuple = None) -> List[dict]:
        """Ejecuta una consulta SQL directa"""
        return self.db.ejecutar(sql, parametros)
    
    @contextmanager
    def transaccion(self):
        """Context manager para transacciones"""
        with self.db.transaccion() as db:
            yield db
    
    def backup(self, ruta: str):
        """Crea un backup de la base de datos"""
        import shutil
        if self.db.tipo == "sqlite":
            shutil.copy2(self.db.cadena, ruta)
            self.migraciones.append(f"Backup creado en {ruta}")
    
    def restaurar(self, ruta: str):
        """Restaura un backup"""
        import shutil
        if self.db.tipo == "sqlite":
            shutil.copy2(ruta, self.db.cadena)
            self.migraciones.append(f"Backup restaurado desde {ruta}")
    
    def obtener_migraciones(self) -> List[str]:
        """Obtiene el historial de migraciones"""
        return self.migraciones


class ModeloManager:
    """Manager para operaciones con modelos"""
    
    def __init__(self, orm: ORM, modelo: Type[Modelo]):
        self.orm = orm
        self.modelo = modelo
        self.tabla = modelo.obtener_tabla()
    
    def todos(self) -> List[Modelo]:
        """Obtiene todos los registros"""
        resultados = self.orm.tabla(self.tabla).seleccionar("*").ejecutar()
        return [self.modelo.desde_dict(r) for r in resultados]
    
    def buscar(self, id: int) -> Optional[Modelo]:
        """Busca por ID"""
        resultado = self.orm.tabla(self.tabla).seleccionar("*").donde("id = ?", id).primero()
        return self.modelo.desde_dict(resultado) if resultado else None
    
    def buscar_por(self, **kwargs) -> List[Modelo]:
        """Busca por criterios"""
        qb = self.orm.tabla(self.tabla).seleccionar("*")
        
        condiciones = []
        valores = []
        for campo, valor in kwargs.items():
            condiciones.append(f"{campo} = ?")
            valores.append(valor)
        
        for i, cond in enumerate(condiciones):
            qb.donde(cond, valores[i])
        
        resultados = qb.ejecutar()
        return [self.modelo.desde_dict(r) for r in resultados]
    
    def crear(self, **kwargs) -> Modelo:
        """Crea un nuevo registro"""
        datos = {k: v for k, v in kwargs.items() if k in self.modelo.__annotations__}
        id_nuevo = self.orm.tabla(self.tabla).insertar(datos)
        return self.buscar(id_nuevo)
    
    def actualizar(self, id: int, **kwargs) -> bool:
        """Actualiza un registro"""
        datos = {k: v for k, v in kwargs.items() if k in self.modelo.__annotations__}
        filas = self.orm.tabla(self.tabla).donde("id = ?", id).actualizar(datos)
        return filas > 0
    
    def eliminar(self, id: int) -> bool:
        """Elimina un registro"""
        filas = self.orm.tabla(self.tabla).donde("id = ?", id).eliminar()
        return filas > 0
    
    def contar(self) -> int:
        """Cuenta registros"""
        return self.orm.tabla(self.tabla).contar()
    
    def query(self) -> QueryBuilder:
        """Obtiene un QueryBuilder"""
        return self.orm.tabla(self.tabla)


# Funciones de conveniencia en español
def conectar_base_de_datos(cadena: str, tipo: str = "sqlite") -> ORM:
    """Conecta a una base de datos"""
    orm = ORM(cadena, tipo)
    orm.conectar()
    return orm


def crear_modelo(nombre: str, campos: Dict[str, str]) -> Type[Modelo]:
    """Crea un modelo dinámicamente"""
    annotations = {"id": int}
    annotations.update(campos)
    
    modelo = type(nombre, (Modelo,), {
        "__annotations__": annotations
    })
    
    return modelo


def ejecutar_migraciones(orm: ORM):
    """Ejecuta las migraciones pendientes"""
    orm.crear_tablas()
    return orm.obtener_migraciones()


# Decoradores
def modelo(tabla: str = None):
    """Decorador para registrar modelos"""
    def decorador(cls):
        cls._tabla = tabla or cls.__name__.lower() + "s"
        return cls
    return decorador


def campo(tipo: str = "TEXT", nullable: bool = True, clave_primaria: bool = False):
    """Decorador para definir campos"""
    def decorador(func):
        return func
    return decorador
