# Video script (30 seconds)

Three versions of the same scene: how the data behind a route can be read on the map. Each version is 60 to 75 words of narration. Word counts cover the "Say" lines only, not the "Screen" notes.

## What the website has today

Checked in `web/index.html`, `web/js/*.js` and `.kiro/specs/c-web-cockpit/requirements.md`:

- Layers panel: a checkbox and an opacity slider for each layer (Terrain, Optical, Spectral).
- Overlays panel: switches for Points of interest and Routes.
- Points of interest: map markers and a list of buttons. A popup shows name, type, source and evidence.
- Routes: an orange line. A popup shows name, length, max slope, slope threshold, data used, start POI and end POI.
- Pointer readout in metres, a scale bar, and a banner saying the data is placeholder.

Not in the site yet, so not in any script: data cards, the comparison view, validation results, the environment panel, and the tablet and HUD pages.

## Before you record

- The layers, points and route in `web/public/data/` are marked DUMMY. The route is a hand-written line, not a router result. The scripts only describe what is on screen, and they do not say the route was computed. Re-record with real data when A and B deliver it.
- `validation/out/report.json` does not exist yet. No script contains a number.
- Keep the placeholder banner in frame while the data is dummy.

---

## Version A: build up the layers

1. **Say:** Martian Map shows where a Mars walk could go, and why.
   **Screen:** Open the site. In the Layers panel, untick Optical and Spectral. The Terrain image and the orange route are visible.
2. **Say:** Start with terrain, and slide its opacity until the ground shows through.
   **Screen:** Drag the Terrain opacity slider down and up. The image fades under the route.
3. **Say:** Now add the spectral layer.
   **Screen:** Tick Spectral in the Layers panel. The spectral image appears over the terrain.
4. **Say:** The route ends at a point marked from spectral data.
   **Screen:** In the Points of interest list, click "Dummy Site Beta (hydrous mineral detection)". The map pans and the popup shows Source: CRISM.
5. **Say:** Click the route to see which data it used.
   **Screen:** Click the orange line. The popup shows Data used, Start POI and End POI.
6. **Say:** Every layer can be switched off, so each dataset keeps a visible role.
   **Screen:** Untick and tick Terrain and Spectral in turn.
7. **Say:** Our aim is a map where the data explains the route.
   **Screen:** Hold on the full map with the route and all layers on.

Word count: 71

---

## Version B: follow the route from point to point

1. **Say:** Every route on this map starts and ends at a science site.
   **Screen:** Open the site. Show the whole map with the markers and the orange route.
2. **Say:** Pick a site in the list, and its popup opens.
   **Screen:** In the Points of interest list, click "Dummy Site Alpha (optical feature)". The map pans and a popup opens.
3. **Say:** This start point comes from optical imagery.
   **Screen:** Point at Source: optical in the popup.
4. **Say:** The end point comes from spectral data.
   **Screen:** Click "Dummy Site Beta (hydrous mineral detection)" in the list. Point at Source: CRISM in the popup.
5. **Say:** Click the orange line between them.
   **Screen:** Click the route line.
6. **Say:** The popup lists the data used, and shows the slope limit beside the steepest slope on the route.
   **Screen:** Point at Data used, Slope threshold and Max slope in the route popup.
7. **Say:** Each answer is a click away.
   **Screen:** Close the popup and hold on the full map.

Word count: 66

---

## Version C: switch the data on and off

1. **Say:** Which data does this route use?
   **Screen:** Open the site with all three layers on and the orange route in view.
2. **Say:** Let us look.
   **Screen:** Move the pointer to the Layers panel.
3. **Say:** Turn off optical and spectral, and only terrain remains under the route.
   **Screen:** Untick Optical and Spectral. The Terrain image and the route stay.
4. **Say:** Bring spectral back and compare.
   **Screen:** Tick Spectral. The spectral image appears again.
5. **Say:** Click the route, and the popup names the data used, plus the start and end points.
   **Screen:** Click the orange line. Point at Data used, Start POI and End POI.
6. **Say:** Hide the route, show it again, and judge each layer on its own.
   **Screen:** In the Overlays panel, untick and tick Routes. Drag one opacity slider.
7. **Say:** Martian Map keeps the evidence beside the route.
   **Screen:** Hold on the full map.

Word count: 63
