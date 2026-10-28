use bevy_app::App;
use std::path::Path;
use udm_app::{CatalogDesktop, DesktopCatalogPlugin, Snapshot, compat, discovery};

fn main() -> Result<(), Box<dyn std::error::Error>> {
    if std::env::args_os().len() != 1 {
        return Err("Usage: udm-app (read-only JSON report; no options)".into());
    }
    let linux = cfg!(target_os = "linux");
    let host = discovery::host(Path::new("/"), linux)?;
    let sessions = if linux {
        discovery::sessions(Path::new("/"))?
    } else {
        vec![]
    };
    let desktops = vec![compat::kde(&host, &sessions)?];
    let warnings = vec!["Read-only discovery. No installs, session activation or live switching implemented. Session launchability and GPU support are unverified.".into()];
    let mut app = App::new();
    app.insert_resource(Snapshot {
        host,
        sessions,
        desktops,
        warnings,
    })
    .add_plugins(DesktopCatalogPlugin);
    app.update();
    let world = app.world_mut();
    let desktops = world
        .query::<&CatalogDesktop>()
        .iter(world)
        .map(|d| &d.0)
        .collect::<Vec<_>>();
    let state = world.resource::<Snapshot>();
    println!(
        "{}",
        serde_json::to_string_pretty(&serde_json::json!({
            "schema_version": 1, "host": state.host, "sessions": state.sessions,
            "desktops": desktops, "warnings": state.warnings,
        }))?
    );
    Ok(())
}
