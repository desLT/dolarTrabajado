#! /usr/bin/env python
# -*- coding: utf-8 -*-

from geoservicios.models import *
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from datetime import datetime  # , date
import re

# xDEPURAR:
ANIO_INICIO_CH = 2014  # CH: cuadro de honor


def uerelizar(cad):  # que tiene forma de URL
	return cad.replace(" ", "-").replace(u"ñ", "n").replace(u"á", "a").replace(u"é", "e").replace(u"í", "i").replace(u"ó", "o").replace(u"ú", "u").lower()


def inicio(request):
	nuevos_geos = ServicioVirtual.objects.all()[:8]
	lista_servis = Valoracion.objects.all()[:8]

	if request.user.is_authenticated():
		u = request.user
		u = get_object_or_404(Perfil, usuario=u)

		return render_to_response('index.html', {
			'perfil': u,
			'perfil_logueado': u,
			'logueado': True,
			'nuevos_geos': nuevos_geos,
			'servicios_valorados': lista_servis,
		}, RequestContext(request))
	else:
		return render_to_response('index.html', {
			'nuevos_geos': nuevos_geos,
			'servicios_valorados': lista_servis,
		}, RequestContext(request))


def sesionar_usr(request):
	if request.user.is_authenticated():
		return HttpResponseRedirect(reverse('geoservicios.views.inicio'))
	else:
		try:
			# xHACER: Post deberia estar sin filtrar?
			usuario = authenticate(username = request.POST['usuario'], password = request.POST['pw'])
		except KeyError:
			return render_to_response('index.html', {
					'mensaje': 'Rellene todos los campos',
				}, RequestContext(request))
		if usuario is not None:
			if usuario.is_active:
				login(request, usuario)
			else:
				return render_to_response('index.html', {
					'mensaje': 'El usuario ha sido eliminado',
				}, RequestContext(request))
		else:
			return render_to_response('index.html', {
				'mensaje': 'Ingrese los datos correctamente',
			}, RequestContext(request))
		return HttpResponseRedirect(reverse('geoservicios.views.perfil', args=[usuario]))


def cerrar_sesion(request):
	logout(request)
	return HttpResponseRedirect(reverse('geoservicios.views.inicio'))


def sugerir(request):
	if request.user.is_authenticated():
		usr = request.user
		usr = Perfil.objects.get(usuario=usr)
		asunto = request.POST['asunto']
		txt = request.POST['txt']
		# xHACER:  deberia validar q no sean chimbos los datos
		Sugerencia.objects.create(texto=txt, asunto= asunto, usuario=usr)
	return HttpResponseRedirect(reverse('geoservicios.views.inicio'))


# xHACER:  validar q no pasa nada si hago sql-injection
def registrar_usr(request):
	try:
		if not re.match('^[a-zA-Z0-9_]+$', request.POST['usuario']):
			return render_to_response('index.html', {
				'mensaje': 'El nombre de usuario solo puede contener letras, numeros y _'
				}, RequestContext(request))
		if not re.match('^[a-zA-Z][a-zA-Z0-9_]*[@][a-zA-Z0-9_.]+[.][a-zA-Z0-9_]+$', request.POST['correo']):
			return render_to_response('index.html', {
				'mensaje': 'Ingrese un correo valido'
				}, RequestContext(request))

		usr = request.POST['usuario'].lower()
		if User.objects.filter(username__iexact = usr):
			return render_to_response('index.html', {
				'mensaje': 'El usuario ya existe'
				}, RequestContext(request))
		u = User.objects.create_user(
			usr,
			request.POST['correo'],
			request.POST['pw'],
		)
		u.first_name = ''
		u.last_name = ''
		u.save()

		p = Perfil.objects.create(
			usuario = u,
			# ubicado_en = '',
		)
		p.save()
		usr = authenticate(username = usr, password = request.POST['pw'])
		login(request, usr)
		return HttpResponseRedirect(reverse('geoservicios.views.perfil', args=[usr]))
	except KeyError:
		return render_to_response('index.html', {
			'mensaje': 'Rellene todos los campos'
			}, RequestContext(request))


