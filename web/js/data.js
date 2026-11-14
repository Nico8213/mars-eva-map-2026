// Data helpers shared by all cockpit scripts.
// Data coordinates are projected metres: x = easting_m, y = northing_m.
// L.CRS.Simple uses LatLng(lat, lng) with lat as the vertical axis, so
// northing maps to lat and easting maps to lng. No reprojection is done.
(function () {
  'use strict';

  var Cockpit = (window.Cockpit = window.Cockpit || {});

  // Relative URL so the site also works under a sub-path (GitHub Pages).
  Cockpit.DATA_ROOT = 'public/data/';

  // Fetch a JSON file from the data root. Throws an Error that names the path.
  Cockpit.loadJson = function (path) {
    var url = Cockpit.DATA_ROOT + path;
    return fetch(url).then(function (response) {
      if (!response.ok) {
        throw new Error('Could not load ' + path + ' (HTTP ' + response.status + ')');
      }
      return response.json();
    }).catch(function (err) {
      // Network and parse errors: keep the file name in the message.
      if (err && err.message && err.message.indexOf(path) !== -1) {
        throw err;
      }
      throw new Error('Could not load ' + path + ': ' + (err && err.message ? err.message : err));
    });
  };

  // [easting_m, northing_m] -> Leaflet LatLng. Also usable as the
  // coordsToLatLng option of L.geoJSON (it only reads indexes 0 and 1).
  Cockpit.toLatLng = function (coord) {
    return L.latLng(coord[1], coord[0]);
  };

  // Two extent formats are accepted:
  //   projected metres (INTERFACES.md): min_easting_m, min_northing_m, max_easting_m, max_northing_m
  //   geographic degrees (current output of A): west, east, south, north
  // In both cases the first value of a point is x (easting or longitude) and
  // the second is y (northing or latitude). Nothing is reprojected.
  function extentValues(extent) {
    var v = (extent && 'west' in extent)
      ? { w: extent.west, s: extent.south, e: extent.east, n: extent.north, unit: 'deg' }
      : {
        w: extent && extent.min_easting_m, s: extent && extent.min_northing_m,
        e: extent && extent.max_easting_m, n: extent && extent.max_northing_m, unit: 'm'
      };
    [v.w, v.s, v.e, v.n].forEach(function (value) {
      if (typeof value !== 'number' || !isFinite(value)) {
        throw new Error('Layer extent has an unknown format. Expected min_/max_ easting/northing in m, or west/east/south/north in degrees.');
      }
    });
    return v;
  }

  // layers.json extent -> Leaflet bounds [[south, west], [north, east]].
  Cockpit.extentToBounds = function (extent) {
    var v = extentValues(extent);
    return [[v.s, v.w], [v.n, v.e]];
  };

  // Unit of the map coordinates for one extent: 'm' (metres) or 'deg' (degrees).
  Cockpit.extentUnit = function (extent) {
    return extentValues(extent).unit;
  };

  // Image URL for a layer file. INTERFACES.md says "relative to layers/", but the
  // current output of A writes "layers/<name>.png" (relative to the data folder).
  // Both forms are accepted.
  Cockpit.layerUrl = function (file) {
    var prefix = file.indexOf('layers/') === 0 ? '' : 'layers/';
    return Cockpit.DATA_ROOT + prefix + file;
  };

  // Smallest bounds that contain every layer extent, or null for an empty list.
  Cockpit.unionBounds = function (layerEntries) {
    var bounds = null;
    layerEntries.forEach(function (entry) {
      var b = L.latLngBounds(Cockpit.extentToBounds(entry.extent));
      bounds = bounds ? bounds.extend(b) : b;
    });
    return bounds;
  };

  // Data cards (data_cards.json), keyed by card id. Popups read the license and
  // other fields from here; no license text is written in the code.
  Cockpit.dataCards = new Map();

  // Load and parse data_cards.json. Resolves when done, also when the file is
  // missing or invalid (an error is shown in the status region and the map keeps working).
  Cockpit.loadDataCards = function () {
    Cockpit.dataCardsReady = Cockpit.loadJson('data_cards.json').then(function (cards) {
      if (!Array.isArray(cards)) {
        throw new Error('data_cards.json must be a JSON array');
      }
      cards.forEach(function (card) {
        if (card && card.id !== undefined) { Cockpit.dataCards.set(card.id, card); }
      });
    }).catch(function (err) {
      Cockpit.showError(err.message);
    });
    return Cockpit.dataCardsReady;
  };

  // The data card whose id matches a layer's data_card_id, or null.
  Cockpit.findCard = function (cardId) {
    return Cockpit.dataCards.get(cardId) || null;
  };

  // Show an error in the status region. Text is set with textContent only.
  Cockpit.showError = function (message) {
    var status = document.getElementById('status');
    if (!status) { return; }
    var line = document.createElement('div');
    line.className = 'error';
    line.textContent = message;
    status.appendChild(line);
  };
})();
