class Medalla(models.Model):
	"""Premio por obtener medalla donde,  tipo_premio:
	0 = precio maximo, 1 = precio maximo de servicio complementario, 2 = cantidad de servicios complementarios, 3 = cantidad de serv simultaneos.
	Ejm:
	--Medalla amarillo, permite ganar hasta 500 Bs al completar 10 transacciones y estar activo en el sitio por 30 dias, 500, 0, 10
	--Medalla roja, permite ganar hasta 20 por cada serv complementario al alcanzar 40 transacciones en 3 meses, 20 , 1, 40
	--Medalla azul, permite ofertar hasta 2 serv complementarios al alcanzar 20 transacciones en 3 meses, 2 , 2, 20
	--Medalla verde, permite aceptar hasta 4 serv complementarios al alcanzar 30 transacciones en 3 meses, 4 , 3, 30"""
	nombre = models.CharField(max_length=75)
	# imagen = models.ImageField()
	descripcion = models.CharField(max_length=250)
	ptos_premio = models.PositiveSmallIntegerField()  # puntos a obsequiar
	tipo_premio = models.PositiveSmallIntegerField()
	requisito_ptos = models.PositiveIntegerField()  # lo q necesitas para obtener medalla

	def __unicode__(self):
		return "%s" % self.nombre



class Premiado(models.Model):
	"""Cada usuario solo puede tener un premio unico en su tipo. Ejm:  Luis solo tiene una medalla que le permite elevar el precio del servicio"""
	medalla = models.ForeignKey(Medalla)
	usuario = models.ForeignKey(Perfil)

	class Meta:
		unique_together = ( ('usuario', 'medalla'), )

	def __unicode__(self):
		return "%s" % self.usuario


class HistorialMedallas(models.Model):
	"""Algunas medallas habra que reemplazarlas por una nueva ya q su premio se superpone sobre un premio anterior. Ejm:  Si puedes hacer 2 servicios, no tiene sentido tener otra que otorgue 4 al lado de la que otorga 2. Esas medallas viejas entran en este historial"""
	usuario = models.ForeignKey(Perfil)
	medalla = models.ForeignKey(Medalla)

	def __unicode__(self):
		return "%s" % self.medalla


class Regalo(models.Model):
	# xHACER:  sera q le pongo fecha para saber cuando fue q le dieron los ptos, entonces tendria q sumar todos los registros donde existe usr y este no seria unique
	# para save necesito saber cuantos ptos le da el regalo y a q usr
	# el regalo se otorga todos los 1ero de cada mes
	usuario = models.ForeignKey(Perfil, unique=True)
	puntos = models.PositiveIntegerField()
	veces = models.PositiveIntegerField()

	def __unicode__(self):
		return "%s" % self.usuario


# -----------------------------------------------------------------------------------------

# <div class="titulo">
# 	<h2><a href="#" title="Ver m&aacute;s">M&aacute;s Creativos <i class="glyphicon glyphicon-chevron-right mas"></i></a></h2>
# </div>
# <div class="row">
# 	<div class="col-md-3 caja-serv">
# 		<div class="cara-secundaria">
# 			<p class="usuario"><a href="/perfil/{{ perfil.usuario }}"><i class="glyphicon glyphicon-user"></i>  @{{ perfil.usuario }}</a></p>
# 			<a class="enlace-serv" href="/categoria/{{ categoria }}/{{ subcategoria }}/{{ geoserv }}/">
# 				<p class="datos-extra">
# 					<span class="titulo-extras">Promedio:</span><span><i class="glyphicon glyphicon-star color-oro"></i> +199k / +199k</span>
# 					<span class="titulo-extras">Experiencia:</span><span><i class="glyphicon glyphicon-bookmark color-oro"></i> +99k</span>
# 					<span class="vermas"><i class="glyphicon glyphicon-chevron-right" style=""></i></span>
# 				</p>
# 			</a>
# 		</div>
# 	 	<div class="cara-principal">
# 			<img src="{{ STATIC_URL }}images/falta.png" width="215" height="130" alt="1.000 Me Gusta para tu post, foto o video en Facebook">
# 	 		<!-- <img data-src="holder.js/300x200" alt="..."> -->
# 		 	<div class="dir-serv">
# 				<div class="row">
# 					<h2 class="col-xs-9 nomb-serv">1.000 Me Gusta para tu post, foto o video en Faceb1.000 Me Gusta para tu po</h2>
# 					<div class="col-xs-3 text-center precio"><div>Bs</div>55.555</div>
# 				</div>
# 	      		</div>
# 		</div>
# 	</div>
# </div>


ESTADISTICAS
<li><a href="#">COMPRADOR</a></li>
<li><a href="#">2 medallas</a></li>
