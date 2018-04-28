#! /usr/bin/env python
# -*- coding: utf-8 -*-

from geoservicios.models import *
from geoservicios.formularios import *
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect  # , Http404
from django.shortcuts import render, get_object_or_404  # , redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.core import serializers
from django.contrib.gis import geos
from django.contrib.gis import measure
from datetime import datetime  # , date
import re

# xDEPURAR:
ANIO_INICIO_CH = 2015  # CH: cuadro de honor
IDIOMAS_DISPONIBLES = ["es", "en"]
	# "es":
	# "en-US":
	# "pt-BR":
	# "ru-RU":
	# "hi":  # india?
	# "en-ZA":  # sudafrica  or "af" or "zu":
	# "zh-CN":
	# "fr-FR":
	# "da-DE":  # or "de-DE":
UBICACION_PREDETERMINADA = (7.125, -66.166)  # Venezuela, (lat, lon) o es mejor localizarlo por la ip y le muestro cosas de por su vdd pais

# xHACER: esto no es mejor con iri_to_uri ??
def uerelizar(cad):  # que tiene forma de URL

	return cad.replace(" ", "-").replace(u"ñ", "n").replace(u"á", "a").replace(u"é", "e").replace(u"í", "i").replace(u"ó", "o").replace(u"ú", "u").lower()

# encuentra-servs-geo
# def recuperar_nuevos_gs(lon, lat):
# 	if request.is_ajax():
# 		lat = request.POST.get('lat',None)
# 		lon = request.POST.get('lon',None)

# 		if lon and lat:
# 			# xHACER:
# 				# esto se debe optimizar con urgencia
# 			mi_punto = geos.fromstr("POINT(%s %s)" % (lon, lat))
# 			distancia_maxima = {'km': 10}
# 			distancia_minima = {'km': 1}
# 			gs = ServicioVirtual.gis.filter(vendedor__ubicacion__distance_lte=(mi_punto, measure.D(**distancia_maxima))).exclude(vendedor__ubicacion__distance_gte=(mi_punto, measure.D(**distancia_minima)))[:8]
# 			gs = gs.distance(mi_punto).order_by('distance')
# 			if gs:
# 				return HttpResponse(serializers.serialize('json', gs.distance(mi_punto)), mimetype='application/json')
# 			return "Apurate agrega tu GeoServicio, al ser el primero acumularas mas puntos de experiencia, lo que te permitira posicionarte mejor en las listas"
# 	return u"Error en la Petición: No es AJAX o no están datos {longitud, latitud}"


def recuperar_mejores_gs(lon, lat):
	# xHACER:
		# esto se debe optimizar con urgencia
	if lon and lat:
		mi_punto = geos.fromstr("POINT(%s %s)" % (lon, lat))
		distancia_maxima = {'km': 10}
		distancia_minima = {'km': 1}
		gs = Valoracion.gis.filter(servicio__vendedor__ubicacion__distance_lte=(mi_punto, measure.D(**distancia_maxima))).exclude(servicio__vendedor__ubicacion__distance_gte=(mi_punto, measure.D(**distancia_minima)))
		gs = gs.distance(mi_punto).order_by('distance')

		return gs.distance(mi_punto)[:8]
	else:
		return "Apurate agrega tu GeoServicio, al ser el primero acumularas mas puntos de experiencia, lo que te permitira posicionarte mejor en las listas"


def buscar(request):
	# xHACER:  limpiar variables
		# GET y cadena de busqueda
		# limitar el tamaño de la cadena q recibe??
	idioma = request.LANGUAGE_CODE
	datos = {
		"formbuscar": FormBuscar(),
		"pag_activa": idioma+"/index.html",
		"idiomas_disponibles": IDIOMAS_DISPONIBLES,
	}
	if request.method == "GET":
		formbuscar = FormBuscar(request.GET)
		if formbuscar.is_valid():
			consulta = formbuscar.cleaned_data["consulta"]  # request.GET["c"]
			usrs = Perfil.objects.filter(usuario__username__icontains=consulta, eliminado=False)
			servis = ServicioVirtual.objects.filter(nombre__icontains=consulta)
			datos = {
				'lista_usuarios': usrs,
				'lista_servicios': servis,
				'consulta': consulta,
				'pag_activa': idioma+"/busqueda.html",
				'idiomas_disponibles': IDIOMAS_DISPONIBLES,
			}
		if request.user.is_authenticated():
			u = request.user
			u = get_object_or_404(Perfil, usuario=u)
			datos['perfil'] = u
			datos['perfil_logueado'] = u
			datos['logueado'] = True
		return render(request, 'base.html', datos)
	return HttpResponseRedirect(reverse('/', datos))


