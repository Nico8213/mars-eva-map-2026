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

  // layers.json extent -> Leaflet bounds [[south, west], [north, east]].
  Cockpit.extentToBounds = function (extent) {
    return [
      [extent.min_northing_m, extent.min_easting_m],
      [extent.max_northing_m, extent.max_easting_m]
    ];
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
