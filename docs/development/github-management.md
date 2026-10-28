# GitHub management handoff

Verified 2026-10-28: main had only LICENSE and .gitignore, no workflows/issues/milestones,
and branch metadata reported unprotected. Protection endpoint returned 404 with the
local CLI account, so organization rules are not fully audited. Connected app reports
admin permission but create_issue returned 403 Resource not accessible by integration.
The connector has no milestone-creation tool. Browser is signed out; local gh authenticates
as a different account with read-only repository permission. Do not change credentials.

No issues or milestones were created. With an owner-authenticated gh session, create
milestones v0.1, v0.2, v0.3, v0.4, v0.5, v0.6, v0.7–v0.9 and v1.0 using the phase names
and acceptance criteria in roadmap.md (plans, not releases). Create the eight scoped
v0.1 tasks from github-tasks.json, assign them to v0.1 and link the setup PR. Inspect for
duplicates first; covered tasks stay open until the PR merges. Then update PROJECT_STATE.md.

Example owner commands (review before publishing):

```sh
gh api repos/WhatzGames/Universal-Desktop-Manager/milestones -f title=v0.1 -f description='Foundation and discovery; see docs/development/roadmap.md'
gh issue create --repo WhatzGames/Universal-Desktop-Manager --title 'v0.1: Workspace foundation' --milestone v0.1 --body-file /path/to/reviewed-body.md
```

Wiki initialization and exact publishing instructions: ../wiki/README.md.