def inicio(request):
	# val = request.META
	# ip_cabecera = request.META["REMOTE_ADDR"]  # remote_host, server_name
	# xDEPURAR:
		# y el http_referer en q lo puedo usar??
	if request.is_ajax():
		lat = request.POST.get('lat',None)
		lon = request.POST.get('lon',None)

		if lon and lat:
			# xHACER:
				# esto se debe optimizar con urgencia
			mi_punto = geos.fromstr("POINT(%s %s)" % (lon, lat))
			distancia_maxima = {'km': 10}
			distancia_minima = {'km': 1}
			gs = ServicioVirtual.gis.filter(vendedor__ubicacion__distance_lte=(mi_punto, measure.D(**distancia_maxima))).exclude(vendedor__ubicacion__distance_gte=(mi_punto, measure.D(**distancia_minima)))[:8]
			gs = gs.distance(mi_punto).order_by('distance')
			if gs:
				return HttpResponse(serializers.serialize('json', gs.distance(mi_punto)), mimetype='application/json')
			return "Apurate agrega tu GeoServicio, al ser el primero acumularas mas puntos de experiencia, lo que te permitira posicionarte mejor en las listas"

	idioma = request.LANGUAGE_CODE
	datos = {
		# 'nuevos_geos': recuperar_nuevos_gs(lon=lo , lat=la),
		'idioma': idioma,
		# 'servicios_valorados': recuperar_mejores_gs(lon=lo, lat=la),
		# 'LANGUAGES': settings.LANGUAGES,
		'idiomas_disponibles': IDIOMAS_DISPONIBLES,
		# 'val': val,
	}
	if request.user.is_authenticated():
		u = request.user
		u = get_object_or_404(Perfil, usuario=u)
		datos['perfil'] = u
		datos['perfil_logueado'] = u
		datos['logueado'] = True
	datos["pag_activa"] = idioma+"/index.html"
	return render(request, "base.html", datos)


def sesionar_usr(request):
	# xHACER:
		# usar is_activeen vez de eliminado para validar q no vuelvan a entrar
	if request.user.is_authenticated():
		return HttpResponseRedirect(reverse('geoservicios.views.inicio'))
	else:
		idioma = request.LANGUAGE_CODE
		datos = {
			"pag_activa": idioma+"/index.html",
			"idiomas_disponibles": IDIOMAS_DISPONIBLES,
		}
		try:
			# xHACER: Post debo filtrarlos!
			usuario = authenticate(username = request.POST['usuario'], password = request.POST['pw'])
			# xHACER:
				# esto es como deberia hacerse?:
				# user = authenticate(username=username, password=password)
				# if user is not None:
		except KeyError:
			datos["mensaje"] = 'Rellene todos los campos'
			return render(request, 'base.html', datos)
		if usuario is not None:
			if usuario.is_active:
				login(request, usuario)
			else:
				datos["mensaje"] = 'El usuario ha sido eliminado'
				return render(request, 'base.html', datos,
				RequestContext(request))
		else:
			datos["mensaje"] = 'Ingrese los datos correctamente'
			return render(request, 'base.html', datos)
		return HttpResponseRedirect(reverse('geoservicios.views.perfil', args=[usuario]))


