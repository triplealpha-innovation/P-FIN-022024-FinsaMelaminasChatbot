from db.database import Base

from sqlalchemy import ForeignKey, Column, Integer, String, DateTime, BigInteger, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

# Definición de modelos

class Centro(Base):
    __tablename__ = 'centro'
    
    id_centro = Column(Integer, primary_key=True)
    descripcion = Column(String)
    
    ordenes = relationship("OrdenTrabajo", backref="centro")
    equipos = relationship("Equipo", backref="centro")


class ClaseActividad(Base):
    __tablename__ = 'clase_actividad'
    
    id_clase_actividad = Column(String, primary_key=True)
    descripcion = Column(String)
    
    ordenes_trabajo = relationship("OrdenTrabajo", backref="clase_actividad")


class ClaveControl(Base):
    __tablename__ = 'clave_control'
    
    id_clave_control = Column(String, primary_key=True)
    descripcion = Column(String)
    
    operaciones = relationship("Operacion", backref="clave_control")


class CodigoEstado(Base):
    __tablename__ = 'codigo_estado'
    
    id_codigo = Column(String, primary_key=True)
    descripcion = Column(String)
    
    status_usuario_ot = relationship("StatusUsuario", backref="codigo_estado_ot")
    status_sistema_ot = relationship("StatusSistemaOrden", backref="codigo_estado_sistema_ot")
    status_sistema_operacion = relationship("StatusSistemaOperacion", backref="codigo_estado_sistema_operacion")
    status_sistema_equipo = relationship("StatusSistemaEquipo", backref="codigo_estado_sistema_equipo")


class Componente(Base):
    __tablename__ = 'componente'
    
    id_componente = Column(String, primary_key=True)
    descripcion = Column(String, nullable=True)
    
    equipo_componentes = relationship("EquipoComponente", backref="componente")


class Empresa(Base):
    __tablename__ = 'empresa'
    
    id_empresa = Column(Integer, primary_key=True)
    descripcion = Column(String)
    
    ordenes = relationship("OrdenTrabajo", backref="empresa")
    equipos = relationship("Equipo", backref="empresa")


class Equipo(Base):
    __tablename__ = 'equipo'
    
    id_equipo = Column(String, primary_key=True)
    id_tipo_equipo = Column(String, ForeignKey('tipo_equipo.id_tipo_equipo'))
    id_empresa = Column(Integer, ForeignKey('empresa.id_empresa'))
    id_centro = Column(Integer, ForeignKey('centro.id_centro'))
    id_linea = Column(Integer, ForeignKey('linea.id_linea'))
    id_elemento_linea = Column(Integer, ForeignKey('linea_elemento.id_elemento_linea', nullable=True))
    descripcion = Column(String)
    equipo_superior = Column(String, nullable=True)
    valido_desde = Column(DateTime)
    fabricante = Column(String, nullable=True)
    emplazamiento_imputacion = Column(BigInteger)
    
    tipo_equipo = relationship("TipoEquipo", backref="equipos")
    empresa = relationship("Empresa", backref="equipos")
    centro = relationship("Centro", backref="equipos")
    linea = relationship("Linea", backref="equipos")
    elemento_linea = relationship("LineaElemento", backref="equipos")
    orden_trabajo = relationship("OrdenTrabajo", backref="equipo")
    equipos_componente = relationship("EquipoComponente", backref="equipo")
    status_sistema_equipo = relationship("StatusSistemaEquipo", backref="equipo")


class EquipoComponente(Base):
    __tablename__ = 'equipo_componente'
    
    id_equipo = Column(String, ForeignKey('equipo.id_equipo'), primary_key=True)
    id_componente = Column(String, ForeignKey('componente.id_componente'), primary_key=True)
    cantidad = Column(Integer)
    
    equipo = relationship("Equipo", backref="equipo_componente")
    componente = relationship("Componente", backref="equipo_componente")