def ver_cuadro_honor(request):  # , mes, anio):
	"""Muestra el cuadro de honor y sus respectivos valores y usuarios"""
	# xHACER:
		# -- seria bueno un calendario o una busqueda para
		# ubicar un usr q estuvo en el cuadro hace time
		# -- q le puedas suministrar el año y mes
		# if (mes >= 1) and (mes <= m and anio <= a) and (anio >= ANIO_INICIO_CH):
		# ch = CuadroHonor.objects.filter(mes=m, anio=a)
		# else:
		# 	error fecha invalida
	ahorita = datetime.now()
	fecha = datetime.date(ahorita)
	m = fecha.month
	a = fecha.year
	lista_atencion = []
	lista_tiempo_entrega = []
	lista_calidad = []
	lista_promedio = []
	lista_experiencia = []
	q = CuadroHonor.objects.filter(tipo_puntaje=0, mes=m, anio=a)
	for l in q:
		lista_atencion.append([l.puntaje, l.usuario])

	q = CuadroHonor.objects.filter(tipo_puntaje=1, mes=m, anio=a)
	for l in q:
		lista_tiempo_entrega.append([l.puntaje, l.usuario])

	q = CuadroHonor.objects.filter(tipo_puntaje=2, mes=m, anio=a)
	for l in q:
		lista_calidad.append([l.puntaje, l.usuario])

	q = CuadroHonor.objects.filter(tipo_puntaje=3, mes=m, anio=a)
	for l in q:
		lista_promedio.append([l.puntaje, l.usuario])

	q = CuadroHonor.objects.filter(tipo_puntaje=4, mes=m, anio=a)
	for l in q:
		lista_experiencia.append([l.puntaje, l.usuario])

	# xHACER: cambiar None este por algo mas elegante
	usr = None
	if request.user.is_authenticated():
		usr = request.user
		usr = get_object_or_404(Perfil, usuario__username = usr)

	return render_to_response('cuadroHonor.html', {
		'perfil': usr if usr else None,
		'perfil_logueado': usr if usr else None,
		'logueado': True if usr else None,
		'lista_atencion': lista_atencion,
		'lista_tiempo_entrega': lista_tiempo_entrega,
		'lista_calidad': lista_calidad,
		'lista_promedio': lista_promedio,
		'lista_experiencia': lista_experiencia,
		}, RequestContext(request))


def crear_cuadro_honor():
	"""Crea un cuadro el primero de cada mes"""
	# xHACER:  crear un trigger q corra en django independientemente de su backend
	ahorita = datetime.now()
	fecha = datetime.date(ahorita)
	anio = fecha.year
	dia = fecha.day
	mes = fecha.month
	if dia == 1 and anio >= ANIO_INICIO_CH:  # (mes >= 1 and mes <= 12)
		try:
			atencion = Contador.objects.all().order_by("-atencion")[5]
			te = Contador.objects.all().order_by("-tiempo_entrega")[5]
			calidad = Contador.objects.all().order_by("-calidad")[5]
			promedio = Contador.objects.all.order_by("-promedio")[5]
			exp = Contador.objects.all.order_by("-experiencia")[5]

			for n in range(len(atencion)):
				CuadroHonor.objects.create(mes=mes, anio= anio, usuario=atencion[n].usuario, puntaje=atencion[n].atencion, tipo_puntaje=0)
			for n in range(len(te)):
				CuadroHonor.objects.create(mes=mes, anio= anio, usuario=te[n].usuario, puntaje=te[n].tiempo_entrega, tipo_puntaje=1)
			for n in range(len(calidad)):
				CuadroHonor.objects.create(mes=mes, anio= anio, usuario=calidad[n].usuario, puntaje=calidad[n].calidad, tipo_puntaje=2)
			for n in range(len(promedio)):
				CuadroHonor.objects.create(mes=mes, anio= anio, usuario=promedio[n].usuario, puntaje=promedio[n].promedio, tipo_puntaje=3)
			for n in range(len(exp)):
				CuadroHonor.objects.create(mes=mes, anio= anio, usuario=exp[n].usuario, puntaje=exp[n].experiencia, tipo_puntaje=4)
		except:
			return "Hubo un error"

		return u"Proceso de generación de valores exitoso!"
	else:
		return "Hubo un error de fecha"


def ver_categoria(request, cat):
	# xHACER:  usar un paginador, validar cat, usar el promedio para ordenar las cat
	cat = get_object_or_404(Categoria, url=cat)
	subcats = Categoria.objects.filter(padre=cat)
	servs = ServicioVirtual.objects.filter(activo=True, subcategoria__in=subcats)[:20]
	if request.user.is_authenticated():
		usr = request.user
		p = get_object_or_404(Perfil, usuario=usr)
		return render_to_response('categoria.html', {
			'perfil': p,
			'perfil_logueado': p,
			'logueado': True,
			'categoria': cat,
			'servicios': servs,
			'subcategorias': subcats,
		}, RequestContext(request))
	else:
		return render_to_response('categoria.html', {
			'servicios': servs,
			'categoria': cat,
			'subcategorias': subcats,
		}, RequestContext(request))


