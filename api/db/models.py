from db.database import Base

from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, BigInteger, Double, Timestamp
from sqlalchemy.orm import relationship

class TipoOrden(Base):
    __tablename__ = 'tipo_orden'
    id_tipo_orden = Column(Integer, primary_key=True)
    descripcion = Column(String)
    # Relación con la tabla OrdenTrabajo en lugar de OrdenTrabajoView
    ordenes_trabajo = relationship("OrdenTrabajo", back_populates="tipo_orden")

class Prioridad(Base):
    __tablename__ = 'prioridad'
    id_prioridad = Column(Integer, primary_key=True)
    descripcion = Column(String)
    # Relación con la tabla OrdenTrabajo en lugar de OrdenTrabajoView
    ordenes_trabajo = relationship("OrdenTrabajo", back_populates="prioridad")

class ClaseActividad(Base):
    __tablename__ = 'clase_actividad'
    id_clase_actividad = Column(Integer, primary_key=True)
    descripcion = Column(String)
    # Relación con la tabla OrdenTrabajo en lugar de OrdenTrabajoView
    ordenes_trabajo = relationship("OrdenTrabajo", back_populates="clase_actividad")

class Empresa(Base):
    __tablename__ = 'empresa'
    id_empresa = Column(Integer, primary_key=True)
    nombre = Column(String)
    # Relación con la tabla OrdenTrabajo en lugar de OrdenTrabajoView
    ordenes_trabajo = relationship("OrdenTrabajo", back_populates="empresa")

class Centro(Base):
    __tablename__ = 'centro'
    id_centro = Column(Integer, primary_key=True)
    nombre = Column(String)
    # Relación con la tabla OrdenTrabajo en lugar de OrdenTrabajoView
    ordenes_trabajo = relationship("OrdenTrabajo", back_populates="centro")

class Linea(Base):
    __tablename__ = 'linea'
    id_linea = Column(Integer, primary_key=True)
    nombre = Column(String)
    # Relación con la tabla OrdenTrabajo en lugar de OrdenTrabajoView
    ordenes_trabajo = relationship("OrdenTrabajo", back_populates="linea")

class LineaElemento(Base):
    __tablename__ = 'linea_elemento'
    id_elemento_linea = Column(Integer, primary_key=True)
    nombre = Column(String)
    # Relación con la tabla OrdenTrabajo en lugar de OrdenTrabajoView
    ordenes_trabajo = relationship("OrdenTrabajo", back_populates="linea_elemento")

class PuestoTrabajo(Base):
    __tablename__ = 'puesto_trabajo'
    id_puesto_trabajo = Column(Integer, primary_key=True)
    descripcion = Column(String)
    # Relación con la tabla OrdenTrabajo en lugar de OrdenTrabajoView
    ordenes_trabajo = relationship("OrdenTrabajo", back_populates="puesto_trabajo_responsable")

class Revision(Base):
    __tablename__ = 'revision'
    id_revision = Column(Integer, primary_key=True)
    descripcion = Column(String)
    # Relación con la tabla OrdenTrabajo en lugar de OrdenTrabajoView
    ordenes_trabajo = relationship("OrdenTrabajo", back_populates="revision")

class Equipo(Base):
    __tablename__ = 'equipo'
    id_equipo = Column(Integer, primary_key=True)
    nombre = Column(String)
    # Relación con la tabla OrdenTrabajo en lugar de OrdenTrabajoView
    ordenes_trabajo = relationship("OrdenTrabajo", back_populates="equipo")

class GrupoPlanificacion(Base):
    __tablename__ = 'grupo_planificacion'
    id_grupo_planificacion = Column(Integer, primary_key=True)
    descripcion = Column(String)
    # Relación con la tabla OrdenTrabajo en lugar de OrdenTrabajoView
    ordenes_trabajo = relationship("OrdenTrabajo", back_populates="grupo_planificacion")

