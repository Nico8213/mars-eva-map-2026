// Layer manager: one imageOverlay per layers.json entry, with a visibility
// checkbox and an opacity slider per layer, and a data card popup per layer.
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

    // Keyboard path to the data card popup (the map click needs a pointer).
    var info = document.createElement('button');
    info.type = 'button';
    info.className = 'layer-info';
    info.textContent = 'Data info';
    info.setAttribute('aria-label', 'Data card of ' + entry.name);
    info.addEventListener('click', function () {
      showInfo([entry], overlay.getBounds().getCenter());
    });

    row.appendChild(check);
    row.appendChild(label);
    row.appendChild(document.createElement('br'));
    row.appendChild(slider);
    row.appendChild(info);
    container.appendChild(row);
  }

  // Text for a card field; "n/a" when the field is missing or empty.
  function cardText(value) {
    if (value === undefined || value === null || value === '') { return 'n/a'; }
    return Array.isArray(value) ? value.join(', ') : String(value);
  }

  function addInfoRow(parent, label, text) {
    var row = document.createElement('div');
    var strong = document.createElement('strong');
    strong.textContent = label + ': ';
    row.appendChild(strong);
    row.appendChild(document.createTextNode(text));
    parent.appendChild(row);
  }

  // Popup content: one block per data card, listing the layers that use it.
  // Every value comes from data_cards.json and is written with textContent only.
  function buildInfoPopup(layerEntries) {
    var groups = [];  // [{ cardId, names: [] }] in layer order, one per card id
    layerEntries.forEach(function (entry) {
      var group = groups.filter(function (g) { return g.cardId === entry.data_card_id; })[0];
      if (!group) {
        group = { cardId: entry.data_card_id, names: [] };
        groups.push(group);
      }
      group.names.push(entry.name);
    });

    var box = document.createElement('div');
    groups.forEach(function (group) {
      var title = document.createElement('h3');
      title.className = 'popup-title';
      title.textContent = group.names.join(', ');
      box.appendChild(title);

      var card = Cockpit.findCard(group.cardId);
      if (!card) {
        addInfoRow(box, 'Data card', 'not found (' + cardText(group.cardId) + ')');
        return;
      }
      addInfoRow(box, 'Product', cardText(card.product));
      addInfoRow(box, 'Resolution', cardText(card.resolution));
      addInfoRow(box, 'License', cardText(card.license));
    });
    return box;
  }

  function showInfo(layerEntries, latlng) {
    var ready = Cockpit.dataCardsReady || Promise.resolve();
    ready.then(function () {
      L.popup({ maxWidth: 320 })
        .setLatLng(latlng)
        .setContent(buildInfoPopup(layerEntries))
        .openOn(Cockpit.map);
    });
  }

  function buildLayers(entries) {
    var map = Cockpit.map;
    var container = document.getElementById('layer-controls');
    Cockpit.layerOverlays = [];

    // Click on the map: show the data cards of the visible layers under the pointer.
    map.on('click', function (event) {
      var hits = entries.filter(function (entry, index) {
        var overlay = Cockpit.layerOverlays[index];
        return overlay && map.hasLayer(overlay) && overlay.getBounds().contains(event.latlng);
      });
      if (hits.length) { showInfo(hits, event.latlng); }
    });

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
