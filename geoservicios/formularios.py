#! /usr/bin/env python
# -*- coding: utf-8 -*-


import re
from django import forms
from django.utils.html import escape
from django.core.exceptions import ValidationError

##################
##    Validar
##################


def validar_usuario(dato):
	if dato and dato:
		try:
			coincidencia = re.match("^[a-z][a-zA-Z0-9]*$", dato)
			coincidencia.groups()
		except:
			raise ValidationError(u"%s no es un nombre correcto de usuario" % dato)




##################
##    Formularios
##################

class FormBuscar(forms.Form):
	consulta = forms.CharField(max_length=250, required=True)

	def clean_consulta(self):
		data = self.cleaned_data["consulta"]
		return escape(str(data))


class FormSesionar(forms.Form):
	usuario = forms.CharField(max_length=250, required=True, validators=[validar_usuario])
	contra = forms.CharField(max_length=250, required=True)


class FormRegistrar(forms.Form):
	usuario = forms.CharField(max_length=250, required=True, validators=[validar_usuario])
	contra = forms.CharField(max_length=250, required=True)
