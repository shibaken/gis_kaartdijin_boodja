var map = new ol.Map({
  target: 'map-container',
  layers: [
    new ol.layer.Tile({
      source: new ol.source.OSM(),
    }),
  ],
  view: new ol.View({
    center: ol.proj.fromLonLat([115.5, -24.5]),
    zoom: 4.6,
  }),
});

var url = '/api/catalogue/entries/'+id+'/layer';

var vectorSource = new ol.source.Vector({
  loader: function(extent, resolution, projection) {
    var xhr = new XMLHttpRequest();
    xhr.open('GET', url);
    xhr.setRequestHeader("Content-Type", "application/json")
    xhr.onload = function() {
      if (xhr.status == 200) {
        var data = JSON.parse(xhr.responseText)
        delete data.crs;
        var features = new ol.format.GeoJSON().readFeatures(data, { featureProjection: 'EPSG:3857' });
        vectorSource.addFeatures(features);
      }
    };
    xhr.send();
  },
});

var vectorLayer = new ol.layer.Vector({ source: vectorSource });
map.addLayer(vectorLayer);