class OrdenTrabajo(Base):
    __tablename__ = 'orden_trabajo'

    id_orden = Column(BigInteger, primary_key=True, index=True)
    id_tipo_orden = Column(Integer, ForeignKey('tipo_orden.id_tipo_orden'))
    id_prioridad = Column(Integer, ForeignKey('prioridad.id_prioridad'))
    id_clase_actividad = Column(Integer, ForeignKey('clase_actividad.id_clase_actividad'))
    id_empresa = Column(Integer, ForeignKey('empresa.id_empresa'))
    id_centro = Column(Integer, ForeignKey('centro.id_centro'))
    id_linea = Column(Integer, ForeignKey('linea.id_linea'))
    id_elemento_linea = Column(Integer, ForeignKey('linea_elemento.id_elemento_linea'))
    id_puesto_trabajo_responsable = Column(Integer, ForeignKey('puesto_trabajo.id_puesto_trabajo'))
    id_revision = Column(Integer, ForeignKey('revision.id_revision'))
    id_equipo = Column(Integer, ForeignKey('equipo.id_equipo'))
    id_grupo_planificacion = Column(Integer, ForeignKey('grupo_planificacion.id_grupo_planificacion'))

    fecha_creacion = Column(DateTime)
    fecha_inicio_limite = Column(DateTime)
    fecha_fin_limite = Column(DateTime)
    fecha_inicio_real = Column(DateTime)
    fecha_fin_real = Column(DateTime)
    fecha_inicio_real_notificaciones = Column(DateTime)
    fecha_fin_real_notificaciones = Column(DateTime)
    liberacion = Column(DateTime)
    autor = Column(String)
    descripcion_orden_trabajo = Column(String)
    posicion_mantenimiento = Column(Double)
    centro_coste_responsable = Column(BigInteger)
    coste_total_real = Column(Double)
    coste_total_plan = Column(Double)
    res_sol_ped = Column(Integer)

    tipo_orden = relationship("TipoOrden", back_populates="ordenes_trabajo")
    prioridad = relationship("Prioridad", back_populates="ordenes_trabajo")
    clase_actividad = relationship("ClaseActividad", back_populates="ordenes_trabajo")
    empresa = relationship("Empresa", back_populates="ordenes_trabajo")
    centro = relationship("Centro", back_populates="ordenes_trabajo")
    linea = relationship("Linea", back_populates="ordenes_trabajo")
    linea_elemento = relationship("LineaElemento", back_populates="ordenes_trabajo")
    puesto_trabajo_responsable = relationship("PuestoTrabajo", back_populates="ordenes_trabajo")
    revision = relationship("Revision", back_populates="ordenes_trabajo")
    equipo = relationship("Equipo", back_populates="ordenes_trabajo")
    grupo_planificacion = relationship("GrupoPlanificacion", back_populates="ordenes_trabajo")

    operaciones = relationship("Operacion", back_populates="orden_trabajo")

class Operacion(Base):
    __tablename__ = 'operacion'

    id_operacion = Column(Integer, primary_key=True, nullable=False)
    id_orden = Column(BigInteger, primary_key=True, nullable=False)
    id_tipo_mano_obra = Column(String, nullable=False)
    id_clave_control = Column(String, nullable=False)
    
    fecha_inicio_limite = Column(Timestamp, nullable=False)
    fecha_fin_limite = Column(Timestamp, nullable=False)
    fecha_inicio_real = Column(Timestamp, nullable=True)
    fecha_fin_real = Column(Timestamp, nullable=True)
    fecha_inicio_real_notificacion = Column(Timestamp, nullable=True)
    fecha_fin_real_notificacion = Column(Timestamp, nullable=True)

    descripcion = Column(String, nullable=False)
    
    tiempo = Column(Double, nullable=False)
    tiempo_real = Column(Double, nullable=False)
    tiempo_real_no_concurrente = Column(Double, nullable=True)
    tiempo_pronostico = Column(Double, nullable=True)
    
    clave_calculo = Column(Integer, nullable=True)
    ce_be = Column(String, nullable=True)
    orden_trabajo = relationship("OrdenTrabajo", back_populates="operaciones")