def ver_subcategoria(request, cat, subcat):
	# xHACER:  usar un paginador, limpiar subcat
	cat = get_object_or_404(Categoria, url=cat)
	subcategorias = Categoria.objects.filter(padre=cat)
	subcat = get_object_or_404(Categoria, url=subcat, padre=cat)
	servs = ServicioVirtual.objects.filter(activo=True, subcategoria=subcat)[:20]

	if request.user.is_authenticated():
		usr = request.user
		p = get_object_or_404(Perfil, usuario=usr)
		return render_to_response('categoria.html', {
			'perfil': p,
			'perfil_logueado': p,
			'logueado': True,
			'categoria': cat,
			'servicios': servs,
			'subcategorias': subcategorias,
			'nomb_subcategoria': subcat,
		}, RequestContext(request))
	else:
		return render_to_response('categoria.html', {
			'servicios': servs,
			'categoria': cat,
			'subcategorias': subcategorias,
			'nomb_subcategoria': subcat,
		}, RequestContext(request))


def ver_servicio(request, cat, serv):
	# xHACER:  usar un paginador, limpiar subcat
	# debe estar activo por si alguien lo save en favs y lo usa cuando este eliminado
	cat = get_object_or_404(Categoria, url=cat)
	serv = get_object_or_404(ServicioVirtual, url=serv)
	try:
		val = Contador.objects.get(servicio=serv)
		te = val.tiempo_entrega/val.experiencia
		exp = val.experiencia
		atencion = val.atencion/val.experiencia
		calidad = val.calidad/val.experiencia
	except:
		te, exp, atencion, calidad = 0, 0, 0, 0

	contrato = serv.contrato.split("<br>")
	extras = ServicioSatelite.objects.filter(servicio=serv)
	if request.user.is_authenticated():
		usr = request.user
		p = get_object_or_404(Perfil, usuario=usr)
		return render_to_response('servicio.html', {
			'perfil': p,
			'logueado': True,
			'perfil_logueado': p,
			'servicio': serv,
			'contrato': contrato,
			'exp': exp,
			'te': te,
			'servs_satelite': extras,
			'calidad': calidad,
			'atencion': atencion,
			'categoria': cat,
		}, RequestContext(request))
	else:
		return render_to_response('servicio.html', {
			'exp': val.experiencia,
			'te': val.tiempo_entrega,
			'calidad': val.calidad,
			'atencion': val.atencion,
			'servicio': serv,
			'contrato': contrato,
			'categoria': cat,
		}, RequestContext(request))


def perfil(request, usr):
	# xHACER:  tiempo estimado de entrega por cada servicio, x semana
	# numero de impresiones de anuncios en las busquedas
	# cant de usuarios atendidos por servicio
	# cant de servicios mutualmente rechazados
	usr = get_object_or_404(User, username=usr)
	perfil = get_object_or_404(Perfil, usuario=usr)
	servis = ServicioVirtual.objects.filter(vendedor=perfil)
	cant_servicios = servis.count()
	facturas = Factura.objects.filter(vendedor=perfil)
	n_facturas = facturas.count()
	lista_servis = []
	# visitas = Visitas.objects.filter(usuario=perfil).count()

	ganancias = 0
	try:
		for s in servis:
			c = Cola.objects.filter(servicio=s)
			pedidos = c.filter(estatus=0).count()
			cancelados = c.filter(estatus=1).count()
			facturados = Factura.objects.filter(servicio=s).count()
			lista_servis.append([ s, pedidos, facturados, cancelados ])

		for f in facturas:
			ganancias += f.pago
		valores = Contador.objects.get(usuario=perfil)
		prom = valores.promedio/valores.experiencia
		te = valores.tiempo_entrega/valores.experiencia
		exp = valores.experiencia
		atencion = valores.atencion/valores.experiencia
		calidad = valores.calidad/valores.experiencia
	except:
		prom, te, exp, atencion, calidad = 0, 0, 0, 0, 0

	categorias = []
	lista_subcat = []
	lista = Categoria.objects.filter(padre=None)
	for i, cat in enumerate(lista):
		categorias.append(cat)
		sublista = Categoria.objects.filter(padre=cat)
		lista_subcat.append([i, sublista])

	# u_extras = get_object_or_404(DatosExtraPerfil, usuario__iexact=usuario)
	datos = {
		'vacacionando': "Vacacionando" if perfil.vacacionando else "Trabajando",
		'prom': prom,
		'tiempo_entrega': te,
		'perfil': perfil,
		'atencion': atencion,
		'calidad': calidad,
		'exp': exp,
		'categorias': categorias,
		'lista_subcat': lista_subcat,
		'ganancias': ganancias,
		'lista_servis': lista_servis,
		'n_servicios': cant_servicios,
		'n_compradores': n_facturas,
		# 'visitas': visitas,
		# 'n_servicios_progreso': x_comprar,
		# 'n_servicios_cancelados': cancelada,
	}
	if request.user.is_authenticated():
		u = get_object_or_404(User, username = request.user)
		datos['logueado'] = True
		if usr != u:
			p = get_object_or_404(Perfil, usuario = u)
			datos['perfil_logueado'] = p
		else:
			datos['perfil_propio'] = True
	return render_to_response('perfil.html', datos, RequestContext(request))


