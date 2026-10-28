# Frequently asked questions

**Can I switch from GNOME to KDE without losing my windows?** No. Switching is not
implemented, and arbitrary window migration between their native compositors is not
promised by the project.

**Does available mean safe to install?** No. It means a candidate was found in local
package metadata. Dependencies, conflicts and graphics readiness are not validated.

**Why is KDE listed when I have not installed it?** The catalog represents desktops
you may investigate; session-entry presence is reported separately.

**Does UDM need sudo or internet access?** The report needs neither. It reads local
files and supported package metadata. A source build needs dependencies available on
the build machine; offline hardware testing can use a transferred test executable.
