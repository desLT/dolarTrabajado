#! /usr/bin/env python
# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models


class Perfil(models.Model):
	"""Los valores de sexo lleva la siguiente connotacion:
	0 = mujer, 1 = hombre, 3 = sexodiverso, 4 = Sin especificar"""
	usuario = models.ForeignKey(User, unique=True)
	nombre_completo = models.CharField(max_length=50, default="")
	# ci = models.CharField(max_length="30", default="")
	edad = models.IntegerField(default=0)
	# ubicado_en = models.CharField(max_length=50)  # nacionalidad?
	vacacionando = models.BooleanField(default=False)
	eliminado = models.BooleanField(default=False)
	sexo = models.PositiveSmallIntegerField(blank=True, default=4)
	# foto = models.ImageField()
	# idiomas q habla el usr?

	def __unicode__(self):
		return "%s" % self.usuario


# class DatosExtraPerfil(models.Model):
	# usuario = models.ForeignKey(Perfil, unique=True)
	# codigo_QR = models.CharField(max_length=250)
	# cuenta_paypal = models.CharField(max_length=250)
	# cuenta_mercadopago = models.CharField(max_length=250)

	# def __unicode__(self):
	# 	return "%s" % self.usuario


class Categoria(models.Model):
	padre = models.ForeignKey('self', blank=True, null=True, related_name="hijos")
	nombre = models.CharField(max_length=75)
	url = models.CharField(max_length=75)
	# descripcion = models.CharField(max_length=250)

	def __unicode__(self):
		return "%s" % self.nombre


class CuadroHonor(models.Model):
	"""Este es distinto a valoracion, y contador ya que este guarda una imagen mensual los otros no. Es un historial de los 30 puestos mejor valorados cada mes en una ciudad, estado/provincia/etc y pais. Donde
	0 = atencion, 1 = tiempo de entrega, 2 = calidad del producto, 3 = promedio, 4 = experiencia acumulada//ESTAS NO? 5 = precio justo, 6 = cantidad de medallas"""
	# pais = models.CharField(max_length=50)
	# estado = models.CharField(max_length=50)
	# ciudad = models.CharField(, max_length=50)
	mes = models.PositiveSmallIntegerField()
	anio = models.PositiveSmallIntegerField()
	usuario = models.ForeignKey(Perfil)
	puntaje = models.SmallIntegerField()
	tipo_puntaje = models.SmallIntegerField()

	# class Meta:
	# 	unique_together = ( ('usuario', 'mes', 'anio'), )
	# xDEPURAR:
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

	# def __unicode__(self):
	# 	return "%d" % self.cantidad


class ServicioVirtual(models.Model):
	nombre = models.CharField(max_length=100)
	url = models.CharField(max_length=100)
	descripcion = models.CharField(max_length=250)
	activo = models.BooleanField(default=True)
	contrato = models.TextField()
	eliminado = models.BooleanField(default=False)
	precio = models.SmallIntegerField(default=0)  # max_digits=10)  # , Ddecimal_places=2)
	# archivo = models.FileField()   imagen/video
	subcategoria = models.ForeignKey(Categoria)
	fecha_pub = models.DateTimeField(auto_now_add=True)
	vendedor = models.ForeignKey(Perfil)

	def __unicode__(self):
		return "%s" % self.nombre


class ServicioSatelite(models.Model):
	"""Es un servicio complementario, es decir, que acompaña al servicio principal por un costo extra"""
	servicio = models.ForeignKey(ServicioVirtual)
	descripcion = models.CharField(max_length=250)
	precio = models.SmallIntegerField(default=0)  # max_digits=10)  # , decimal_places=2)
	activo = models.BooleanField(default=True)
	eliminado = models.BooleanField(default=False)

	def __unicode__(self):
		return "%s" % self.descripcion


class Factura(models.Model):
	# xHACER: poner q la id sea una vaina codificada como los codigos de barra y no un int
	comprador = models.ForeignKey(Perfil, related_name='factura_comprador')
	vendedor = models.ForeignKey(Perfil, related_name='factura_vendedor')
	fecha = models.DateTimeField(auto_now_add=True)
	servicio = models.ForeignKey(ServicioVirtual)
	pago = models.PositiveIntegerField()
	contrato = models.TextField()

	def __unicode__(self):
		return "%d" % self.id


class Cola(models.Model):
	ESTADO = (
		(0, "En espera (aunque confirmada la compra)"),
		(1, "Cancelada")
	)
	estatus = models.SmallIntegerField(blank=True, choices=ESTADO, default=0)
	fecha = models.DateTimeField(auto_now_add=True)
	servicio = models.ForeignKey(ServicioVirtual)
	comprador = models.ForeignKey(Perfil, related_name='cola_comprador')
	vendedor = models.ForeignKey(Perfil, related_name='cola_vendedor')
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
	"""Es una copia modificable que va escalando (sumatoria). Cada mes se toma una "foto" promediada para guardar su incremento/decremento en el cuadro de honor"""
	usuario = models.ForeignKey(Perfil)
	servicio = models.ForeignKey(ServicioVirtual)
	experiencia = models.BigIntegerField()
	atencion = models.BigIntegerField()
	calidad = models.BigIntegerField()
	promedio = models.BigIntegerField()
	tiempo_entrega = models.BigIntegerField()

	class Meta:
		unique_together = (('usuario', 'servicio'), )

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
	"""Es una copia de todas las transacciones que hace cada usuario"""
	atencion = models.SmallIntegerField(default=0)
	tiempo_entrega = models.SmallIntegerField(default=0)
	calidad = models.SmallIntegerField(default=0)
	# precio = models.SmallIntegerField(default=0)  # max_digits=10, decimal_places=2, default=0.0)  # DecimalField
	promedio = models.SmallIntegerField(default=0)
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
