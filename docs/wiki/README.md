# Wiki publication

Wiki enabled; SSH inspection on 2026-10-28 returned Repository not found, consistent
with an uninitialized Wiki. These pages are ready to publish; they make no release claims.

Owner: open https://github.com/WhatzGames/Universal-Desktop-Manager/wiki and click
Create the first page, name it Home, paste Home.md, then save. This initializes Wiki Git.
Then (using the configured GitHub SSH alias):

```sh
git clone git@github-personal:WhatzGames/Universal-Desktop-Manager.wiki.git
cp docs/wiki/{Home,Getting-Started,KDE-Plasma,Known-Limitations,Troubleshooting}.md Universal-Desktop-Manager.wiki/
cd Universal-Desktop-Manager.wiki
git add '*.md'
git commit -S -m 'Add initial user manual'
git push origin master
```

Verify the Wiki default branch before pushing if GitHub creates a different branch.
GitHub requires first-page initialization through its web UI; unavailable Wiki Git
cannot be initialized by a normal clone. No separate wiki license has been adopted.
