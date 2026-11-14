// Cockpit entry point: creates the map and fits it to the layer extents.
// Layers, POIs and routes are added by later scripts (tasks 4 to 6).
(function () {
  'use strict';

  var Cockpit = window.Cockpit;

  // CRS name is not decided yet (INTERFACES.md, PRD 12.6). Do not invent one.
  Cockpit.crsLabel = 'TBD';

  // Plain image map in metre coordinates. No tile layer or base map is added.
  var map = L.map('map', {
    crs: L.CRS.Simple,
    minZoom: -6,
    maxZoom: 4,
    zoomSnap: 0.25,
    zoomDelta: 0.5,
    attributionControl: false
  });
  Cockpit.map = map;

  // Panes keep the drawing order fixed: layers < routes < POIs.
  // Layer panes (z-index 200 to 299) are created in layers.js.
  map.createPane('routes').style.zIndex = 450;
  map.createPane('poi').style.zIndex = 460;

  // One map unit is one metre, so the scale control shows metres and km.
  L.control.scale({ metric: true, imperial: false, position: 'bottomright' }).addTo(map);

  // Readout of pointer position in metres and the CRS label.
  var ReadoutControl = L.Control.extend({
    options: { position: 'bottomleft' },
    onAdd: function () {
      var div = L.DomUtil.create('div', 'coord-readout');
      div.textContent = 'E: - m, N: - m | CRS: ' + Cockpit.crsLabel;
      this._div = div;
      return div;
    },
    update: function (latlng) {
      this._div.textContent =
        'E: ' + latlng.lng.toFixed(1) + ' m, N: ' + latlng.lat.toFixed(1) +
        ' m | CRS: ' + Cockpit.crsLabel;
    }
  });
  var readout = new ReadoutControl().addTo(map);
  map.on('mousemove', function (e) { readout.update(e.latlng); });

  // Fit the view to the union of all layer extents.
  function fitToLayers(layerEntries) {
    var bounds = Cockpit.unionBounds(layerEntries);
    if (!bounds) {
      map.setView([0, 0], 0);
      return;
    }
    map.fitBounds(bounds);
    // Allow zooming out only a little past the full view, so the map is not lost.
    map.setMinZoom(map.getZoom() - 2);
  }

  // layers.json lives in layers/ next to the PNGs (see design.md).
  Cockpit.loadJson('layers/layers.json').then(function (layerEntries) {
    Cockpit.layerEntries = layerEntries;
    fitToLayers(layerEntries);
    // Tasks 4 to 6 hook in here once their scripts exist.
    document.dispatchEvent(new CustomEvent('cockpit:layers-loaded', { detail: layerEntries }));
  }).catch(function (err) {
    Cockpit.layerEntries = [];
    fitToLayers([]);
    Cockpit.showError(err.message);
  });
})();
