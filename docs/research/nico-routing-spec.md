# Routing specification (written by Nico)

## 1. Goal
Find the lowest-cost walking route between two points of interest on the slope grid.

## 2. Cost function
- How slope turns into cost: <for example cost = 1 + (slope / limit)^2>
- Reason and source: <link>
- Cells steeper than <limit> degrees are blocked. Reason and source: <link>

## 3. Start and end points
- Rule for choosing them: <for example from the landing site to each point of interest in poi.geojson>

## 4. Validation
- Metric(s): <for example mean distance between our route and the Perseverance traverse>
- Parameters (locked before running): <list>
- Comparison segment(s): <which part of the traverse>

## 5. Comparison routes (F10)
- Data layer removed in each comparison: <list>