def crear_servicio(request):
	if request.user.is_authenticated():
		# xDEPURAR:  crear un servicio fisico??
		usr = request.user
		p = Perfil.objects.get(usuario=usr)
		# xHACER:
			# si añade una categoria como tratarla?
			# limpiar todos los datos de entrada
		nomb = request.POST['nomb']
		url = uerelizar(nomb)
		precio = int(request.POST['precio'])
		descrip = request.POST['descrip']
		cont = ""
		n_clausulas = int(request.POST['Nclausulas'])+1
		for k in range(n_clausulas):
			n = 'clausula-'+str(k)
			cont += request.POST[n] + "<br>"
		cont = cont[: len(cont)-4 ]
		id_subc = int(request.POST['subc'])
		id_cat = int(request.POST['subcategoria'])
		cat = Categoria.objects.filter(padre=None)[id_cat]
		subc = Categoria.objects.filter(padre=cat)[id_subc]

		s = ServicioVirtual.objects.create(nombre=nomb, url=url, descripcion=descrip, contrato=cont, precio=precio, subcategoria=subc, vendedor=p)
		Contador.objects.create(usuario=p, servicio=s, experiencia=0, atencion=0, calidad=0, promedio=0, tiempo_entrega=0)

		return HttpResponseRedirect(reverse('geoservicios.views.perfil', args=[usr]))
	else:
		return HttpResponseRedirect(reverse('geoservicios.views.inicio'))


def crear_complemento_servicio(request, servicio):
	"""este debe permanecer individual xq deberia ser capaz de procesar N numero de servicios extras"""
	if request.user.is_authenticated():
		usr = request.user
		usr = Perfil.objects.get(usuario=usr)

		try:
			# xHACER:  sera q acepto servicio via get or post?? y ademas debo limpiar el dato!!
			serv = get_object_or_404(ServicioVirtual, id=servicio)
			nomb_complemento = request.POST['nomb-complemento']
			desc_complemento = request.POST['desc-complemento']
			precio_complemento = request.POST['precio-complemento']
			ServicioSatelite.objects.create(servicio_v=serv, usuario=usr, nombre=nomb_complemento, descripcion=desc_complemento, precio=precio_complemento)
		except:
			pass  # xHACER: q pasa si no se envia y q retorna al final
		return usr
	else:
		return HttpResponseRedirect(reverse('geoservicios.views.sesionar_usr'))


def enlistar_usuario(request, usr):
	"""Enlistar solicitudes de servicio"""
	if request.user.is_authenticated():
		u = get_object_or_404(Perfil, usuario__username=usr)
		serv = request.POST["serv"]
		serv = get_object_or_404(ServicioVirtual, url=serv)
		cont = ""
		n_clausulas = int(request.POST['Nclausulas'])+1
		for k in range(n_clausulas):
			n = 'clausula-'+str(k)
			cont += request.POST[n] + "<br>"
		cont = cont[: len(cont)-4 ]
		Cola.objects.create(servicio=serv, estatus=0, vendedor=serv.vendedor, comprador=u, contrato=cont)
		return HttpResponseRedirect(reverse('geoservicios.views.perfil', args=[u]))
	else:
		return HttpResponseRedirect(reverse('geoservicios.views.inicio'))