class CosteOrdenTrabajo(Base):
    __tablename__ = 'coste_orden_trabajo'
    
    id_orden = Column(BigInteger, ForeignKey('orden_trabajo.id_orden'), primary_key=True)
    id_tipo_coste = Column(String, ForeignKey('tipo_coste.id_tipo_coste'), primary_key=True)
    importe_plan = Column(Float)
    importe_real = Column(Float)
    
    tipo_coste = relationship("TipoCoste", backref="coste_orden_trabajo")
    orden_trabajo = relationship("OrdenTrabajo", backref="coste_orden_trabajo")


class Fallo(Base):
    __tablename__ = 'fallo'
    
    id_orden = Column(BigInteger, ForeignKey('orden_trabajo.id_orden'), primary_key=True)
    id_tipo_fallo = Column(String, ForeignKey('tipo_fallo.id_tipo_fallo'), primary_key=True)
    
    orden_trabajo = relationship("OrdenTrabajo", backref="fallo")
    tipo_fallo = relationship("TipoFallo", backref="fallo")


class GrupoPlanificacion(Base):
    __tablename__ = 'grupo_planificacion'
    
    id_grupo_planificacion = Column(String, primary_key=True)
    descripcion = Column(String)
    
    ordenes_trabajo = relationship("OrdenTrabajo", backref="grupo_planificacion")


class Linea(Base):
    __tablename__ = 'linea'
    
    id_linea = Column(Integer, primary_key=True)
    descripcion = Column(String)
    descripcion_abreviada = Column(String, nullable=True)
    
    ordenes_trabajo = relationship("OrdenTrabajo", backref="linea")
    equipos = relationship("Equipo", backref="linea")


class LineaElemento(Base):
    __tablename__ = 'linea_elemento'
    
    id_elemento_linea = Column(Integer, primary_key=True)
    descripcion = Column(String)
    
    ordenes_trabajo = relationship("OrdenTrabajo", backref="linea_elemento")
    equipos = relationship("Equipo", backref="linea_elemento")


class ManoObraNotificada(Base):
    __tablename__ = 'mano_obra_notificada'
    
    id_orden = Column(BigInteger, ForeignKey('orden_trabajo.id_orden'), primary_key=True)
    id_operacion = Column(Integer, ForeignKey('operacion.id_operacion'), primary_key=True)
    id_operario = Column(BigInteger, ForeignKey('operario.id_operario', nullable=True))
    id_proveedor = Column(BigInteger, ForeignKey('proveedor.id_proveedor', nullable=True))
    id_proveedor_facturacion = Column(BigInteger, ForeignKey('proveedor.id_proveedor', nullable=True))
    fecha_inicio = Column(DateTime)
    fecha_fin = Column(DateTime)
    tiempo = Column(Float)
    descripcion = Column(String, nullable=True)
    grua = Column(String, nullable=True)
    matricula = Column(String, nullable=True)
    documento_compras = Column(BigInteger, nullable=True)
    posicion = Column(Integer)
    
    operacion = relationship("Operacion", backref="mano_obra_notificada")
    operario = relationship("Operario", backref="mano_obra_notificada")
    proveedor = relationship("Proveedor", backref="mano_obra_notificada", foreign_keys=[id_proveedor])
    proveedor_facturacion = relationship("Proveedor", backref="mano_obra_notificada_facturacion", foreign_keys=[id_proveedor_facturacion])


