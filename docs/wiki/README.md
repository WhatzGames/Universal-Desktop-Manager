# Published user manual

Live Wiki: https://github.com/WhatzGames/Universal-Desktop-Manager/wiki

Owner initialized Home on 2026-10-28. Fourteen user pages plus _Sidebar.md were
published in signed Wiki commit `ee09dc3f040e119c8e0c00c600bf97ed42455c67`.
The live Getting Started page and fourteen-page navigation were checked in a browser.
The v0.2 user updates are published in signed Wiki commits `e0a3763` and `f5bb5ac`; all pages match
the source copies in draft PR #13. this README
is publication guidance and is not itself a Wiki page. No separate Wiki license adopted.

Both repositories follow My Flow layout:

- Bare Wiki Git data: `<workspace>/bares/Universal-Desktop-Manager.wiki.git`
- Wiki checkout: `<workspace>/worktrees/Universal-Desktop-Manager-wiki`, branch master
- SSH remote: `git@github-personal:WhatzGames/Universal-Desktop-Manager.wiki.git`
- Same author, personal SSH signing key and attribution hooks as the project repository

## Updating an initialized Wiki

Review user-facing edits in docs/wiki with the code PR. From the project checkout,
inspect the Wiki worktree for unrelated changes and fetch before copying. For an
authorized publication, copy only the fourteen manual pages and sidebar, not README.md:

```sh
git -C ../Universal-Desktop-Manager-wiki status --short
git -C ../Universal-Desktop-Manager-wiki fetch --all --prune
cp docs/wiki/{Home,Getting-Started,Installation,First-Launch,Quick-Start,Installing-Desktops,Switching-Desktops,X11-and-Wayland,Supported-Desktops,KDE-Plasma,Settings,Troubleshooting,Known-Limitations,FAQ,_Sidebar}.md ../Universal-Desktop-Manager-wiki/
git -C ../Universal-Desktop-Manager-wiki diff --check
git -C ../Universal-Desktop-Manager-wiki add '*.md'
git -C ../Universal-Desktop-Manager-wiki commit -S -m 'Update user manual'
git -C ../Universal-Desktop-Manager-wiki push origin master
```

Resolve any upstream divergence before pushing. Verify links and page rendering after
publication and record the Wiki commit in PROJECT_STATE.md. Keep planned features
clearly labeled; the foundation from PR #1 is merged, while v0.2 installation acceptance remains pending.

Signed Wiki commit `bb46dc8` publishes the snapshot approval and installation
limitations updates from integration PR #14. Installation acceptance remains open.