def lista_solicitudes_servicio(request):
	"""Aceptar o rechazar solicitudes y mostrar la lista"""
	if request.user.is_authenticated():
		u = get_object_or_404(Perfil, usuario__username=request.user)
		try:
			opc = request.POST["opc"]
			if opc == "1":  # cancelar
				ident = request.POST["ident"]
				Cola.objects.filter(id=ident).delete()
				# xHACER: falta verificar q sea el servicio q quiero eliminar
			if opc == "2":  # aceptar
				pass  # xHACER:
		except:
			pass
		lista = []
		servis = Cola.objects.filter(estatus=0, vendedor=u)
		for sec in servis:  # sec= servicio en cola
			if sec.servicio.contrato != sec.contrato:
				x = sec.contrato.split("<br>")
			else:
				x = []
			lista.append([sec, x])
		return render_to_response('encolados.html', {
			'perfil': u,
			'perfil_logueado': u,
			'logueado': True,
			'lista': lista,
		}, RequestContext(request))
	else:
		return HttpResponseRedirect(reverse('geoservicios.views.inicio'))


def buscar(request):
	# xHACER:  limpiar variables POST y busqueda
	consulta = request.GET['c']
	usrs = Perfil.objects.filter(usuario__username__icontains=consulta)
	servis = ServicioVirtual.objects.filter(nombre__icontains=consulta)
	# elif request.POST['tipo'] == "medalla":
		# obj = Medalla.objects.filter(nombre=busqueda)

	if request.user.is_authenticated():
		u = request.user
		u = get_object_or_404(Perfil, usuario=u)

		return render_to_response('busqueda.html', {
			'perfil': u,
			'consulta': consulta,
			'perfil_logueado': u,
			'logueado': True,
			'lista_usuarios': usrs,
			'lista_servicios': servis,
		}, RequestContext(request))
	else:
		return render_to_response('busqueda.html', {
			'lista_usuarios': usrs,
			'lista_servicios': servis,
			'consulta': consulta,
		}, RequestContext(request))


def configurar_cta(request):
	if request.user.is_authenticated():
		usr = request.user
		p = get_object_or_404(Perfil, usuario=usr)
		datos = {
			'perfil': p,
			'logueado': True,
			'perfil_logueado': p,
		}
		try:
			if request.POST:
				nomb = request.POST['nombre']
				vacas = request.POST['vacas']
				edad = request.POST['edad']
				datos["edad"] = edad
				datos["vacas"] = vacas
				datos["nombre_completo"] = nomb
				Perfil.objects.filter(usuario=p).update(nombre_completo=nomb, edad=edad, vacacionando=vacas)
				datos["mensaje"] = "Se guardaron tus cambios!  :)"
			else:
				datos["edad"] = p.edad
				datos["vacas"] = p.vacacionando
				datos["nombre_completo"] = p.nombre_completo
		except:
			pass

		return render_to_response('config.html', datos, RequestContext(request))
	else:
		return HttpResponseRedirect(reverse('geoservicios.views.inicio'))


def contactarnos(request):
	if request.user.is_authenticated():
		usr = request.user
		p = get_object_or_404(Perfil, usuario=usr)
		return render_to_response('contacto.html', {
			'logueado': p,
			'perfil_logueado': p,
			'logueado': True,
		}, RequestContext(request))
	else:
		return render_to_response('contacto.html', RequestContext(request))


def comprar(request):
	"""Este modulo realiza:
		* Aceptar_compra (confirmar el cobro)
		* Confirmar_entrega (Facturada)
		* Cancelacion de la compra
	estos son seciones enlazados a paypal, mercadopago, bitpay o RIPPLE"""
	if request.user.is_authenticated():
		factura = request.POST["orden"]
		# xHACER:  implementar algo q no permita q se pueda ver la facturas de otras personas
		# falta valorar la compra en caso de confirmar
		try:
			factura = Factura.objects.get(id=factura)
		except:
			# esto significa q es para crear una nva factura
			Factura.objects.create()

		usr_sesionado = request.user
		usr_sesionado = Perfil.objects.get(usuario=usr)
		if usr_sesionado != factura.comprador or usr_sesionado != factura.vendedor:
			return "no me jodas"
	else:
		return HttpResponseRedirect(reverse('geoservicios.views.sesionar_usr'))


