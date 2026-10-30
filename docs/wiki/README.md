# User manual publication

The user-facing manual is published at
https://github.com/WhatzGames/Universal-Desktop-Manager/wiki.
The Markdown pages in this directory are its reviewed source; README.md is developer
publication guidance, not a Wiki page. No separate Wiki license is adopted.

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

Resolve upstream divergence before pushing. Verify links, page rendering and source
content after publication. Keep planned features clearly labeled and describe tested
behavior with its practical limits.
