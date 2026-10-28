//! Read-only host and session discovery; session Exec values are never executed.
use serde::Serialize;
use std::{collections::BTreeMap, fs, io, path::Path};

#[derive(Debug, Serialize)]
pub struct Host {
    pub os: String,
    pub architecture: String,
    pub distribution: String,
    pub version: String,
    pub package_manager: Option<String>,
}

/// Parse literal os-release values without evaluating shell expansions.
pub fn fields(text: &str) -> BTreeMap<String, String> {
    text.lines()
        .filter_map(|line| {
            let line = line.trim();
            if line.starts_with('#') {
                return None;
            }
            let (key, value) = line.split_once('=')?;
            let value = value.trim();
            let value = value
                .strip_prefix('"')
                .and_then(|v| v.strip_suffix('"'))
                .or_else(|| value.strip_prefix('\'').and_then(|v| v.strip_suffix('\'')))
                .unwrap_or(value);
            Some((key.trim().to_owned(), value.to_owned()))
        })
        .collect()
}

pub fn host(root: &Path, linux: bool) -> io::Result<Host> {
    let mut result = Host {
        os: std::env::consts::OS.into(),
        architecture: std::env::consts::ARCH.into(),
        distribution: "unknown".into(),
        version: "unknown".into(),
        package_manager: None,
    };
    if !linux {
        return Ok(result);
    }
    let text = match fs::read_to_string(root.join("etc/os-release")) {
        Ok(text) => text,
        Err(e) if e.kind() == io::ErrorKind::NotFound => {
            fs::read_to_string(root.join("usr/lib/os-release"))?
        }
        Err(e) => return Err(e),
    };
    let data = fields(&text);
    result.distribution = data.get("ID").cloned().unwrap_or_else(|| "unknown".into());
    result.version = data
        .get("VERSION_ID")
        .cloned()
        .unwrap_or_else(|| "unknown".into());
    result.package_manager = ["apt-cache", "dnf", "pacman", "zypper"]
        .into_iter()
        .find(|name| root.join("usr/bin").join(name).is_file())
        .map(str::to_owned);
    Ok(result)
}

#[derive(Debug, Clone, Serialize)]
pub struct Session {
    pub id: String,
    pub name: String,
    pub backend: String,
    pub desktop: String,
    pub exec: String,
    pub try_exec: Option<String>,
}

pub fn session(text: &str, id: String, backend: &str) -> Option<Session> {
    let mut data = BTreeMap::new();
    let mut entry = false;
    for line in text.lines().map(str::trim) {
        if line.starts_with('[') {
            entry = line == "[Desktop Entry]";
            continue;
        }
        if entry
            && !line.starts_with('#')
            && let Some((k, v)) = line.split_once('=')
        {
            data.insert(k.trim(), v.trim());
        }
    }
    // Session definitions such as Debian Plasma can omit Type.
    if data.get("Type").is_some_and(|kind| *kind != "Application")
        || data.get("Hidden") == Some(&"true")
    {
        return None;
    }
    let name = data.get("Name").filter(|s| !s.is_empty())?;
    let exec = data.get("Exec").filter(|s| !s.is_empty())?;
    Some(Session {
        id,
        name: (*name).into(),
        backend: backend.into(),
        desktop: data.get("DesktopNames").unwrap_or(&"").to_string(),
        exec: (*exec).into(),
        try_exec: data.get("TryExec").map(|s| (*s).into()),
    })
}

pub fn sessions(root: &Path) -> io::Result<Vec<Session>> {
    let mut result = Vec::new();
    for (directory, backend) in [
        ("usr/share/wayland-sessions", "wayland"),
        ("usr/share/xsessions", "x11"),
    ] {
        let entries = match fs::read_dir(root.join(directory)) {
            Ok(entries) => entries,
            Err(e) if e.kind() == io::ErrorKind::NotFound => continue,
            Err(e) => return Err(e),
        };
        for entry in entries {
            let path = entry?.path();
            if path.extension().is_some_and(|s| s == "desktop") {
                let text = fs::read_to_string(&path)?;
                if let Some(s) = session(
                    &text,
                    path.file_name().unwrap().to_string_lossy().into(),
                    backend,
                ) {
                    result.push(s);
                }
            }
        }
    }
    result.sort_by(|a, b| (&a.backend, &a.id).cmp(&(&b.backend, &b.id)));
    Ok(result)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn filesystem_discovery_and_missing_directories() {
        let root = std::env::temp_dir().join(format!("udm-discovery-{}", std::process::id()));
        std::fs::create_dir_all(root.join("etc")).unwrap();
        std::fs::create_dir_all(root.join("usr/share/wayland-sessions")).unwrap();
        std::fs::write(root.join("etc/os-release"), "ID=debian\nVERSION_ID=13").unwrap();
        std::fs::write(
            root.join("usr/share/wayland-sessions/plasma.desktop"),
            include_str!("../tests/fixtures/plasmawayland.desktop"),
        )
        .unwrap();
        let h = host(&root, true).unwrap();
        assert_eq!(h.distribution, "debian");
        assert_eq!(h.version, "13");
        assert!(h.package_manager.is_none());
        let found = sessions(&root).unwrap();
        assert_eq!(found.len(), 1);
        assert_eq!(found[0].backend, "wayland");
        assert_eq!(found[0].desktop, "KDE");
        assert_eq!(found[0].name, "Plasma (Wayland)");
        assert_eq!(
            found[0].try_exec.as_deref(),
            Some("${CMAKE_INSTALL_FULL_BINDIR}/startplasma-wayland")
        );
        assert!(
            crate::compat::kde(&h, &found)
                .unwrap()
                .session_entry_present
        );
        std::fs::write(
            root.join("usr/share/wayland-sessions/invalid.desktop"),
            [255],
        )
        .unwrap();
        assert!(sessions(&root).is_err());
        std::fs::remove_dir_all(root).unwrap();
    }
    #[test]
    fn release_values_are_literal() {
        let f = fields("# comment\nID=debian\nVERSION_ID=\"13\"\nNAME='$(touch nope)'\n");
        assert_eq!(f["ID"], "debian");
        assert_eq!(f["VERSION_ID"], "13");
        assert_eq!(f["NAME"], "$(touch nope)");
    }
    #[test]
    fn sections_hidden_and_required_fields() {
        let entry = "[Desktop Entry]\nType=Application\nName=Plasma\nExec=startplasma-wayland\nDesktopNames=KDE\n[Other]\nHidden=true\n";
        let s = session(entry, "plasma.desktop".into(), "wayland").unwrap();
        assert_eq!(s.desktop, "KDE");
        assert_eq!(s.exec, "startplasma-wayland");
        assert!(
            session(
                &entry.replace("Type=Application", "Hidden=true"),
                "x".into(),
                "x11"
            )
            .is_none()
        );
        for kind in ["Link", "Directory", ""] {
            assert!(
                session(
                    &entry.replace("Type=Application", &format!("Type={kind}")),
                    "x".into(),
                    "wayland"
                )
                .is_none()
            );
        }
        assert!(
            session(
                "[Desktop Entry]\nType=Application\nName=X",
                "x".into(),
                "x11"
            )
            .is_none()
        );
    }
}
