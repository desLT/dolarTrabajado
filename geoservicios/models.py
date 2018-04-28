#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.contrib.gis.db import models as gis_models
from django.db import models


# xHACER:
	# Perfil deberia heredar de User?
	# xq quizas conviene usar sus metodos.. is_active, get_fullname, etc
	# o actualizar como se usa User (Abstract....)
class Perfil(models.Model):
	"""Datos geograficos no implican necesariamente que son fuente fidedigna ya que son ingresados por el usr.
Se toman:
		- La ip
		- Sus datos ingresados
		- Lat, Long del gps o navegador

Precision de la ubicacion debe ser menor o igual a 10 y es evaluada asi:

					PAIS	ESTADO		CIUDAD

	User			Vzla	Sucre		Cumana
	IP				Vzla	Sucre		Cumana
	GPS/Navegador	Vzla	Sucre		Cumana
	-------------------------------------------
					3ptos +	3ptos +		3ptos +	1pto(GU) = 10ptos

GU: "Gracias Usuario". Si el usr provee los datos anteriores en su perfil"""
	LISTA = (
		(0, "Mujer"),
		(1, "Hombre"),
		(3, "Sexodiverso"),
		(4, "Elige")
	)
	usuario = models.ForeignKey(User, unique=True)
	nombre_completo = models.CharField(max_length=50, default="")
	# ci = models.CharField(max_length="30", default="")
	edad = models.IntegerField(default=0)
	vacacionando = models.BooleanField(default=False)
	eliminado = models.BooleanField(default=False)
	# xHACER:
		# cada User trae por defecto metodos asociados (is_active, etc)
	sexo = models.PositiveSmallIntegerField(blank=True, default=4, choices=LISTA)
	# foto = models.ImageField()
	# idiomas q habla el usr?
	pais = models.CharField(max_length=100, default="")
	estado = models.CharField(max_length=150, default="")
	ciudad = models.CharField(max_length=150, default="")
	ubicacion = gis_models.PointField(u"longitud/latitud", geography=True, blank=True, null=True)
	precision_ubicacion = models.PositiveSmallIntegerField(default=0)

	gis = gis_models.GeoManager()
	objects = models.Manager()

	def __unicode__(self):
		return "%s" % self.usuario


# class Perfil(models.Model):
# 	LISTA = (
# 		("m", "Mujer"),
# 		("h", "Hombre"),
# 		("s", "Sexodiverso"),
# 		("e", "Elige"),
# 	)
# 	usuario = models.ForeignKey(User, unique=True)
# 	nombre_completo = models.CharField(max_length=50, default="")
# 	edad = models.IntegerField(default=0)
# 	vacacionando = models.BooleanField(default=False)
# 	eliminado = models.BooleanField(default=False)
# 	sexo = models.CharField(max_length=1, blank=True, default=4, choices=LISTA)
# 	pais = models.CharField(max_length=100, default="")
# 	estado = models.CharField(max_length=150, default="")
# 	ciudad = models.CharField(max_length=150, default="")
# 	ubicacion = gis_models.PointField(u"longitud/latitud", geography=True, blank=True, null=True)
# 	precision_ubicacion = models.PositiveSmallIntegerField(default=0)

# 	gis = gis_models.GeoManager()
# 	objects = models.Manager()

# 	def __unicode__(self):
# 		return "%s" % self.usuario






# class BusquedaEficiente(models.Model):
	# """Quizas seria buena idea crear una tabla con menos claves foraneas y menos columnas para que sea mas eficiente la busqueda"""


# class DatosExtraPerfil(models.Model):
	# usuario = models.ForeignKey(Perfil, unique=True)
	# codigo_QR = models.CharField(max_length=250)
	# cuenta_paypal = models.CharField(max_length=250)
	# cuenta_mercadopago = models.CharField(max_length=250)

	# def __unicode__(self):
	# 	return "%s" % self.usuario


class Categoria(models.Model):
	"""(padre y url eran los atributos de la entidad cat cuando era con varios idiomas)"""
	nombre = models.CharField(max_length=75)
	descripcion = models.CharField(max_length=250)
	padre = models.ForeignKey('self', blank=True, null=True, related_name="hijos")
	url = models.CharField(max_length=75)
	
	class Meta:
		unique_together = (("padre", "url"),)

	def __unicode__(self):
		return "%s" % self.nombre


# class TraduccionCategoria(Categoria):
	# # categoria = models.ForeignKey(Categoria)
	# nombre = models.CharField(max_length=75)
	# descripcion = models.CharField(max_length=250)
	# idioma = models.CharField(max_length=5)

	# def __unicode__(self):
	# 	return "%s" % self.nombre


class CuadroHonor(models.Model):
	"""Este es distinto a valoracion, y contador ya que este guarda una imagen mensual los otros no. Es un historial de los 30 puestos mejor valorados cada trimestre/semestre/año en un estado/pais. Donde
	0 = atencion, 1 = tiempo de entrega, 2 = calidad del producto, 3 = promedio, 4 = experiencia acumulada//ESTAS NO? 5 = precio justo, 6 = cantidad de medallas"""
	pais = models.CharField(max_length=50)
	estado = models.CharField(max_length=50)
	fecha = models.DateField()
	usuario = models.ForeignKey(Perfil)
	puntaje = models.PositiveSmallIntegerField()
	tipo_puntaje = models.PositiveSmallIntegerField()

	class Meta:
		unique_together = ( ('usuario', 'fecha'), )
	
	class Meta:
		ordering = ["tipo_puntaje", "-puntaje"]

	def __unicode__(self):
		return "%s" % self.usuario


# class ActividadExtras(models.Model):
	# """Cuantas veces se usa un determinado servicio"""
	# servicio = models.ForeignKey(ServicioSatelite)
	# cantidad = models.BigIntegerField()

	# def __unicode__(self):
		# return "%d" % self.cantidad


