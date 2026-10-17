# Modern Diagram: Coord layout and link routing

## Coord convention

- Property name is `Coord` (`MVector<double,3>` on containers).
- Screen mapping: `scene ≈ kernel * 30` (`DEFAULT_COORD_SCALE` in `UModernDiagramCoordinateManager`).
- Preferred flow: left → right (inputs → processing → outputs).
- Dense horizontal chains (dendrites) use pitch **X ≈ 11** kernel units (`NPulseNeuron::BuildStructure`).
- `SetCoord` inside `Build` / `ApplyDiagramLayout` overwrites child positions on rebuild.

## Membrane segment internals (`NPulseMembrane::ABuild`)

Defaults match the polished `Dendrite1_85` layout (TimeNeuronTimeLearnerBranch/Test), with a wider Syn→Channel gap:

| N synapses / mechanism | Layout |
|------------------------|--------|
| **N = 1** | Exc: `ExcSynapse (0.3, 1.6)` → `ExcChannel (17.8, 1.6)`; Inh: `(0.3, 5.25)` → `(17.8, 5.25)` (ΔX = 1 block + 1.5 blocks) |
| **N > 1** | Synapses in a **left column** (`Y += i * 3.5`); channel on the **right** at mid-Y of that column. Inh row base = `max(5.25, 1.6 + N_exc * 3.5)` so it clears the Exc column. |

`NPulseMembraneIzhikevich` places `PosChannel` on the Exc-channel slot. Synapse `Trainer` stays at relative `(0, -3)`.

## Link enumeration (scope)

- Internal draw pass uses `scopeChildBoundaryLinksXmlFromModelScope` (personal links of direct children), matching classic `SaveComponentDrawInfo`.
- Recursive `GetComponentInternalLinks` is **not** used for drawing — nested feedback would collapse to peer self-loops on the parent node.
- External **incoming** (left): `UModernDiagramExternalSourceItem` + dashed link to local inputs; depth filter `isConnectorNestedInsideVisibleChild`.
  - External **outgoing** (right): `UModernDiagramExternalSinkItem` — one diamond per local output that has at least one consumer outside the current scope; label `Component:property` **relative to the current diagram scope** (current level name is omitted, e.g. on `Dendrite1_85` → `ExcChannel:Output`); single dashed stub from the local output port (no fan-out to each external consumer).
  - Resolution uses `UModernDiagramScopePath` / `resolveNodeByIdOnDiagram`: strip **current scope** from model-root ids, then take the visible top child (not the global first segment).
  - StructTrain sample: at **Neuron** scope, `Dendrite1_85.ExcChannel → Dendrite1_84.*` is an internal peer edge (no diamond). Drill into **Dendrite1_85** → two right diamonds (`ExcChannel:Output`, `InhChannel:Output`) for the sibling-channel exports.

## Link routing

- Implementation: `Rdk/GUI/Qt/UModernDiagramLinkRouter.{h,cpp}`.
- **Port invariant:** outputs on the **right**, inputs on the **left**. Reverse Manhattan paths leave the source to **+X** and enter the destination from **-X**.
- Modes (`RouteMode::Auto`):
  - **ExternalCorridor** — dashed external incoming: outside top/bottom envelope (no forced left detour); `parallelIndex` spreads fan-out lanes.
  - **OrthogonalAvoid** — reverse internal links (`start.x > end.x + ε`): H-ended Manhattan; never falls back to L→R cubic.
  - **CubicFallback** — forward internal links and external **outgoing** stubs (classic Bezier, horizontal tangents).
- Colors:
  - forward / external: `link.solid` (blue);
  - reverse: `link.reverse` (green) via `UStyleManager::getLinkReverseColor()`;
  - temp rubber-band: `link.dashed`.
- External **incoming** port placement (`layoutOptimal`, left):
  - X: `leftOfBounds` and `leftOfTargets`;
  - Y: target centers / **median** / span center, row samples, and outside `bounds±gap`;
  - scoring uses **ExternalCorridor**; **no** outside-band Y penalty when the port is already in the left pocket (fan-out bus);
  - left-pocket dashed routes prefer a shared vertical stem at `S.x` over a full top/bottom envelope (avoids kink piles for N≫1 tips).
- External **outgoing** sink placement (right): immediately to the **right of the source node** (`sinkTopLeftBesideSource`); auto-restored positions in the left input pocket are ignored. Settings group `UModernDiagramWidget_ExternalSinkPositions`.
- Wired from `UModernDiagramLinkItem::updateGeometry`.