def cerrar_sesion(request):
	# xHACER: 	# idioma = request.LANGUAGE_CODE
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
		idioma = request.LANGUAGE_CODE
		datos = {
			"pag_activa": idioma+"/index.html",
			"idiomas_disponibles": IDIOMAS_DISPONIBLES,
		}
		if not re.match('^[a-zA-Z0-9_]+$', request.POST['usuario']):
			datos["mensaje"] = 'El nombre de usuario solo puede contener letras, numeros y _'
			return render(request, 'base.html', datos)
		if not re.match('^[a-zA-Z][a-zA-Z0-9_]*[@][a-zA-Z0-9_.]+[.][a-zA-Z0-9_]+$', request.POST['correo']):
			datos["mensaje"] = 'Ingrese un correo valido'
			return render(request, 'base.html', datos)

		usr = request.POST['usuario'].lower()
		if User.objects.filter(username__iexact = usr):
			datos["mensaje"] = 'El usuario ya existe'
			return render(request, 'base.html', datos)
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
		datos["mensaje"] = 'Rellene todos los campos'
		return render(request, 'base.html', datos)


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
	q = CuadroHonor.objects.filter(tipo_puntaje=0, mes=m, anio=a, usuario__eliminado=False)
	for l in q:
		lista_atencion.append([l.puntaje, l.usuario])

	q = CuadroHonor.objects.filter(tipo_puntaje=1, mes=m, anio=a, usuario__eliminado=False)
	for l in q:
		lista_tiempo_entrega.append([l.puntaje, l.usuario])

	q = CuadroHonor.objects.filter(tipo_puntaje=2, mes=m, anio=a, usuario__eliminado=False)
	for l in q:
		lista_calidad.append([l.puntaje, l.usuario])

	q = CuadroHonor.objects.filter(tipo_puntaje=3, mes=m, anio=a, usuario__eliminado=False)
	for l in q:
		lista_promedio.append([l.puntaje, l.usuario])

	q = CuadroHonor.objects.filter(tipo_puntaje=4, mes=m, anio=a, usuario__eliminado=False)
	for l in q:
		lista_experiencia.append([l.puntaje, l.usuario])

	# xHACER: cambiar None este por algo mas elegante
	usr = None
	if request.user.is_authenticated():
		usr = request.user
		usr = get_object_or_404(Perfil, usuario__username = usr)
	idioma = request.LANGUAGE_CODE
	return render(request, 'base.html', {
		"pag_activa": idioma+"/cuadroHonor.html",
		"idiomas_disponibles": IDIOMAS_DISPONIBLES,
		'perfil': usr if usr else None,
		'perfil_logueado': usr if usr else None,
		'logueado': True if usr else None,
		'lista_atencion': lista_atencion,
		'lista_tiempo_entrega': lista_tiempo_entrega,
		'lista_calidad': lista_calidad,
		'lista_promedio': lista_promedio,
		'lista_experiencia': lista_experiencia,
		})


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
	servs = ServicioVirtual.objects.filter(activo=True, subcategoria__in=subcats, vendedor__eliminado=False)[:20]
	idioma = request.LANGUAGE_CODE
	datos = {
		'categoria': cat,
		'servicios': servs,
		'subcategorias': subcats,
		"pag_activa": idioma+"/categoria.html",
		"idiomas_disponibles": IDIOMAS_DISPONIBLES,
	}
	if request.user.is_authenticated():
		usr = request.user
		p = get_object_or_404(Perfil, usuario=usr)
		datos['perfil'] = p
		datos['perfil_logueado'] = p
		datos['logueado'] = True
		return render(request, 'base.html', datos)
	else:
		return render(request, 'base.html', datos)


def ver_subcategoria(request, cat, subcat):
	# xHACER:  usar un paginador, limpiar subcat, 
	cat = get_object_or_404(Categoria, url=cat)
	subcategorias = Categoria.objects.filter(padre=cat)
	subcat = get_object_or_404(Categoria, url=subcat, padre=cat)
	servs = ServicioVirtual.objects.filter(activo=True, subcategoria=subcat, vendedor__eliminado=False)[:20]
	idioma = request.LANGUAGE_CODE
	datos = {
		'categoria': cat,
		'servicios': servs,
		'subcategorias': subcategorias,
		'nomb_subcategoria': subcat,
		"pag_activa": idioma+"/categoria.html",
		"idiomas_disponibles": IDIOMAS_DISPONIBLES,
	}
	if request.user.is_authenticated():
		usr = request.user
		p = get_object_or_404(Perfil, usuario=usr)
		datos['perfil'] = p
		datos['perfil_logueado'] = p
		datos['logueado'] = True
		return render(request, 'base.html', datos)
	else:
		return render(request, 'base.html', datos)


def ver_servicio(request, cat, serv):
	# xHACER:  usar un paginador, limpiar subcat
	cat = get_object_or_404(Categoria, url=cat)
	serv = get_object_or_404(ServicioVirtual, url=serv)
	data = {}
	if serv.vendedor.eliminado:
		data["mensaje"] = "Lo sentimos, el usuario ha cancelado su cuenta"
	elif serv.eliminado:
		data["mensaje"] = "Lo sentimos, el usuario ha cancelado el servicio o esta de vacaciones"
	if data:
		return render(request, 'base.html', data)
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
	idioma = request.LANGUAGE_CODE
	datos = {
		"pag_activa": idioma+"/servicio.html",
		"idiomas_disponibles": IDIOMAS_DISPONIBLES,
		'exp': val.experiencia,
		'te': val.tiempo_entrega,
		'calidad': val.calidad,
		'atencion': val.atencion,
		'servicio': serv,
		'contrato': contrato,
		'categoria': cat,
		'servs_satelite': extras,
	}
	if request.user.is_authenticated():
		usr = request.user
		p = get_object_or_404(Perfil, usuario=usr)
		datos['perfil'] = p
		datos['logueado'] = True
		datos['perfil_logueado'] = p
		return render(request, 'base.html', datos)
	else:
		return render(request, 'base.html', datos)


