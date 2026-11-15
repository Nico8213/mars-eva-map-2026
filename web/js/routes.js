// Route display: polylines from routes/route_<name>.geojson files listed in
// routes/index.json. Numbers are shown as stored; nothing is computed here.
(function () {
  'use strict';

  var Cockpit = window.Cockpit;

  function isMissing(value) {
    return value === undefined || value === null;
  }

  function formatValue(value, unit) {
    if (isMissing(value)) { return 'n/a'; }
    if (Array.isArray(value)) { return value.length ? value.join(', ') : 'n/a'; }
    return unit ? value + ' ' + unit : String(value);
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
    var title = document.createElement('h3');
    title.className = 'popup-title';
    title.textContent = 'Route ' + formatValue(props.name);
    box.appendChild(title);
    addRow(box, 'Length', formatValue(props.length_m, 'm'));
    addRow(box, 'Max slope', formatValue(props.max_slope_deg, 'deg'));
    addRow(box, 'Slope threshold', formatValue(props.slope_threshold_deg, 'deg'));
    addRow(box, 'Data used', formatValue(props.data_used));
    addRow(box, 'Start POI', formatValue(props.start_poi));
    addRow(box, 'End POI', formatValue(props.end_poi));
    return box;
  }

  // Draw one route: a dark casing line below a bright line, so it is visible
  // on every layer. Only the bright line is clickable.
  function drawRoute(feature, group) {
    var casing = L.geoJSON(feature, {
      coordsToLatLng: Cockpit.toLatLng,
      pane: 'routes',
      interactive: false,
      style: function () { return { color: '#000', weight: 8, opacity: 0.8 }; }
    });
    var line = L.geoJSON(feature, {
      coordsToLatLng: Cockpit.toLatLng,
      pane: 'routes',
      style: function () {
        // A route click must not also open the layer popup.
        return { color: '#ff7043', weight: 4, opacity: 1, bubblingMouseEvents: false };
      },
      onEachFeature: function (f, layer) {
        layer.bindPopup(function () { return buildPopup(f.properties || {}); });
      }
    });
    group.addLayer(casing);
    group.addLayer(line);
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

  // Route data may not exist yet. A missing or unreadable index or route file
  // (HTTP 404, network error, invalid JSON) is not an error for the user: log one
  // line and leave the map as it is.
  var NO_DATA_MESSAGE = 'No route data available yet';

  function loadRoutes() {
    var map = Cockpit.map;
    var group = L.layerGroup();
    var drawn = 0;

    return Cockpit.loadJson('routes/index.json').then(function (files) {
      if (!Array.isArray(files)) { throw new Error('routes/index.json is not a list'); }
      // One failed file must not stop the others.
      return Promise.allSettled(files.map(function (file) {
        return Cockpit.loadJson('routes/' + file).then(function (feature) {
          if (!feature || !feature.geometry || feature.geometry.type !== 'LineString') {
            // The file loaded but has the wrong content: tell the user.
            Cockpit.showError('Route file is not a LineString Feature: routes/' + file);
            return;
          }
          drawRoute(feature, group);
          drawn += 1;
        });
      }));
    }).then(function (results) {
      // A route file that cannot be loaded is skipped; the others are still drawn.
      var failedFiles = results.filter(function (r) { return r.status === 'rejected'; });
      if (failedFiles.length || drawn === 0) {
        console.log(NO_DATA_MESSAGE);
      }
      if (drawn === 0) { return; }
      Cockpit.routeLayer = group;
      group.addTo(map);
      addToggle(group);
    }).catch(function () {
      // Index missing or unreadable. Exit without throwing.
      console.log(NO_DATA_MESSAGE);
    });
  }

  document.addEventListener('cockpit:map-ready', loadRoutes);
})();
