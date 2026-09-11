# Modern Diagram: Coord layout and link routing

## Coord convention

- Property name is `Coord` (`MVector<double,3>` on containers).
- Screen mapping: `scene ≈ kernel * 30` (`DEFAULT_COORD_SCALE` in `UModernDiagramCoordinateManager`).
- Preferred flow: left → right (inputs → processing → outputs).
- Dense horizontal chains (dendrites) use pitch **X ≈ 11** kernel units (`NPulseNeuron::BuildStructure`).
- `SetCoord` inside `Build` / `ApplyDiagramLayout` overwrites child positions on rebuild.

## Link routing

- Implementation: `Rdk/GUI/Qt/UModernDiagramLinkRouter.{h,cpp}`.
- **Port invariant:** outputs on the **right**, inputs on the **left**. Reverse Manhattan paths leave the source to **+X** and enter the destination from **-X**.
- Modes (`RouteMode::Auto`):
  - **CubicFallback** — forward internal links and **external dashed** incoming (classic Bezier, horizontal tangents).
  - **OrthogonalAvoid** — **only** reverse internal links (`start.x > end.x + ε`): H-ended Manhattan around the row; never falls back to L→R cubic (wrong port tangents).
  - **ExternalCorridor** — optional explicit mode (outside envelope); not selected by `Auto`.
- Colors:
  - forward / external: `link.solid` (blue);
  - reverse: `link.reverse` (green) via `UStyleManager::getLinkReverseColor()`;
  - temp rubber-band: `link.dashed`.
- External port placement (`layoutOptimal`): searches **X** (`leftOfBounds` and `leftOfTargets`) and **Y**.
- Wired from `UModernDiagramLinkItem::updateGeometry`.
