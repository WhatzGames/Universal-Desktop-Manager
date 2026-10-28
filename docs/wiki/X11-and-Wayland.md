# X11 and Wayland

X11 and Wayland are display-system protocols used by Linux desktops. UDM currently
lists their standard system session definitions; it does not start either display
server. Xwayland can let X11 applications run under a Wayland compositor, but does not
transfer running windows from one display server to another. No compositor, Xwayland
integration or window-preserving desktop switching is implemented in UDM yet.
