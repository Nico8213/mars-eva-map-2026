// Cockpit entry point: creates the map and fits it to the layer extents.
// Layers, POIs and routes are added by the other scripts in js/.
(function () {
  'use strict';

  var Cockpit = window.Cockpit;

  // The CRS name is not decided yet (see docs/INTERFACES.md). Do not invent one.
  Cockpit.crsLabel = 'TBD';

  // Unit of the map coordinates: 'm' (projected metres) or 'deg' (geographic degrees).
  // It is set from the layer extents once layers.json has loaded.
  Cockpit.coordUnit = 'm';

  // Plain image map. No tile layer or base map is added.
  // The zoom range is wide on purpose: an extent of 0.07 degrees needs zoom 13 or
  // more to fill the screen. It is narrowed after the view is fitted (fitToLayers).
  var map = L.map('map', {
    crs: L.CRS.Simple,
    minZoom: -10,
    maxZoom: 20,
    zoomSnap: 0.25,
    zoomDelta: 0.5,
    attributionControl: false
  });
  Cockpit.map = map;

  // Panes keep the drawing order fixed: layers < routes < POIs.
  // Layer panes (z-index 200 to 299) are created in layers.js.
  map.createPane('routes').style.zIndex = 450;
  map.createPane('poi').style.zIndex = 460;

  // Readout of pointer position and the CRS label. Metres: E/N. Degrees: lon/lat.
  var ReadoutControl = L.Control.extend({
    options: { position: 'bottomleft' },
    onAdd: function () {
      var div = L.DomUtil.create('div', 'coord-readout');
      div.textContent = 'Move the pointer over the map | CRS: ' + Cockpit.crsLabel;
      this._div = div;
      return div;
    },
    update: function (latlng) {
      var text;
      if (Cockpit.coordUnit === 'deg') {
        text = 'Lon: ' + latlng.lng.toFixed(5) + ' deg, Lat: ' + latlng.lat.toFixed(5) + ' deg';
      } else {
        text = 'E: ' + latlng.lng.toFixed(1) + ' m, N: ' + latlng.lat.toFixed(1) + ' m';
      }
      this._div.textContent = text + ' | CRS: ' + Cockpit.crsLabel;
    }
  });
  var readout = new ReadoutControl().addTo(map);
  map.on('mousemove', function (e) { readout.update(e.latlng); });

  // Tell the other scripts that the map exists and has a view
  // (POI and route scripts listen for this; vector layers need a view first).
  function announceMapReady() {
    document.dispatchEvent(new CustomEvent('cockpit:map-ready'));
  }

  // Fit the view to the union of all layer extents.
  function fitToLayers(layerEntries) {
    var bounds = Cockpit.unionBounds(layerEntries);
    if (layerEntries.length) {
      Cockpit.coordUnit = Cockpit.extentUnit(layerEntries[0].extent);
    }
    if (!bounds) {
      map.setView([0, 0], 0);
      return;
    }
    map.fitBounds(bounds);
    // Allow zooming out a little past the full view and in a few levels, so the
    // map is not lost and the image is not zoomed into blur forever.
    var fitZoom = map.getZoom();
    map.setMinZoom(fitZoom - 2);
    map.setMaxZoom(fitZoom + 4);

    // The scale control measures in map units, so it is only correct for metres.
    // For degrees it would print wrong distances, so it is left out.
    if (Cockpit.coordUnit === 'm') {
      L.control.scale({ metric: true, imperial: false, position: 'bottomright' }).addTo(map);
    }
  }

  // Start loading the data cards early; popups wait for them when needed.
  Cockpit.loadDataCards();

  // layers.json lives in layers/ next to the PNGs.
  Cockpit.loadJson('layers/layers.json').then(function (layerEntries) {
    Cockpit.layerEntries = layerEntries;
    fitToLayers(layerEntries);
    // layers.js builds the layer menu when it receives this event.
    document.dispatchEvent(new CustomEvent('cockpit:layers-loaded', { detail: layerEntries }));
    announceMapReady();
  }).catch(function (err) {
    Cockpit.layerEntries = [];
    fitToLayers([]);
    Cockpit.showError(err.message);
    announceMapReady();
  });
})();
