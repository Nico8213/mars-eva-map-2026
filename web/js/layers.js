// Layer manager: one imageOverlay per layers.json entry, with a visibility
// checkbox and an opacity slider per layer (F1).
(function () {
  'use strict';

  var Cockpit = window.Cockpit;
  var DEFAULT_OPACITY = 0.7;

  function addLayerRow(container, entry, index, overlay) {
    var map = Cockpit.map;
    var checkId = 'layer-' + index;
    var sliderId = 'layer-opacity-' + index;

    var row = document.createElement('div');
    row.className = 'layer-row';

    var check = document.createElement('input');
    check.type = 'checkbox';
    check.id = checkId;
    check.checked = true;

    var label = document.createElement('label');
    label.htmlFor = checkId;
    label.textContent = entry.name;

    var slider = document.createElement('input');
    slider.type = 'range';
    slider.id = sliderId;
    slider.min = '0';
    slider.max = '1';
    slider.step = '0.05';
    slider.value = String(DEFAULT_OPACITY);
    slider.setAttribute('aria-label', 'Opacity of ' + entry.name);

    // Remove or re-add the overlay. Its pane keeps the drawing order fixed.
    check.addEventListener('change', function () {
      if (check.checked) {
        map.addLayer(overlay);
      } else {
        map.removeLayer(overlay);
      }
    });

    // Update opacity without reloading the image.
    slider.addEventListener('input', function () {
      overlay.setOpacity(parseFloat(slider.value));
    });

    row.appendChild(check);
    row.appendChild(label);
    row.appendChild(document.createElement('br'));
    row.appendChild(slider);
    container.appendChild(row);
  }

  function buildLayers(entries) {
    var map = Cockpit.map;
    var container = document.getElementById('layer-controls');
    Cockpit.layerOverlays = [];

    entries.forEach(function (entry, index) {
      // One pane per layer: z-index follows list order (200 to 299).
      var paneName = 'layer-' + index;
      map.createPane(paneName).style.zIndex = 200 + index;

      var overlay = L.imageOverlay(
        Cockpit.layerUrl(entry.file),
        Cockpit.extentToBounds(entry.extent),
        { opacity: DEFAULT_OPACITY, alt: entry.name, interactive: false, pane: paneName }
      );

      // A failed image only affects this layer.
      overlay.on('error', function () {
        Cockpit.showError('Layer image failed to load: ' + entry.name);
      });

      overlay.addTo(map);
      Cockpit.layerOverlays.push(overlay);
      addLayerRow(container, entry, index, overlay);
    });
  }

  document.addEventListener('cockpit:layers-loaded', function (event) {
    buildLayers(event.detail);
  });
})();
