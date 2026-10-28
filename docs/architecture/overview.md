# Architecture and status

Implemented: one Cargo member, udm-app, with discovery and compatibility modules, a
headless Bevy plugin, an ECS desktop component and a snapshot resource. Discovery IO
happens before the startup system; the plugin only loads data. The one-shot executable
prints structured JSON and exits. No renderer or graphics backend is linked by design.
Split crates only when independent runtime or API boundaries justify them.

Proposed: independent Smithay/calloop compositor, Bevy controller and restricted Polkit
package helper communicating through typed IPC. Live Wayland handles stay in the
compositor. Management UI failure must not terminate clients. Smithay is not a dependency
of v0.1, and no compositor compatibility claim has been tested.

Three future modes: custom live shell on one retained compositor; isolated nested native
session with original apps remaining in the host; standard native login with possible
logout. None supports universal live migration between native desktop compositors.

See [ADR](../adr/0001-foundation.md), [design](../design/discovery.md), and
[master plan](../development/master-plan.md) for preservation and security contracts.
