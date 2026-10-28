//! Only Debian 13's local APT cache is queried; no refresh, resolution or installation.
use crate::discovery::{Host, Session};
use serde::Serialize;
use std::{io, process::Command};

#[derive(Debug, Clone, PartialEq, Eq, Serialize)]
#[serde(rename_all = "snake_case")]
pub enum Availability {
    Available,
    Unavailable,
    Unknown,
    Unsupported,
}

#[derive(Debug, Serialize)]
pub struct Desktop {
    pub id: String,
    pub name: String,
    pub session_entry_present: bool,
    pub launchability: String,
    pub availability: Availability,
    pub evidence: String,
    pub live_switch_capable: bool,
}

pub fn apt_candidate(text: &str, success: bool) -> Availability {
    if !success {
        return Availability::Unknown;
    }
    match text
        .lines()
        .find_map(|l| l.trim().strip_prefix("Candidate:"))
    {
        Some(v) if v.trim() == "(none)" => Availability::Unavailable,
        Some(v) if !v.trim().is_empty() => Availability::Available,
        _ => Availability::Unknown,
    }
}

pub fn kde(host: &Host, sessions: &[Session]) -> io::Result<Desktop> {
    let present = sessions.iter().any(|s| {
        s.backend == "wayland"
            && (s.desktop.split(';').any(|d| d == "KDE")
                || s.exec.split_whitespace().next().is_some_and(|e| {
                    e.ends_with("/startplasma-wayland") || e == "startplasma-wayland"
                }))
    });
    let mut d = Desktop { id: "kde-plasma-wayland".into(), name: "KDE Plasma Wayland".into(),
        session_entry_present: present, launchability: "unverified: entry presence does not prove executable or graphics readiness".into(),
        availability: Availability::Unsupported, evidence: "Package query supports Debian 13 with /usr/bin/apt-cache only; other releases are unvalidated".into(), live_switch_capable: false };
    if host.os == "linux"
        && host.distribution == "debian"
        && host.version == "13"
        && host.package_manager.as_deref() == Some("apt-cache")
    {
        // shortcut: synchronous local query can stall; bound execution before adding interactive workflows.
        let out = Command::new("/usr/bin/apt-cache")
            .args(["policy", "kde-plasma-desktop"])
            .env("LC_ALL", "C")
            .output()?;
        d.availability = apt_candidate(&String::from_utf8_lossy(&out.stdout), out.status.success());
        d.evidence = format!(
            "Local APT cache policy for kde-plasma-desktop, exit {}; cache freshness, Wayland dependencies and installability unverified",
            out.status
        );
    }
    Ok(d)
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn apt_status_does_not_overclaim() {
        assert_eq!(
            apt_candidate("  Candidate: 4:6.3.5", true),
            Availability::Available
        );
        assert_eq!(
            apt_candidate("  Candidate: (none)", true),
            Availability::Unavailable
        );
        assert_eq!(apt_candidate("", true), Availability::Unknown);
        assert_eq!(apt_candidate("Candidate: 1", false), Availability::Unknown);
    }
    #[test]
    fn non_linux_has_catalog_but_no_support() {
        let h = Host {
            os: "macos".into(),
            architecture: "aarch64".into(),
            distribution: "unknown".into(),
            version: "unknown".into(),
            package_manager: None,
        };
        let d = kde(&h, &[]).unwrap();
        assert!(!d.session_entry_present);
        assert!(!d.live_switch_capable);
        assert_eq!(d.availability, Availability::Unsupported);
    }
}