class OrdenTrabajo(Base):
    __tablename__ = 'orden_trabajo'

    id_orden = Column(BigInteger, primary_key=True)
    id_tipo_orden = Column(String, ForeignKey('tipo_orden.id_tipo_orden'))
    id_prioridad = Column(Integer, ForeignKey('prioridad.id_prioridad'))
    id_clase_actividad = Column(String, ForeignKey('clase_actividad.id_clase_actividad'))
    id_empresa = Column(Integer, ForeignKey('empresa.id_empresa'))
    id_centro = Column(Integer, ForeignKey('centro.id_centro'))
    id_linea = Column(Integer, ForeignKey('linea.id_linea'))
    id_elemento_linea = Column(Integer, ForeignKey('linea_elemento.id_elemento_linea', nullable=True))
    id_grupo_planificacion = Column(String, ForeignKey('grupo_planificacion.id_grupo_planificacion'))
    id_puesto_trabajo_responsable = Column(String, ForeignKey('puesto_trabajo.id_puesto_trabajo'))
    id_revision = Column(String, ForeignKey('revision.id_revision', nullable=True))
    id_equipo = Column(String, ForeignKey('equipo.id_equipo', nullable=True))
    fecha_creacion = Column(DateTime)
    fecha_inicio_real = Column(DateTime, nullable=True)
    fecha_fin_real = Column(DateTime, nullable=True)
    fecha_inicio_real_notificaciones = Column(DateTime, nullable=True)
    fecha_fin_real_notificaciones = Column(DateTime, nullable=True)
    liberacion = Column(DateTime, nullable=True)
    autor = Column(String)
    descripcion = Column(String)
    posicion_mantenimiento = Column(Float, nullable=True)
    
    tipo_orden = relationship("TipoOrden", backref="ordenes")
    prioridad = relationship("Prioridad", backref="ordenes")
    clase_actividad = relationship("ClaseActividad", backref="ordenes")
    empresa = relationship("Empresa", backref="ordenes")
    centro = relationship("Centro", backref="ordenes")
    linea = relationship("Linea", backref="ordenes")
    elemento_linea = relationship("LineaElemento", backref="ordenes")
    grupo_planificacion = relationship("GrupoPlanificacion", backref="ordenes")
    puesto_trabajo_responsable = relationship("PuestoTrabajo", backref="ordenes")
    revision = relationship("Revision", backref="ordenes")
    equipo = relationship("Equipo", backref="ordenes")
    
    operaciones = relationship("Operacion", backref="orden_trabajo")
    status_sistema = relationship("StatusSistemaOrden", backref="orden_trabajo")
    status_usuario = relationship("StatusUsuario", backref="orden_trabajo")
    paradas = relationship("Parada", backref="orden_trabajo")
    coste_orden_trabajo = relationship("CosteOrdenTrabajo", backref="orden_trabajo")
    fallo = relationship("Fallo", backref="orden_trabajo")


class Operacion(Base):
    __tablename__ = 'operacion'

    id_operacion = Column(Integer, primary_key=True)
    id_orden = Column(BigInteger, ForeignKey('orden_trabajo.id_orden'))
    id_tipo_mano_obra = Column(String, ForeignKey('tipo_mano_obra.id_tipo_mano_obra', nullable=True))
    id_clave_control = Column(String, ForeignKey('clave_control.id_clave_control'))
    fecha_inicio_real = Column(DateTime, nullable=True)
    fecha_fin_real = Column(DateTime, nullable=True)
    fecha_inicio_real_notificaciones = Column(DateTime, nullable=True)
    fecha_fin_real_notificaciones = Column(DateTime, nullable=True)
    descripcion = Column(String, nullable=True)
    tiempo = Column(Float)
    tiempo_real = Column(Float)
    
    orden_trabajo = relationship("OrdenTrabajo", backref="operaciones")
    tipo_mano_obra = relationship("TipoManoObra", backref="operaciones")
    clave_control = relationship("ClaveControl", backref="operaciones")
    
    status_sistema_operacion = relationship("StatusSistemaOperacion", backref="operacion")
    mano_obra_notificada = relationship("ManoObraNotificada", backref="operacion")


class Operario(Base):
    __tablename__ = 'operario'

    id_operario = Column(BigInteger, primary_key=True)
    nombre = Column(String)
    nif = Column(String)
    
    mano_obra_notificada = relationship("ManoObraNotificada", backref="operario")


class Prioridad(Base):
    __tablename__ = 'prioridad'

    id_prioridad = Column(Integer, primary_key=True)
    descripcion = Column(String)
    
    ordenes = relationship("OrdenTrabajo", backref="prioridad")