def perfil(request, usr):
	# xHACER:  tiempo estimado de entrega por cada servicio, x semana
	# numero de impresiones de anuncios en las busquedas
	# cant de usuarios atendidos por servicio
	# cant de servicios rechazados mutuamente
	usr = get_object_or_404(User, username=usr)
	try:
		perfil = get_object_or_404(Perfil, usuario=usr, eliminado=False)
	except:
		idioma = request.LANGUAGE_CODE
		data = {}
		data["mensaje"] = "El usuario ha cancelado su cuenta"
		data["pag_activa"] = idioma+"/index.html"
		data["idiomas_disponibles"] = IDIOMAS_DISPONIBLES
		return render(request, 'base.html', data)
	servis = ServicioVirtual.objects.filter(vendedor=perfil)
	cant_servicios = servis.count()
	facturas = Factura.objects.filter(servicio__vendedor=perfil)
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
	idioma = request.LANGUAGE_CODE
	datos = {
		'vacacionando': "Si" if perfil.vacacionando else "No, Trabajando",
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
		"pag_activa": idioma+"/perfil.html",
		"idiomas_disponibles": IDIOMAS_DISPONIBLES,
	}
	if request.user.is_authenticated():
		u = get_object_or_404(User, username = request.user)
		datos['logueado'] = True
		if usr != u:
			p = get_object_or_404(Perfil, usuario = u)
			datos['perfil_logueado'] = p
		else:
			datos['perfil_propio'] = True
	return render(request, 'base.html', datos)


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
		# xHACER:
			# si tu eres un chino como coño traduces tu servicio a url??
		precio = int(request.POST['precio'])
		descrip = request.POST['descrip']
		cont = ""
		if(request.POST['Nclausulas']!=""):
			n_clausulas = int(request.POST['Nclausulas'])+1
		else:
			n_clausulas = 1
		for k in range(n_clausulas):
			n = 'clausula-'+str(k)
			cont += request.POST[n] + "<br>"
		cont = cont[: len(cont)-4 ]
		id_subc = int(request.POST['subc'])
		id_cat = int(request.POST['subcategoria'])
		cat = Categoria.objects.filter(padre=None)[id_cat]
		subc = Categoria.objects.filter(padre=cat)[id_subc]

		s = ServicioVirtual.objects.create(nombre=nomb, url=url, descripcion=descrip, contrato=cont, precio=precio, subcategoria=subc, vendedor=p)
		Contador.objects.create(servicio=s, experiencia=0, atencion=0, calidad=0, promedio=0, tiempo_entrega=0)

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
		if u == serv.vendedor:
			# xHACER: quizas yo deba hacer mi propio redirect q envie datos POST
			idioma = request.LANGUAGE_CODE
			datos = {
				'perfil': u,
				'perfil_logueado': u,
				'logueado': True,
				'lista': lista,
				"pag_activa": idioma+"/lista-solicitudes-servicio.html",
				"idiomas_disponibles": IDIOMAS_DISPONIBLES,
				"mensaje": "No puedes comprar tus propios servicios"
			}
			return render(request, 'base.html', datos)
		# cont = ""
		# n_clausulas = int(request.POST['Nclausulas'])+1
		# for k in range(n_clausulas):
		# 	n = 'clausula-'+str(k)
		# 	cont += request.POST[n] + "<br>"
		# cont = cont[: len(cont)-4 ]
		Cola.objects.create(servicio=serv, estatus=0, comprador=u, contrato=serv.contrato)
		return HttpResponseRedirect(reverse('geoservicios.views.perfil', args=[u]))
	else:
		return HttpResponseRedirect(reverse('geoservicios.views.inicio'))


def lista_solicitudes_servicio(request):
	"""Aceptar o rechazar solicitudes y mostrar la lista"""
	if request.user.is_authenticated():
		u = get_object_or_404(Perfil, usuario__username=request.user)
		try:
			opc = request.POST["opc"]
			if opc == "0":  # sin ver
				pass
			if opc == "1":  # vendedor acepto tomar la orden
				ident = request.POST["ident"]
				Cola.objects.filter(id=ident).update(estatus=1)
				# xHACER: falta verificar q sea el servicio q quiero
			if opc == "2":  # aceptar
				pass  # xHACER: guardar en factura con cant de mercadopago/paypal
		except:
			pass
		lista = []
		servis = Cola.objects.filter(estatus=0)
		for sec in servis:  # sec= servicio en cola
			if sec.servicio.contrato != sec.contrato:
				x = sec.contrato.split("<br>")
			else:
				x = []
			lista.append([sec, x])
		idioma = request.LANGUAGE_CODE
		datos = {
			'perfil': u,
			'perfil_logueado': u,
			'logueado': True,
			'lista': lista,
			"pag_activa": idioma+"/encolados.html",
			"idiomas_disponibles": IDIOMAS_DISPONIBLES,
		}
		return render(request, 'base.html', datos)
	else:
		return HttpResponseRedirect(reverse('geoservicios.views.inicio'))


