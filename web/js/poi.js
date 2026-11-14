// Points of interest: circle markers from poi.geojson with a click popup.
// Data strings are written with textContent only, never as HTML.
(function () {
  'use strict';

  var Cockpit = window.Cockpit;

  // Marker colour per source value. Colours are handed out in order of first use,
  // so no source name is written in the code. The source is also named in the popup.
  var PALETTE = ['#ffd54f', '#4fc3f7', '#81c784', '#ba68c8', '#ff8a65', '#e0e0e0'];
  var sourceColors = {};

  function colorFor(source) {
    var key = String(source);
    if (!Object.prototype.hasOwnProperty.call(sourceColors, key)) {
      sourceColors[key] = PALETTE[Object.keys(sourceColors).length % PALETTE.length];
    }
    return sourceColors[key];
  }

  function addRow(parent, label, value) {
    var row = document.createElement('div');
    var strong = document.createElement('strong');
    strong.textContent = label + ': ';
    row.appendChild(strong);
    row.appendChild(document.createTextNode(value === undefined || value === null ? 'n/a' : String(value)));
    parent.appendChild(row);
  }

  function buildPopup(props) {
    var box = document.createElement('div');
    var title = document.createElement('h3');
    title.className = 'popup-title';
    title.textContent = props.name === undefined ? 'n/a' : props.name;
    box.appendChild(title);
    addRow(box, 'Type', props.type);
    addRow(box, 'Source', props.source);
    addRow(box, 'Evidence', props.evidence);
    return box;
  }

  function buildPoi(poi) {
    var map = Cockpit.map;
    var markers = [];

    var layer = L.geoJSON(poi, {
      coordsToLatLng: Cockpit.toLatLng,
      pointToLayer: function (feature, latlng) {
        var color = colorFor(feature.properties.source);
        return L.circleMarker(latlng, {
          pane: 'poi',
          bubblingMouseEvents: false, // a POI click must not also open the layer popup
          radius: 8,
          color: '#000',
          weight: 2,
          fillColor: color,
          fillOpacity: 0.95
        });
      },
      onEachFeature: function (feature, marker) {
        marker.bindPopup(function () { return buildPopup(feature.properties); });
        markers.push({ feature: feature, marker: marker });
      }
    }).addTo(map);
    Cockpit.poiLayer = layer;

    // Group toggle in the Overlays fieldset.
    var toggleRow = document.createElement('div');
    var check = document.createElement('input');
    check.type = 'checkbox';
    check.id = 'toggle-poi';
    check.checked = true;
    var label = document.createElement('label');
    label.htmlFor = 'toggle-poi';
    label.textContent = 'Points of interest';
    toggleRow.appendChild(check);
    toggleRow.appendChild(label);
    document.getElementById('overlay-controls').appendChild(toggleRow);

    check.addEventListener('change', function () {
      if (check.checked) { map.addLayer(layer); } else { map.removeLayer(layer); }
    });

    // Keyboard path: one button per POI opens its popup.
    var list = document.getElementById('poi-list');
    markers.forEach(function (item) {
      var props = item.feature.properties;
      var li = document.createElement('li');
      var button = document.createElement('button');
      button.type = 'button';
      button.textContent = (props.name || 'n/a') + ' (' + (props.type || 'n/a') + ')';
      button.addEventListener('click', function () {
        if (!check.checked) {
          check.checked = true;
          map.addLayer(layer);
        }
        map.panTo(item.marker.getLatLng());
        item.marker.openPopup();
      });
      li.appendChild(button);
      list.appendChild(li);
    });
  }

  document.addEventListener('cockpit:map-ready', function () {
    Cockpit.loadJson('poi.geojson').then(buildPoi).catch(function (err) {
      Cockpit.showError(err.message);
    });
  });
})();
