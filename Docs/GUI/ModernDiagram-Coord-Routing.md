# Modern Diagram: Coord layout and link routing

## Coord convention

- Property name is `Coord` (`MVector<double,3>` on containers).
- Screen mapping: `scene ≈ kernel * 30` (`DEFAULT_COORD_SCALE` in `UModernDiagramCoordinateManager`).
- Preferred flow: left → right (inputs → processing → outputs).
- Dense horizontal chains (dendrites) use pitch **X ≈ 11** kernel units (`NPulseNeuron::BuildStructure`).
- `SetCoord` inside `Build` / `ApplyDiagramLayout` overwrites child positions on rebuild.

## Link enumeration (scope)

- Internal draw pass uses `scopeChildBoundaryLinksXmlFromModelScope` (personal links of direct children), matching classic `SaveComponentDrawInfo`.
- Recursive `GetComponentInternalLinks` is **not** used for drawing — nested feedback would collapse to peer self-loops on the parent node.
- External incoming keeps its own depth filter (`isConnectorNestedInsideVisibleChild`).

## Link routing

- Implementation: `Rdk/GUI/Qt/UModernDiagramLinkRouter.{h,cpp}`.
- **Port invariant:** outputs on the **right**, inputs on the **left**. Reverse Manhattan paths leave the source to **+X** and enter the destination from **-X**.
- Modes (`RouteMode::Auto`):
  - **ExternalCorridor** — dashed external incoming: outside top/bottom envelope (no forced left detour); `parallelIndex` spreads fan-out lanes.
  - **OrthogonalAvoid** — reverse internal links (`start.x > end.x + ε`): H-ended Manhattan; never falls back to L→R cubic.
  - **CubicFallback** — forward internal links (classic Bezier, horizontal tangents).
- Colors:
  - forward / external: `link.solid` (blue);
  - reverse: `link.reverse` (green) via `UStyleManager::getLinkReverseColor()`;
  - temp rubber-band: `link.dashed`.
- External port placement (`layoutOptimal`):
  - X: `leftOfBounds` and `leftOfTargets`;
  - Y: target centers, row samples, and **outside** `bounds±gap` candidates;
  - scoring uses **ExternalCorridor** (live obstacleHits) plus a penalty for Y inside the node band.
- Wired from `UModernDiagramLinkItem::updateGeometry`.
