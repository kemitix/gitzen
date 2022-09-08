# gitzen

Stacked PR Manager for Git/Github

![GitZen Logo](./logo/gitzen-logo-256.webp)

> Inspired by <https://github.com/ejoffe/spr/> and <https://github.com/getcord/spr>.

I want to combine the power of ejoffe's `git spr status`, `update` and `merge` commands, with getcord's ability to add meaningful commits to existing PRs, rather than by simply force-pushing the change.

## Exploratory Notes

The first steps are to figure out the underlying git commands that are used to create and update the PRs.

## Settings

Various options will be controlled by a `.gitzen` file that the user can manage in their repo.

## Commands

Base executable is `git-zen`. It can be used a `git zen`. I recommend setting an alias `alias gz="git zen"`.

- `gz status` - Displays the status of the branch and its PRs
- `gz push` - Push changes to GitHub, create and update PRs
- `gz merge` - Merge any ready PRs and update/rebase depdendant PRs

### Status

Fetch details of the user's pull requests from github.
Display the status of each pull request.
If there are no PRs display "Stack is empty - no PRs found".
Doesn't make any remote changes.
Doesn't make any local changes.

## Push

Compare the local branch's unmerged commits with currently open pull requests in github.
Create a new pull request for all new commits.
Update the pull request if a commit has been amended.
Where commits are reordered, pull requests will also be reordered to match.

## Requirements

- python 3.7+

## How it Works

You have three commits on a branch, that you want to submit for review and merge.
Each commit builds upon the work of the previous commits.
Each commit can be reviewed by different members of your team, based on their expertise.

```bash
git init demo
cd demo
touch database
git add database
git commit -m"[button-foo] Add db support"
touch backend
git add backend
git commit -m"[button-foo] Add backend"
touch frontend
git add frontend
git commit -m"[button-foo] Add frontend"
```

Running `git zen push` will:

```bash
git zen push
```

- generate a zen-token for each commit
- rebase all three commits to add the zen-token into their body (zen-token-[1-3])
- create a branch on origin/main (or origin/master): `gz/pr/${zen-token-1}`
- cherry pick the first commit onto this branch
- create a PR from this branch `gz/pr/${zen-token-1}` onto `main`
- create a branch on `gz/pr/${zen-token-1}`: `gz/pr/${zen-token-2}`
- cherry pick the second commit onto this branch
- create a PR from this branch `gz/pr/${zen-token-2}` onto `gz/pr/${zen-token-1}`
  - the PR includes a note or a check to not merge manuall
- create a branch on `gz/pr/${zen-token-2}`: `gz/pr/${zen-token-3}`
- cherry pick the third commit onto this branch
- create a PR from this branch `gz/pr/${zen-token-3}` onto `gz/pr/${zen-token-2}`
  - the PR includes a note or a check to not merge manuall

We now have three PRs, chained on top of each other using branches that consist of cherry-picked commits from our own branch.

A DB admin reviews your first PR and asks you to change an index definition.
You update the commit, rebasing your branch, and use git zen push to update the PRs.

```bash
git rebase -i @{upstream}
# edit the database index
git add database
git commit --amend --no-edit
git rebase --continue
git zen push
```

This time, git zen push will:

- the first commit has a zen-token: `zen-token-1`, so the PR branch is `gz/pr/${zen-token-1}`
- the first commit is cherry-picked onto `gz/pr/${zen-token-1}`
  - this results in the _changes_ that were made following the review being added as a new commit
- the second commit has a zen-token: `zen-token-2`, so the PR branch is `gz/pr/${zen-token-2}`
- the branch `gz/pr/${zen-token-2}` is rebased onto `gz/pr/${zen-token-1}`
- the third commit has a zen-token: `zen-token-3`, so the PR branch is `gz/pr/${zen-token-3}`
- the branch `gz/pr/${zen-token-3}` is rebased onto `gz/pr/${zen-token-2}`

The DB admin review your updated PR and approves it.
You can now merge your PR with `git zen merge`:

```bash
git zen merge
```

The default behaviour of git zen merge is to attempt to merge the first PR on your stack.

- for the first commit, the branch `gz/pr/${zen-token-1}` is checked
  - is it mergable (approved, passing checks, no conflicts, etc)
  - ensure adding our single commit to remote upstream give the same tree as merging the branch?
- merge the PR using a squash merge
- for the second commit, the branch `gz/pr/${zen-token-2}` is updated
  - rebase on `main` (or `master`)
  - update the PR to target the main branch
- for the third commit, there are no changes needed

### Zen Token

As the commits are updated, following review feedback, etc, the zen-token is used to keep track of the branches and prs created for each commit. The zen-token is simply a unique random hash.