class ProveedorManoObra(Base):
    __tablename__ = 'proveedor_mano_obra'

    id_proveedor = Column(BigInteger, primary_key=True)
    nombre = Column(String)
    
    mano_obra_notificada = relationship("ManoObraNotificada", backref="proveedor")
    mano_obra_notificada_facturacion = relationship("ManoObraNotificada", backref="proveedor_facturacion")


class PuestoTrabajo(Base):
    __tablename__ = 'puesto_trabajo'

    id_puesto_trabajo = Column(String, primary_key=True)
    descripcion = Column(String)
    
    ordenes = relationship("OrdenTrabajo", backref="puesto_trabajo")


class Revision(Base):
    __tablename__ = 'revision'

    id_revision = Column(String, primary_key=True)
    descripcion = Column(String, nullable=True)
    
    ordenes = relationship("OrdenTrabajo", backref="revision")


class StatusSistemaOrden(Base):
    __tablename__ = 'status_sistema_orden'

    id_orden = Column(BigInteger, ForeignKey('orden_trabajo.id_orden'), primary_key=True)
    id_codigo = Column(String, ForeignKey('codigo_estado.id_codigo'))
    
    orden_trabajo = relationship("OrdenTrabajo", backref="status_sistema")
    codigo_estado = relationship("CodigoEstado", backref="status_sistema_orden")


class StatusSistemaOperacion(Base):
    __tablename__ = 'status_sistema_operacion'

    id_orden = Column(BigInteger, ForeignKey('orden_trabajo.id_orden'), primary_key=True)
    id_operacion = Column(Integer, ForeignKey('operacion.id_operacion'), primary_key=True)
    id_codigo = Column(String, ForeignKey('codigo_estado.id_codigo'))
    
    operacion = relationship("Operacion", backref="status_sistema_operacion")
    codigo_estado = relationship("CodigoEstado", backref="status_sistema_operacion")


class StatusSistemaEquipo(Base):
    __tablename__ = 'status_sistema_equipo'

    id_equipo = Column(String, ForeignKey('equipo.id_equipo'), primary_key=True)
    id_codigo = Column(String, ForeignKey('codigo_estado.id_codigo'))
    
    equipo = relationship("Equipo", backref="status_sistema_equipo")
    codigo_estado = relationship("CodigoEstado", backref="status_sistema_equipo")


class StatusUsuario(Base):
    __tablename__ = 'status_usuario'

    id_orden = Column(BigInteger, ForeignKey('orden_trabajo.id_orden'), primary_key=True)
    id_codigo = Column(String, ForeignKey('codigo_estado.id_codigo'))
    
    orden_trabajo = relationship("OrdenTrabajo", backref="status_usuario")
    codigo_usuario = relationship("CodigoEstado", backref="status_usuario")


class TipoEquipo(Base):
    __tablename__ = 'tipo_equipo'

    id_tipo_equipo = Column(String, primary_key=True)
    descripcion = Column(String)
    
    equipos = relationship("Equipo", backref="tipo_equipo")


class TipoCoste(Base):
    __tablename__ = 'tipo_coste'

    id_tipo_coste = Column(String, primary_key=True)
    descripcion = Column(String)
    
    coste_orden_trabajo = relationship("CosteOrdenTrabajo", backref="tipo_coste")


class TipoFallo(Base):
    __tablename__ = 'tipo_fallo'

    id_tipo_fallo = Column(String, primary_key=True)
    descripcion = Column(String)
    patron = Column(String)
    
    fallo = relationship("Fallo", backref="tipo_fallo")


class TipoManoObra(Base):
    __tablename__ = 'tipo_mano_obra'

    id_tipo_mano_obra = Column(String, primary_key=True)
    descripcion = Column(String)
    
    operaciones = relationship("Operacion", backref="tipo_mano_obra")


class TipoOrden(Base):
    __tablename__ = 'tipo_orden'

    id_tipo_orden = Column(String, primary_key=True)
    descripcion = Column(String)
    
    ordenes = relationship("OrdenTrabajo", backref="tipo_orden")
