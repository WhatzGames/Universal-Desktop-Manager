//! UDM discovery controller and explicit restricted package workflow. No compositor.
pub mod compat;
pub mod discovery;
pub mod packages;
use bevy_app::{App, Plugin, Startup};
use bevy_ecs::prelude::*;
use serde::Serialize;

#[derive(Resource, Debug, Serialize)]
pub struct Snapshot {
    pub host: discovery::Host,
    pub sessions: Vec<discovery::Session>,
    pub desktops: Vec<compat::Desktop>,
    pub warnings: Vec<String>,
}

#[derive(Component)]
pub struct CatalogDesktop(pub compat::Desktop);

/// Loads precomputed discovery into ECS without performing host IO in a system.
pub struct DesktopCatalogPlugin;
impl Plugin for DesktopCatalogPlugin {
    fn build(&self, app: &mut App) {
        app.add_systems(Startup, load_catalog);
    }
}
fn load_catalog(mut commands: Commands, mut state: ResMut<Snapshot>) {
    for desktop in state.desktops.drain(..) {
        commands.spawn(CatalogDesktop(desktop));
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn plugin_loads_catalog_once() {
        let host = discovery::host(std::path::Path::new("/"), false).unwrap();
        let desktop = compat::kde(&host, &[]).unwrap();
        let mut app = App::new();
        app.insert_resource(Snapshot {
            host,
            sessions: vec![],
            desktops: vec![desktop],
            warnings: vec![],
        })
        .add_plugins(DesktopCatalogPlugin);
        app.update();
        app.update();
        let world = app.world_mut();
        assert_eq!(world.query::<&CatalogDesktop>().iter(world).count(), 1);
    }
}