def configurar_cta(request):
	if request.user.is_authenticated():
		usr = request.user
		p = get_object_or_404(Perfil, usuario=usr)
		idioma = request.LANGUAGE_CODE
		datos = {
			"pag_activa": idioma+"/config.html",
			"idiomas_disponibles": IDIOMAS_DISPONIBLES,
			'perfil': p,
			'logueado': True,
			'perfil_logueado': p,
		}
		try:
			if request.method == "POST":
				peses = [p.nombre_completo, p.edad,p.vacacionando]
				var = [None,None,None]
				# nomb = request.POST['nombre']
				# vacas = request.POST['vacas']
				# edad = request.POST['edad']
				for i, dat in enumerate(['nombre','edad','vacas']):
					if request.POST[dat]:
						datos[dat] = var[i] = request.POST[dat]
					else:
						datos[dat] = var[i] = peses[i]
				Perfil.objects.filter(usuario=p).update(nombre_completo=var[0], edad=var[1], vacacionando=var[2])
				datos["mensaje"] = "Se guardaron tus cambios!  =)"
			else:
				datos["nombre"] = p.nombre_completo
				datos["edad"] = p.edad
				datos["vacas"] = p.vacacionando
				# xHACER:
					# no se lee del otro lado la variable "vacas", al parecer no sale en BD
		except BaseException, e:
			datos["mensaje"] = e
		return render(request, 'base.html', datos)
	else:
		return HttpResponseRedirect(reverse('geoservicios.views.inicio'))


def borrar_cta(request):
	"""Actualmente conservo Valoracion para saber si el q se fue era bueno en lo que hace, ServiciosVirtuales/Setelite para tener control de las facturas hechas"""
	if request.user.is_authenticated():
		usr = request.user
		p = get_object_or_404(Perfil, usuario=usr)
		idioma = request.LANGUAGE_CODE
		datos = {
			"pag_activa": idioma+"/index.html",
			"idiomas_disponibles": IDIOMAS_DISPONIBLES
		}
		try:
			Perfil.objects.filter(usuario=p).update(eliminado=True)
			s=ServicioVirtual.objects.filter(vendedor=p)
			ServicioVirtual.objects.filter(vendedor=p).update(eliminado=True)
			ServicioSatelite.objects.filter(servicio=s).update(eliminado=True)
			Cola.objects.filter(servicio=s).delete()
			Contador.objects.filter(servicio=s).delete()
			Disponibilidad.objects.filter(servicio=s).delete()
			logout(request)
			datos["mensaje"] = "Su cuenta ha sido cerrada. Te extrañaremos :(  (Puedes volver cuando quieras)"

		except BaseException, e:
			datos["mensaje"] = e

		return render(request, 'base.html', datos)
	else:
		return HttpResponseRedirect(reverse('geoservicios.views.inicio'))


def contactarnos(request):
	idioma = request.LANGUAGE_CODE
	datos = {
		"pag_activa": idioma+"/contacto.html",
		"idiomas_disponibles": IDIOMAS_DISPONIBLES,
	}
	if request.user.is_authenticated():
		usr = request.user
		p = get_object_or_404(Perfil, usuario=usr)
		datos['logueado'] = p
		datos['perfil_logueado'] = p
		datos['logueado'] = True
		return render(request, 'base.html', datos)
	else:
		return render(request, 'base.html', datos)


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


