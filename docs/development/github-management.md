# GitHub management handoff

Verified 2026-10-28: initial main had LICENSE and .gitignore only, no workflows/issues/
milestones; branch metadata reported unprotected. Protection endpoint returned 404
with the local CLI account, so organization rules are not fully audited.

Owner granted integration access; earlier PR/issue 403 errors are resolved.
PR #1 is open and unmerged: https://github.com/WhatzGames/Universal-Desktop-Manager/pull/1
Eight open enhancement tasks #2–#9 link the PR, acceptance criteria and validation.
Do not recreate them from github-tasks.json. Keep open until reviewed/merged.

No milestone-creation connector exists. Local gh account lacks owner write access;
browser is signed out. Proposed temporary GitHub Actions workflow was rejected by
automatic approval review because issues:write automation requires explicit scope
approval. No such workflow is committed or active. Proposal: create only v0.1, v0.2,
v0.3, v0.4, v0.5, v0.6, v0.7–v0.9 and v1.0 with phase names from roadmap.md; assign
issues #2–#9 and PR #1 to v0.1; remove the workflow after success. Never close issues,
change code/main, or merge through that workflow.

Alternative owner-authenticated commands:

```sh
gh api repos/WhatzGames/Universal-Desktop-Manager/milestones -f title=v0.1 -f description='Foundation and discovery; planned, not released; see docs/development/roadmap.md'
gh issue edit 2 --repo WhatzGames/Universal-Desktop-Manager --milestone v0.1
```

Repeat milestone creation for remaining phases and assignment for issues #3–#9/PR #1.
Wiki initialization and exact publishing instructions: ../wiki/README.md.
