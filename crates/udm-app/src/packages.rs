//! Explicit package commands. The default discovery command remains read-only.
use std::{io, process::Command};

const HELPER: &str = "/usr/libexec/udm-packages";

pub fn run(args: &[String]) -> io::Result<()> {
    let mut command = match args {
        [action] if action == "plan" || action == "verify" => {
            let mut command = Command::new(HELPER);
            command.arg(action);
            command
        }
        [action, digest] if action == "install" && valid_digest(digest) => {
            let mut command = Command::new("/usr/bin/pkexec");
            command.args([HELPER, "install", digest]);
            command
        }
        _ => {
            return Err(io::Error::new(
                io::ErrorKind::InvalidInput,
                "Usage: udm-app packages plan | verify | install REVIEWED_SHA256",
            ));
        }
    };
    let status = command.status()?;
    if status.success() {
        Ok(())
    } else {
        Err(io::Error::other(format!("Package helper exited {status}")))
    }
}

fn valid_digest(value: &str) -> bool {
    value.len() == 64
        && value
            .bytes()
            .all(|b| b.is_ascii_digit() || (b'a'..=b'f').contains(&b))
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn accepts_only_review_digest() {
        assert!(valid_digest(&"a".repeat(64)));
        for invalid in ["", "--help", "$(id)", &"a".repeat(63), &"G".repeat(64)] {
            assert!(!valid_digest(invalid));
        }
        assert!(run(&["shell".into()]).is_err());
        assert!(run(&["install".into(), "--help".into()]).is_err());
    }
}
