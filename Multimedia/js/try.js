(function() {
	var cuerpo_pag = $(".container");
	var servs = $("#index-nvos-gs");

	var getLocation = function() {
		if (navigator.geolocation) {
			navigator.geolocation.getCurrentPosition(handlePosition);
		} else {
			cuerpo_pag.html("Su navegador no tiene funciones para la GeoLocalzación");
		}
	}

	var handlePosition = function(position) {
		var lat = position.coords.latitude;
		var lon = position.coords.longitude;
		$.post(url, {
			"lat": lat,
			"lon": lon },
			function(data) {
				servs.empty();
				$.each(data.features, function(index, val) {
					var name = val.properties.name;
					var description = val.properties.description;
					servs.append(name);
					servs.append(description);
					makeMap(val, lon, lat);
				});
			}); 
	}
	getLocation();
})();