# xHACER: cargar en el index las categorias desde la BD y no estaticamente
def inicializar_categorias():
	c = Categoria.objects.create(nombre=u"Gráficos, Diseño y Fotografía", url="graficos-diseno-fotografia")
	Categoria.objects.create(nombre=u"Historietas, Caricaturas y Personajes", padre=c, url="historietas-caricaturas-personajes")
	Categoria.objects.create(nombre=u"Diseño de Logos", padre=c, url="diseno-logos")
	Categoria.objects.create(nombre=u"Ilustración", padre=c, url="ilustracion")
	Categoria.objects.create(nombre=u"Portada de Libros y Paquetes", padre=c, url="portada-libros-paquetes")
	Categoria.objects.create(nombre=u"Diseño Web e Interfaz de Usuario (IU)", padre=c, url="diseno-web-iu")
	Categoria.objects.create(nombre=u"Fotografía y Edición Fotográfica", padre=c, url="fotografia-edicion-fotografica")
	Categoria.objects.create(nombre=u"Diseño de Presentaciones", padre=c, url="diseno-presentaciones")
	Categoria.objects.create(nombre=u"Tarjetas de Negocios", padre=c, url="tarjetas-negocios")
	Categoria.objects.create(nombre=u"Encabezados y Anuncios", padre=c, url="encabezados-anuncios")
	Categoria.objects.create(nombre=u"Arquitectura", padre=c, url="arquitectura")
	Categoria.objects.create(nombre=u"Página Web Estática", padre=c, url="pagina-web-estatica")
	Categoria.objects.create(nombre=u"Mobiliario", padre=c, url="mobiliario")
	Categoria.objects.create(nombre=u"Videojuegos", padre=c, url="videojuegos")
	Categoria.objects.create(nombre=u"Otros", padre=c, url="otros")
	# termino

	c = Categoria.objects.create(nombre=u"Transcripción, Traducción y Redacción", url="transcripcion-traduccion-redaccion")
	Categoria.objects.create(nombre=u"Redacción y Escritura Creativa", padre=c, url="redaccion-escritura-creativa")
	Categoria.objects.create(nombre=u"Traducción", padre=c, url="traduccion")
	Categoria.objects.create(nombre=u"Transcripción", padre=c, url="transcripcion")
	Categoria.objects.create(nombre=u"Contenido para Sitios Web", padre=c, url="contenido-sitios-web")
	Categoria.objects.create(nombre=u"Reseña/Crítica", padre=c, url="resena-critica")
	Categoria.objects.create(nombre=u"Curriculum, Cartas de Presentación", padre=c, url="curriculum-cartas-presentacion")
	Categoria.objects.create(nombre=u"Redacción de Discursos", padre=c, url="redaccion-discursos")
	Categoria.objects.create(nombre=u"Edición y Revisión de Escritos", padre=c, url="edicion-revision-escritos")
	Categoria.objects.create(nombre=u"Comunicado de Prensa", padre=c, url="comunicado-prensa")
	Categoria.objects.create(nombre=u"Otros", padre=c, url="otros")
	# termino

	c = Categoria.objects.create(nombre=u"Audio y Música", url="audio-musica")
	Categoria.objects.create(nombre=u"Edición y Masterizadó de Audio", padre=c, url="edicion-masterizado-audio")
	Categoria.objects.create(nombre=u"Canciones", padre=c, url="canciones")
	Categoria.objects.create(nombre=u"Composición de canciones", padre=c, url="composicion-canciones")
	Categoria.objects.create(nombre=u"Lecciones de Música", padre=c, url="lecciones-musica")
	Categoria.objects.create(nombre=u"Música Rap", padre=c, url="musica-rap")
	Categoria.objects.create(nombre=u"Narración y Edición Doblaje", padre=c, url="narracion-edicion-doblaje")
	Categoria.objects.create(nombre=u"Efectos de sonido", padre=c, url="efectos-sonido")
	Categoria.objects.create(nombre=u"Tonos de Llamada Personalizados", padre=c, url="tonos-llamada-personalizados")
	Categoria.objects.create(nombre=u"Felicitaciones por Correo de Voz", padre=c, url="felicitaciones-correo-voz")
	Categoria.objects.create(nombre=u"Canciones Personalizadas", padre=c, url="canciones-personalizadas")
	Categoria.objects.create(nombre=u"Otros", padre=c, url="otros")
	# termino

	c = Categoria.objects.create(nombre=u"Programación y Tecnología", url="programacion-tecnologia")
	Categoria.objects.create(nombre=u".Net", padre=c, url=".net")
	Categoria.objects.create(nombre=u"C/C++", padre=c, url="c-c++")
	Categoria.objects.create(nombre=u"CSS y HTML", padre=c, url="css-html")
	Categoria.objects.create(nombre=u"Joomla y Drupal", padre=c, url="joomla-drupal")
	Categoria.objects.create(nombre=u"Base de Datos", padre=c, url="base-datos")
	Categoria.objects.create(nombre=u"Java", padre=c, url="java")
	Categoria.objects.create(nombre=u"JavaScript", padre=c, url="javascript")
	Categoria.objects.create(nombre=u"PSD a HTML", padre=c, url="psd-html")
	Categoria.objects.create(nombre=u"WordPress", padre=c, url="wordpress")
	Categoria.objects.create(nombre=u"Flash", padre=c, url="flash")
	Categoria.objects.create(nombre=u"iOS, Android y Móviles", padre=c, url="ios-android-moviles")
	Categoria.objects.create(nombre=u"PHP", padre=c, url="php")
	Categoria.objects.create(nombre=u"Preguntas y Respuestas (PR) y Pruebas de Software", padre=c, url="pr-pruebas-software")
	Categoria.objects.create(nombre=u"Tecnología", padre=c, url="tecnologia")
	Categoria.objects.create(nombre=u"Otros", padre=c, url="otros")
	# termino

	c = Categoria.objects.create(nombre=u"Marketing Digital", url="marketing-digital")
	Categoria.objects.create(nombre=u"Análisis Web", padre=c, url="analisis-web")
	Categoria.objects.create(nombre=u"Artículos y Envíos de RP", padre=c, url="articulos-envios-rp")
	Categoria.objects.create(nombre=u"Menciones en Blogs", padre=c, url="menciones-blogs")
	Categoria.objects.create(nombre=u"Búsqueda de Dominios", padre=c, url="busqueda-dominios")
	Categoria.objects.create(nombre=u"Páginas de Fans", padre=c, url="paginas-fans")
	Categoria.objects.create(nombre=u"Optimización para Motores de Búsqueda (SEO)", padre=c, url="seo")
	Categoria.objects.create(nombre=u"Marketing en Redes Sociales", padre=c, url="marketing-redes-sociales")
	Categoria.objects.create(nombre=u"Generar Tráfico Web", padre=c, url="generar-trafico-web")
	Categoria.objects.create(nombre=u"Marketing en Videos", padre=c, url="marketing-videos")
	Categoria.objects.create(nombre=u"Otros", padre=c, url="otros")
	# termino

	c = Categoria.objects.create(nombre=u"Publicidad y Propaganda", url="publicidad-propaganda")
	Categoria.objects.create(nombre=u"Tu mensaje en/con...", padre=c, url="tu-mensaje-en-con")
	Categoria.objects.create(nombre=u"Volantes, Folletos y Regalos", padre=c, url="volantes-folletos-regalos")
	Categoria.objects.create(nombre=u"Anuncios Humanos", padre=c, url="anuncios-humanos")
	Categoria.objects.create(nombre=u"Comerciales", padre=c, url="comerciales")
	Categoria.objects.create(nombre=u"Mascotas Modelos", padre=c, url="mascotas-modelos")
	Categoria.objects.create(nombre=u"Publicidad en Exteriores", padre=c, url="publicidad-exteriores")
	Categoria.objects.create(nombre=u"Radio", padre=c, url="radio")
	Categoria.objects.create(nombre=u"Promoción Musical", padre=c, url="promocion-musical")
	Categoria.objects.create(nombre=u"Publicidad en Anuncios Web", padre=c, url="publicidad-anuncios-web")
	Categoria.objects.create(nombre=u"Otros", padre=c, url="otros")
	# termino

	c = Categoria.objects.create(nombre=u"Negocios", url="negocios")
	Categoria.objects.create(nombre=u"Planes de Negocios", padre=c, url="planes-negocios")
	Categoria.objects.create(nombre=u"Consejos para tu Carrera Profesional", padre=c, url="consejos-carrera-profesional")
	Categoria.objects.create(nombre=u"Estudio de Mercado", padre=c, url="estudio-mercado")
	Categoria.objects.create(nombre=u"Presentaciones", padre=c, url="presentaciones")
	Categoria.objects.create(nombre=u"Asistentecia Virtual", padre=c, url="asistentecia-virtual")
	Categoria.objects.create(nombre=u"Consejos para Negocios", padre=c, url="consejos-negocios")
	Categoria.objects.create(nombre=u"Servicios de Marca", padre=c, url="servicios-marca")
	Categoria.objects.create(nombre=u"Consultoría Financiera", padre=c, url="consultoria-financiera")
	Categoria.objects.create(nombre=u"Consultoría Legal", padre=c, url="consultoria-legal")
	Categoria.objects.create(nombre=u"Otros", padre=c, url="otros")
	# termino

	c = Categoria.objects.create(nombre=u"Video y Animación", url="video-animacion")
	Categoria.objects.create(nombre=u"Comerciales", padre=c, url="comerciales")
	# xPENSAR:
		# deberia cambiar la estrategia (q un servicio elija las categorias)??
		# comerciales puede estar en video y en publicidad
	Categoria.objects.create(nombre=u"Edición, Efectos y Post Producción", padre=c, url="edicion-efectos-post-produccion")
	Categoria.objects.create(nombre=u"Animación y 3D", padre=c, url="animacion-3d")
	Categoria.objects.create(nombre=u"Testimonios y Comentarios", padre=c, url="testimonios-comentarios")
	Categoria.objects.create(nombre=u"Marionetas", padre=c, url="marionetas")
	Categoria.objects.create(nombre=u"Stop Motion", padre=c, url="stop-motion")
	Categoria.objects.create(nombre=u"Intros", padre=c, url="intros")
	Categoria.objects.create(nombre=u"Storyboarding", padre=c, url="storyboarding")
	Categoria.objects.create(nombre=u"Otros", padre=c, url="otros")
	# termino

	c = Categoria.objects.create(nombre=u"Diversión y Entretenimiento", url="diversion-entretenimiento")
	Categoria.objects.create(nombre=u"Video StandUp sobre Tema/Evento", padre=c, url="video-standup-sobre-tema-evento")
	Categoria.objects.create(nombre=u"Chistes Escritos", padre=c, url="chistes-escritos")
	Categoria.objects.create(nombre=u"Chistes en Vivo", padre=c, url="chistes-vivo")
	Categoria.objects.create(nombre=u"Discurso Gracioso para Evento", padre=c, url="discurso-gracioso-evento")
	Categoria.objects.create(nombre=u"Personificación de Celebridades", padre=c, url="personificacion-celebridades")
	Categoria.objects.create(nombre=u"Truco de Magia Personalizable", padre=c, url="truco-magia-personalizable")
	Categoria.objects.create(nombre=u"Otros", padre=c, url="otros")
	# termino

	c = Categoria.objects.create(nombre=u"Estilo de vida", url="estilo-vida")
	Categoria.objects.create(nombre=u"Cuidado de Animales y Mascotas", padre=c, url="cuidado-animales-mascotas")
	Categoria.objects.create(nombre=u"Consejos sobre Relaciones", padre=c, url="consejos-relaciones")
	Categoria.objects.create(nombre=u"Maquillaje, Estilo y Belleza", padre=c, url="maquillaje-estilo-belleza")
	Categoria.objects.create(nombre=u"Astrología y Tarot", padre=c, url="astrologia-tarot")
	Categoria.objects.create(nombre=u"Recetas de Cocina", padre=c, url="recetas-cocina")
	Categoria.objects.create(nombre=u"Consejos para Padres", padre=c, url="consejos-padres")
	Categoria.objects.create(nombre=u"Viajes", padre=c, url="viajes")
	Categoria.objects.create(nombre=u"Otros", padre=c, url="otros")
	# termino

	c = Categoria.objects.create(nombre=u"Regalos", url="regalos")
	Categoria.objects.create(nombre=u"Tarjetas de Felicitación", padre=c, url="tarjetas-felicitacion")
	Categoria.objects.create(nombre=u"Video Felicitaciones", padre=c, url="video-felicitaciones")
	Categoria.objects.create(nombre=u"Arte y Manualidades", padre=c, url="arte-manualidades")
	Categoria.objects.create(nombre=u"Joyería Hecha a Mano", padre=c, url="joyeria-hecha-mano")
	Categoria.objects.create(nombre=u"Regalos para Nerdos", padre=c, url="regalos-nerdos")
	Categoria.objects.create(nombre=u"Otros", padre=c, url="otros")