# xHACER: cargar en el index las categorias desde la BD y no estaticamente?
# ver archivo vista_traduccionCategoria.txt
def inicializar_categorias():		
	c = Categoria.objects.create(url="graficos-diseno-fotografia", nombre=u"Gráficos, Diseño y Fotografía", descripcion="")
	Categoria.objects.create(nombre=u"Historietas, Caricaturas y Personajes", descripcion="", padre=c, url="historietas-caricaturas-personajes")
	Categoria.objects.create(nombre=u"Diseño de Logos", descripcion="", padre=c, url="diseno-logos")
	Categoria.objects.create(nombre=u"Ilustración", descripcion="", padre=c, url="ilustracion")
	Categoria.objects.create(nombre=u"Portada de Libros y Paquetes", descripcion="", padre=c, url="portada-libros-paquetes")
	Categoria.objects.create(nombre=u"Diseño Web e Interfaz de Usuario (IU)", descripcion="", padre=c, url="diseno-web-iu")
	Categoria.objects.create(nombre=u"Fotografía y Edición Fotográfica", descripcion="", padre=c, url="fotografia-edicion-fotografica")
	Categoria.objects.create(nombre=u"Diseño de Presentaciones", descripcion="", padre=c, url="diseno-presentaciones")
	Categoria.objects.create(nombre=u"Tarjetas de Negocios", descripcion="", padre=c, url="tarjetas-negocios")
	Categoria.objects.create(nombre=u"Encabezados y Anuncios", descripcion="", padre=c, url="encabezados-anuncios")
	Categoria.objects.create(nombre=u"Arquitectura", descripcion="", padre=c, url="arquitectura")
	Categoria.objects.create(nombre=u"Página Web Estática", descripcion="", padre=c, url="pagina-web-estatica")
	Categoria.objects.create(nombre=u"Mobiliario", descripcion="", padre=c, url="mobiliario")
	Categoria.objects.create(nombre=u"Videojuegos", descripcion="", padre=c, url="videojuegos")
	Categoria.objects.create(nombre=u"Otros", descripcion="", padre=c, url="otros")
	# termino


	c = Categoria.objects.create(url="transcripcion-traduccion-redaccion", nombre=u"Transcripción, Traducción y Redacción", descripcion="")
	Categoria.objects.create(nombre=u"Redacción y Escritura Creativa", descripcion="", padre=c, url="redaccion-escritura-creativa")
	Categoria.objects.create(nombre=u"Traducción", descripcion="", padre=c, url="traduccion")
	Categoria.objects.create(nombre=u"Transcripción", descripcion="", padre=c, url="transcripcion")
	Categoria.objects.create(nombre=u"Contenido para Sitios Web", descripcion="", padre=c, url="contenido-sitios-web")
	Categoria.objects.create(nombre=u"Reseña/Crítica", descripcion="", padre=c, url="resena-critica")
	Categoria.objects.create(nombre=u"Curriculum, Cartas de Presentación", descripcion="", padre=c, url="curriculum-cartas-presentacion")
	Categoria.objects.create(nombre=u"Redacción de Discursos", descripcion="", padre=c, url="redaccion-discursos")
	Categoria.objects.create(nombre=u"Edición y Revisión de Escritos", descripcion="", padre=c, url="edicion-revision-escritos")
	Categoria.objects.create(nombre=u"Comunicado de Prensa", descripcion="", padre=c, url="comunicado-prensa")
	Categoria.objects.create(nombre=u"Otros", descripcion="", padre=c, url="otros")
	# termino


	c = Categoria.objects.create(url="audio-musica", nombre=u"Audio y Música", descripcion="")
	Categoria.objects.create(nombre=u"Edición y Masterizadó de Audio", descripcion="", padre=c, url="edicion-masterizado-audio")
	Categoria.objects.create(nombre=u"Canciones", descripcion="", padre=c, url="canciones")
	Categoria.objects.create(nombre=u"Composición de canciones", descripcion="", padre=c, url="composicion-canciones")
	Categoria.objects.create(nombre=u"Lecciones de Música", descripcion="", padre=c, url="lecciones-musica")
	Categoria.objects.create(nombre=u"Música Rap", descripcion="", padre=c, url="musica-rap")
	Categoria.objects.create(nombre=u"Narración y Edición Doblaje", descripcion="", padre=c, url="narracion-edicion-doblaje")
	Categoria.objects.create(nombre=u"Efectos de sonido", descripcion="", padre=c, url="efectos-sonido")
	Categoria.objects.create(nombre=u"Tonos de Llamada Personalizados", descripcion="", padre=c, url="tonos-llamada-personalizados")
	Categoria.objects.create(nombre=u"Felicitaciones por Correo de Voz", descripcion="", padre=c, url="felicitaciones-correo-voz")
	Categoria.objects.create(nombre=u"Canciones Personalizadas", descripcion="", padre=c, url="canciones-personalizadas")
	Categoria.objects.create(nombre=u"Otros", descripcion="", padre=c, url="otros")
	# termino


	c = Categoria.objects.create(url="programacion-tecnologia", nombre=u"Programación y Tecnología", descripcion="")
	Categoria.objects.create(nombre=u".Net", descripcion="", padre=c, url=".net")
	Categoria.objects.create(nombre=u"C/C++", descripcion="", padre=c, url="c-c++")
	Categoria.objects.create(nombre=u"CSS y HTML", descripcion="", padre=c, url="css-html")
	Categoria.objects.create(nombre=u"Joomla y Drupal", descripcion="", padre=c, url="joomla-drupal")
	Categoria.objects.create(nombre=u"Base de Datos", descripcion="", padre=c, url="base-datos")
	Categoria.objects.create(nombre=u"Java", descripcion="", padre=c, url="java")
	Categoria.objects.create(nombre=u"JavaScript", descripcion="", padre=c, url="javascript")
	Categoria.objects.create(nombre=u"PSD a HTML", descripcion="", padre=c, url="psd-html")
	Categoria.objects.create(nombre=u"WordPress", descripcion="", padre=c, url="wordpress")
	Categoria.objects.create(nombre=u"Flash", descripcion="", padre=c, url="flash")
	Categoria.objects.create(nombre=u"iOS, Android y Móviles", descripcion="", padre=c, url="ios-android-moviles")
	Categoria.objects.create(nombre=u"PHP", descripcion="", padre=c, url="php")
	Categoria.objects.create(nombre=u"Preguntas y Respuestas (PR) y Pruebas de Software", descripcion="", padre=c, url="pr-pruebas-software")
	Categoria.objects.create(nombre=u"Tecnología", descripcion="", padre=c, url="tecnologia")
	Categoria.objects.create(nombre=u"Otros", descripcion="", padre=c, url="otros")
	# termino


	c = Categoria.objects.create(url="marketing-digital", nombre=u"Marketing Digital", descripcion="")
	Categoria.objects.create(nombre=u"Análisis Web", descripcion="", padre=c, url="analisis-web")
	Categoria.objects.create(nombre=u"Artículos y Envíos de RP", descripcion="", padre=c, url="articulos-envios-rp")
	Categoria.objects.create(nombre=u"Menciones en Blogs", descripcion="", padre=c, url="menciones-blogs")
	Categoria.objects.create(nombre=u"Búsqueda de Dominios", descripcion="", padre=c, url="busqueda-dominios")
	Categoria.objects.create(nombre=u"Páginas de Fans", descripcion="", padre=c, url="paginas-fans")
	Categoria.objects.create(nombre=u"Optimización para Motores de Búsqueda (SEO)", descripcion="", padre=c, url="seo")
	Categoria.objects.create(nombre=u"Marketing en Redes Sociales", descripcion="", padre=c, url="marketing-redes-sociales")
	Categoria.objects.create(nombre=u"Generar Tráfico Web", descripcion="", padre=c, url="generar-trafico-web")
	Categoria.objects.create(nombre=u"Marketing en Videos", descripcion="", padre=c, url="marketing-videos")
	Categoria.objects.create(nombre=u"Otros", descripcion="", padre=c, url="otros")
	# termino


	c = Categoria.objects.create(url="publicidad-propaganda", nombre=u"Publicidad y Propaganda", descripcion="")
	Categoria.objects.create(nombre=u"Tu mensaje en/con...", descripcion="", padre=c, url="tu-mensaje-en-con")
	Categoria.objects.create(nombre=u"Volantes, Folletos y Regalos", descripcion="", padre=c, url="volantes-folletos-regalos")
	Categoria.objects.create(nombre=u"Anuncios Humanos", descripcion="", padre=c, url="anuncios-humanos")
	Categoria.objects.create(nombre=u"Comerciales", descripcion="", padre=c, url="comerciales")
	Categoria.objects.create(nombre=u"Mascotas Modelos", descripcion="", padre=c, url="mascotas-modelos")
	Categoria.objects.create(nombre=u"Publicidad en Exteriores", descripcion="", padre=c, url="publicidad-exteriores")
	Categoria.objects.create(nombre=u"Radio", descripcion="", padre=c, url="radio")
	Categoria.objects.create(nombre=u"Promoción Musical", descripcion="", padre=c, url="promocion-musical")
	Categoria.objects.create(nombre=u"Publicidad en Anuncios Web", descripcion="", padre=c, url="publicidad-anuncios-web")
	Categoria.objects.create(nombre=u"Otros", descripcion="", padre=c, url="otros")
	# termino


	c = Categoria.objects.create(url="negocios", nombre=u"Negocios", descripcion="")
	Categoria.objects.create(nombre=u"Planes de Negocios", descripcion="", padre=c, url="planes-negocios")
	Categoria.objects.create(nombre=u"Consejos para tu Carrera Profesional", descripcion="", padre=c, url="consejos-carrera-profesional")
	Categoria.objects.create(nombre=u"Estudio de Mercado", descripcion="", padre=c, url="estudio-mercado")
	Categoria.objects.create(nombre=u"Presentaciones", descripcion="", padre=c, url="presentaciones")
	Categoria.objects.create(nombre=u"Asistentecia Virtual", descripcion="", padre=c, url="asistentecia-virtual")
	Categoria.objects.create(nombre=u"Consejos para Negocios", descripcion="", padre=c, url="consejos-negocios")
	Categoria.objects.create(nombre=u"Servicios de Marca", descripcion="", padre=c, url="servicios-marca")
	Categoria.objects.create(nombre=u"Consultoría Financiera", descripcion="", padre=c, url="consultoria-financiera")
	Categoria.objects.create(nombre=u"Consultoría Legal", descripcion="", padre=c, url="consultoria-legal")
	Categoria.objects.create(nombre=u"Otros", descripcion="", padre=c, url="otros")
	# termino


	c = Categoria.objects.create(url="video-animacion", nombre=u"Video y Animación", descripcion="")
	Categoria.objects.create(nombre=u"Comerciales", descripcion="", padre=c, url="comerciales")
	# xPENSAR:
		# deberia cambiar el esquema (q un servicio elija las categorias)??
		# comerciales puede estar en video y en publicidad
	Categoria.objects.create(nombre=u"Edición, Efectos y Post Producción", descripcion="", padre=c, url="edicion-efectos-post-produccion")
	Categoria.objects.create(nombre=u"Animación y 3D", descripcion="", padre=c, url="animacion-3d")
	Categoria.objects.create(nombre=u"Testimonios y Comentarios", descripcion="", padre=c, url="testimonios-comentarios")
	Categoria.objects.create(nombre=u"Marionetas", descripcion="", padre=c, url="marionetas")
	Categoria.objects.create(nombre=u"Stop Motion", descripcion="", padre=c, url="stop-motion")
	Categoria.objects.create(nombre=u"Intros", descripcion="", padre=c, url="intros")
	Categoria.objects.create(nombre=u"Storyboarding", descripcion="", padre=c, url="storyboarding")
	Categoria.objects.create(nombre=u"Otros", descripcion="", padre=c, url="otros")
	# termino


	c = Categoria.objects.create(url="diversion-entretenimiento", nombre=u"Diversión y Entretenimiento", descripcion="")
	Categoria.objects.create(nombre=u"Video StandUp sobre Tema/Evento", descripcion="", padre=c, url="video-standup-sobre-tema-evento")
	Categoria.objects.create(nombre=u"Chistes Escritos", descripcion="", padre=c, url="chistes-escritos")
	Categoria.objects.create(nombre=u"Chistes en Vivo", descripcion="", padre=c, url="chistes-vivo")
	Categoria.objects.create(nombre=u"Discurso Gracioso para Evento", descripcion="", padre=c, url="discurso-gracioso-evento")
	Categoria.objects.create(nombre=u"Personificación de Celebridades", descripcion="", padre=c, url="personificacion-celebridades")
	Categoria.objects.create(nombre=u"Truco de Magia y Predigitacion", descripcion="", padre=c, url="truco-magia-predigitacion")
	# xHACER:
		# q es esto mijo?
	Categoria.objects.create(nombre=u"Humor Gr&aacute;fico", descripcion="", padre=c, url="humor-grafico")
	Categoria.objects.create(nombre=u"Otros", descripcion="", padre=c, url="otros")
	# termino


	c = Categoria.objects.create(url="estilo-vida", nombre=u"Estilo de vida", descripcion="")
	Categoria.objects.create(nombre=u"Cuidado de Animales y Mascotas", descripcion="", padre=c, url="cuidado-animales-mascotas")
	Categoria.objects.create(nombre=u"Consejos sobre Relaciones", descripcion="", padre=c, url="consejos-relaciones")
	Categoria.objects.create(nombre=u"Maquillaje, Estilo y Belleza", descripcion="", padre=c, url="maquillaje-estilo-belleza")
	Categoria.objects.create(nombre=u"Astrología y Tarot", descripcion="", padre=c, url="astrologia-tarot")
	Categoria.objects.create(nombre=u"Recetas de Cocina", descripcion="", padre=c, url="recetas-cocina")
	Categoria.objects.create(nombre=u"Consejos para Padres", descripcion="", padre=c, url="consejos-padres")
	Categoria.objects.create(nombre=u"Viajes", descripcion="", padre=c, url="viajes")
	Categoria.objects.create(nombre=u"Otros", descripcion="", padre=c, url="otros")
	# termino


	c = Categoria.objects.create(url="regalos", nombre=u"Regalos", descripcion="")
	Categoria.objects.create(nombre=u"Tarjetas de Felicitación", descripcion="", padre=c, url="tarjetas-felicitacion")
	Categoria.objects.create(nombre=u"Video Felicitaciones", descripcion="", padre=c, url="video-felicitaciones")
	Categoria.objects.create(nombre=u"Arte y Manualidades", descripcion="", padre=c, url="arte-manualidades")
	Categoria.objects.create(nombre=u"Joyería Hecha a Mano", descripcion="", padre=c, url="joyeria-hecha-mano")
	Categoria.objects.create(nombre=u"Regalos para Nerdos", descripcion="", padre=c, url="regalos-nerdos")
	Categoria.objects.create(nombre=u"Otros", descripcion="", padre=c, url="otros")
	# termino
