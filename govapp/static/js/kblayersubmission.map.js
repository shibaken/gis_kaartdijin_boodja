// import GeoJSON from "/govapp/frontend/node_modules/ol/format/GeoJSON";
// import Map from "/node_modules/ol/Map";
// import VectorLayer from '/node_modules/ol/layer/Vector';
// import VectorSource from '/node_modules/ol/source/Vector';
// import View from '/node_modules/ol/View';

// import OSM from '/frontend/node_modules/ol/source/OSM';
// import TileLayer from '/frontend/node_modules/ol/layer/Tile';
// import {Map, View} from '/frontend/node_modules/ol';
// import {fromLonLat} from '/frontend/node_modules/ol/proj';

import OSM from '/static/ol/source/OSM.js';
import TileLayer from '/static/ol/layer/Tile.js';
import Map from '/static/ol/Map.js';
import View from '/static/ol/View.js';
import {fromLonLat} from '/static/ol/proj.js';

new Map({
  target: 'map-container',
  layers: [
    new TileLayer({
      source: new OSM(),
    }),
  ],
  view: new View({
    center: fromLonLat([0, 0]),
    zoom: 2,
  }),
});
