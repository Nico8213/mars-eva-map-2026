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
  function drawRoute(feature, group, grid) {
    var toLatLng = Cockpit.toLatLng;

    // 根据 Austin 的要求，如果存在 grid.json，则将网格米(Easting/Northing)转换为页面坐标(x/y)
    if (grid && grid.pixel_size_m) {
      toLatLng = function (coords) {
        var easting = coords[0];
        var northing = coords[1];
        var x = (easting - grid.top_left_x_m) / grid.pixel_size_m;
        var y = (grid.top_left_y_m - northing) / grid.pixel_size_m;
        return Cockpit.toLatLng([x, y]);
      };
    }

    var casing = L.geoJSON(feature, {
      coordsToLatLng: toLatLng,
      pane: 'routes',
      interactive: false,
      style: function () { return { color: '#000', weight: 8, opacity: 0.8 }; }
    });
    var line = L.geoJSON(feature, {
      coordsToLatLng: toLatLng,
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

  var NO_DATA_MESSAGE = 'No route data available yet';

  function loadRoutes() {
    var map = Cockpit.map;
    var group = L.layerGroup();
    var drawn = 0;

    // 优先读取 grid.json 获取网格参数，再去渲染 routes
    Cockpit.loadJson('grid.json').catch(function () {
      return null; // 如果文件不存在则安全降级，不抛出异常
    }).then(function (grid) {
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
    }).catch(function () {
      console.log(NO_DATA_MESSAGE);
    });
  }

  document.addEventListener('cockpit:map-ready', loadRoutes);
})();