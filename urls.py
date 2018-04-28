from django.conf.urls import patterns, url, include

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('geoservicios.views',
	url('^$', 'inicio'),
	url('^/busca-gs/$', 'inicio', name="encuentra-servs-geo"),

	url('^sesionarme/$', 'sesionar_usr'),
	url('^cierre-sesion/$', 'cerrar_sesion'),
	url('^registrarme/$', 'registrar_usr'),

	url('^perfil/(?P<usr>[a-zA-Z0-9_]+)/$', 'perfil'),
	url('^configuracion/$', 'configurar_cta'),
	url('^borrar-cta/$', 'borrar_cta'),

	url('^categoria/(?P<cat>[a-zA-Z-]+)/$', 'ver_categoria'),
	url('^categoria/(?P<cat>[a-zA-Z-]+)/(?P<subcat>[a-zA-Z-]+)/$', 'ver_subcategoria'),
	url('^categoria/(?P<cat>[a-zA-Z-]+)/[a-zA-Z-+]+/(?P<serv>[0-9a-zA-Z-_()!\.,\']+)/$', 'ver_servicio'),
	url('^buscar?$', 'buscar'),
	url('^cuadroHonor/$', 'ver_cuadro_honor'),

	url('^enlistar-usuario/(?P<usr>[a-zA-Z0-9_]+)/$', 'enlistar_usuario'),
	url('^lista-solicitudes-servicio/$', 'lista_solicitudes_servicio'),
	url('^crear-servicio/$', 'crear_servicio'),
	url('^sugerencia/$', 'sugerir'),
	url('^contacto/$', 'contactarnos'),


	url('^i18n/', include('django.conf.urls.i18n')),
	# xHACER:  url('^borrar/(?P<id_tlmsj>\\d+)/$', 'borrar'),

	# te-hago-un-mono-con-tus-tripas-internas-te-perforare-las-orejas-con-tus-unas-pa-que-seas-serio-oiste"

	# Uncomment the admin/doc line below to enable admin documentation:
	# url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

	# Uncomment the next line to enable the admin:
	# url(r'^admin/', include(admin.site.urls)),
)
