# App 1.0.18 / Velnio 0.4.1

- Supports the exact P8 firmware 0.4.0 application profile with its existing addressed event, LED, gesture profile and health maps.
- Preserves support for firmware 0.3.0 and 0.2.0, full Settings, identities and session authority.
- Unknown firmware/map/variant combinations remain unsupported. Firmware flashing and the bootloader updater are outside this App release.

# App 1.0.17 / Velnio 0.4.0

- Adds addressed P8 firmware 0.3.0 event transport to the full Velnio integration.
- Preserves Settings, branch management, bindings, LED feedback and diagnostics.
- Uses the existing Velnio Installer slug so HA can offer a normal App update.
- Keeps the R4 payload, installer runtime and pruned base recipe unchanged.
- Includes matching ARM64/AMD64 source materials and license notices.
- Firmware flashing and qualification of 50 physical modules are outside this update.

# App 1.0.15 / Velnio 0.2.2 — experimental

- Separate Velnio Installer identity with default Velnio product and manual start.
- Exact previously qualified hosted AMD64 and ARM64 images, without rebuilding.
- Core restart request budgeting corrects the default first-start failure from the earlier internal candidate. The health polling default remains 180 seconds.
- Velnio 0.2.2 includes the empty-branch diagnostics correction.
- Publishes matching source materials, first-party license grant, upstream notices and checksums for controlled experimental evaluation.
- U4 and physical qualification remain open; U16 temperature and complete U23 health entities remain unfinished. Stable 1.0 / U36 is NO_GO.
