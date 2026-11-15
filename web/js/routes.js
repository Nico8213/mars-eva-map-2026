// Route display: polylines from routes/route_<name>.geojson files listed in
// routes/index.json. Numbers are shown as stored; nothing is computed here.
(function () {
  'use strict';

  var Cockpit = window.Cockpit;

  var ROUTE_COLOR = '#ff7043';
  var ROUTE_WEIGHT = 4;
  var ROUTE_WEIGHT_HOVER = 7;
  var CASING_WEIGHT = 8;
  var CASING_WEIGHT_HOVER = 11;
  // Stroke width of the invisible click layer (pixels).
  var HIT_WEIGHT = 20;

  // The only popup fields. Labels are these property names; values are read from the feature.
  var POPUP_KEYS = ['name', 'length_m', 'max_slope_deg', 'slope_threshold_deg', 'data_used', 'cost_function'];

  function valueText(value) {
    if (value === undefined || value === null) { return ''; }
    return Array.isArray(value) ? value.join(', ') : String(value);
  }

  function addRow(parent, label, text) {
    var row = document.createElement('div');
    var strong = document.createElement('strong');
    strong.textContent = label + ': ';
    row.appendChild(strong);
    row.appendChild(document.createTextNode(text));
    parent.appendChild(row);
  }

  function buildPopup(props) {
    var box = document.createElement('div');
    POPUP_KEYS.forEach(function (key) {
      addRow(box, key, valueText(props[key]));
    });
    return box;
  }

  // Route points are projected metres [easting, northing]. Convert them to image
  // pixels with the grid.json origin and pixel size, then place the pixels inside
  // the image extent, so routes use the same map units as the layers and POIs.
  function gridToLatLng(grid) {
    var v = Cockpit.extentToBounds(Cockpit.layerEntries[0].extent); // [[south, west], [north, east]]
    return function (coord) {
      var col = (coord[0] - grid.top_left_x_m) / grid.pixel_size_m;
      var row = (grid.top_left_y_m - coord[1]) / grid.pixel_size_m;
      return L.latLng(
        v[1][0] - (row / grid.height) * (v[1][0] - v[0][0]),
        v[0][1] + (col / grid.width) * (v[1][1] - v[0][1])
      );
    };
  }
  // Draw one route: a dark casing line below a bright line, so it is visible
  // on every layer. A third, invisible wide line takes the clicks.
  function drawRoute(feature, group, grid) {
    var toLatLng = gridToLatLng(grid);
    var casing = L.geoJSON(feature, {
      coordsToLatLng: toLatLng,
      pane: 'routes',
      interactive: false,
      style: function () { return { color: '#000', weight: CASING_WEIGHT, opacity: 0.8 }; }
    });
    // The visible line is display only. Its 4 px stroke is too thin to hit reliably.
    var line = L.geoJSON(feature, {
      coordsToLatLng: toLatLng,
      pane: 'routes',
      interactive: false,
      style: function () { return { color: ROUTE_COLOR, weight: ROUTE_WEIGHT, opacity: 1 }; }
    });
    // Invisible wide line on top of the others. It handles the click and hover.
    var hit = L.geoJSON(feature, {
      coordsToLatLng: toLatLng,
      pane: 'routes',
      // A route click must not also open the layer popup.
      bubblingMouseEvents: false,
      style: function () { return { color: '#000', weight: HIT_WEIGHT, opacity: 0, lineCap: 'round', lineJoin: 'round' }; },
      onEachFeature: function (f, layer) {
        layer.bindPopup(function () { return buildPopup(f.properties || {}); });
        layer.on('mouseover', function () {
          line.setStyle({ weight: ROUTE_WEIGHT_HOVER });
          casing.setStyle({ weight: CASING_WEIGHT_HOVER });
        });
        layer.on('mouseout', function () {
          line.setStyle({ weight: ROUTE_WEIGHT });
          casing.setStyle({ weight: CASING_WEIGHT });
        });
      }
    });
    group.addLayer(casing);
    group.addLayer(line);
    group.addLayer(hit);
  }

  // Legend entry for routes. Only the label and the note below are written here.
  function addLegendItem() {
    var list = document.getElementById('legend');
    if (!list) { return; }
    var item = document.createElement('li');
    var swatch = document.createElement('span');
    swatch.className = 'legend-swatch';
    swatch.style.background = ROUTE_COLOR;
    swatch.setAttribute('aria-hidden', 'true');
    var name = document.createElement('strong');
    name.textContent = 'Route';
    var note = document.createElement('span');
    note.textContent = 'slope constraint only';
    item.appendChild(swatch);
    item.appendChild(name);
    item.appendChild(note);
    list.appendChild(item);
  }

  function addToggle(group) {
    var map = Cockpit.map;
    var row = document.createElement('div');
    var check = document.createElement('input');
    check.type = 'checkbox';
    check.id = 'toggle-routes';
    check.checked = true;
    var label = document.createElement('label');
    label.htmlFor = 'toggle-routes';
    label.textContent = 'Routes';
    row.appendChild(check);
    row.appendChild(label);
    document.getElementById('overlay-controls').appendChild(row);

    check.addEventListener('change', function () {
      if (check.checked) { map.addLayer(group); } else { map.removeLayer(group); }
    });
  }

  var NO_DATA_MESSAGE = 'No route data available yet';

  function loadRoutes() {
    var map = Cockpit.map;
    var group = L.layerGroup();
    var drawn = 0;

    // Grid parameters are required for the conversion; any failure ends in the catch below.
    Cockpit.loadJson('grid.json').then(function (grid) {
      return Cockpit.loadJson('routes/index.json').then(function (files) {
        if (!Array.isArray(files)) { throw new Error('routes/index.json is not a list'); }
        // One failed file must not stop the others.
        return Promise.allSettled(files.map(function (file) {
          return Cockpit.loadJson('routes/' + file).then(function (feature) {
            if (!feature || !feature.geometry || feature.geometry.type !== 'LineString') {
              Cockpit.showError('Route file is not a LineString Feature: routes/' + file);
              return;
            }
            drawRoute(feature, group, grid);
            drawn += 1;
          });
        }));
      });
    }).then(function (results) {
      var failedFiles = results.filter(function (r) { return r.status === 'rejected'; });
      if (failedFiles.length || drawn === 0) {
        console.log(NO_DATA_MESSAGE);
      }
      if (drawn === 0) { return; }
      Cockpit.routeLayer = group;
      group.addTo(map);
      addToggle(group);
      addLegendItem();
    }).catch(function () {
      console.log(NO_DATA_MESSAGE);
    });
  }

  document.addEventListener('cockpit:map-ready', loadRoutes);
})();