# class Visitas(models.Model):
	# usuario = models.ForeignKey(Perfil, unique=True)
	# cantidad = models.BigIntegerField()
	# servicio = models.ForeignKey(ServicioVirtual)
	# pais del visitante

	# def __unicode__(self):
	# 	return "%d" % self.cantidad


class ServicioVirtual(models.Model):
	"""Eliminado existe para no borrar estos datos para las facturas. El maximo valor del precio (PSI field) que toma el precio para Django v1.7 es 32767"""
	nombre = models.CharField(max_length=100)
	url = models.CharField(max_length=100)
	descripcion = models.CharField(max_length=250)
	activo = models.BooleanField(default=True)
	contrato = models.TextField()
	eliminado = models.BooleanField(default=False)
	precio = models.PositiveSmallIntegerField(default=0)  # max_digits=10)  # , Ddecimal_places=2)
	# archivo = models.FileField()   imagen/video
	subcategoria = models.ForeignKey(Categoria)
	fecha_pub = models.DateTimeField(auto_now_add=True)
	vendedor = models.ForeignKey(Perfil)

	class Meta:
		ordering = ["fecha_pub"]

	def __unicode__(self):
		return "%s" % self.nombre


class ServicioSatelite(models.Model):
	"""Es un servicio complementario, es decir, que acompaña al servicio principal por un costo extra. Eliminado existe para no borrar estos datos para las facturas"""
	servicio = models.ForeignKey(ServicioVirtual)
	descripcion = models.CharField(max_length=250)
	precio = models.PositiveSmallIntegerField(default=0)  # max_digits=10)  # , decimal_places=2)
	activo = models.BooleanField(default=True)
	eliminado = models.BooleanField(default=False)

	def __unicode__(self):
		return "%s" % self.descripcion


class Factura(models.Model):
	"""Pago (para Django v1.7) puede manejar hasta 2.147.483.647"""
	# xHACER: poner q la id sea una vaina codificada como los codigos de barra y no un int
	comprador = models.ForeignKey(Perfil)  # , related_name='factura_comprador')
	# vendedor = models.ForeignKey(Perfil, related_name='factura_vendedor')    esto sale de:  servicio__usuario
	fecha = models.DateTimeField(auto_now_add=True)
	servicio = models.ForeignKey(ServicioVirtual)
	pago = models.PositiveIntegerField()
	contrato = models.TextField()

	def __unicode__(self):
		return "%d" % self.id


class Cola(models.Model):
	# xHACER:
		# quizas estado deberian ser todos espera, hasta q salga de la cola, y cancelado seria una operacion q te resta ptos??
	ESTADO = (
		(0, "En espera (vendedor debe aceptar solicitud)"),
		(1, "En espera (aunque confirmada la compra/venta)"),
		(2, "Cancelada")
	)
	estatus = models.PositiveSmallIntegerField(blank=True, choices=ESTADO, default=0)
	fecha = models.DateTimeField(auto_now_add=True)
	servicio = models.ForeignKey(ServicioVirtual)
	comprador = models.ForeignKey(Perfil)  # , related_name='cola_comprador')
	# vendedor = models.ForeignKey(Perfil, related_name='cola_vendedor')  # esto sale de:  servicio__usuario
	contrato = models.TextField()
	# eliminada = models.BooleanField(default=False)

	class Meta:
		ordering = ["fecha"]

	def __unicode__(self):
		return "%s" % self.servicio


# class ExtrasFactura(models.Model):
	# factura = models.ForeignKey(Factura)
	# pago = models.PositiveIntegerField()
	# serv_extra = models.ForeignKey(ServicioSatelite)

	# def __unicode__(self):
		# return "%d" % self.pago


class Contador(models.Model):
	"""Es una copia modificable que va escalando (sumatoria). Cada mes se toma una "foto" promediada para guardar el incremento/decremento del puntaje de un usuario. Esto para calcular posiciones en el cuadro de honor"""
	servicio = models.ForeignKey(ServicioVirtual)
	experiencia = models.BigIntegerField()
	atencion = models.BigIntegerField()
	calidad = models.BigIntegerField()
	promedio = models.BigIntegerField()
	tiempo_entrega = models.BigIntegerField()
	# class Meta:
		# unique_together = (('usuario', 'servicio'), )

	def __unicode__(self):
		return "%s" % self.usuario


class Disponibilidad(models.Model):
	servicio = models.ForeignKey(ServicioVirtual, unique=True)
	contador = models.PositiveSmallIntegerField(default=0)
	maximo = models.PositiveSmallIntegerField(default=1)
	num_dias = models.PositiveSmallIntegerField(default=7)

	def __unicode__(self):
		return "%d" % self.contador


class Valoracion(models.Model):
	"""Es la reseña de cada transaccion que hace cada usuario"""
	atencion = models.PositiveSmallIntegerField(default=0)
	tiempo_entrega = models.PositiveSmallIntegerField(default=0)
	calidad = models.PositiveSmallIntegerField(default=0)
	# precio = models.SmallIntegerField(default=0)  # max_digits=10, decimal_places=2, default=0.0)  # DecimalField
	promedio = models.PositiveSmallIntegerField(default=0)
	estafa = models.BooleanField(default=False)
	eliminada = models.BooleanField(default=False)
	servicio = models.ForeignKey(ServicioVirtual)

	class Meta:
		ordering = ["-promedio"]

	def __unicode__(self):
		return "%d" % self.promedio


class Sugerencia(models.Model):
	texto = models.TextField()
	asunto = models.CharField(max_length=150)
	usuario = models.ForeignKey(Perfil)

	def __unicode__(self):
		return "%s" % self.asunto
