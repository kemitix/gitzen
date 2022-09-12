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

- `git zen init` - Install a commit-msg hook to add a zen-token to commits
- `git zen status` - Displays the status of the branch and its PRs
- `git zen push` - Push changes to Github, create and update PRs
- `git zen merge` - Merge any ready PRs and update/rebase dependant PRs

### Init

Git Zen keeps track of the PR that related to your commit by adding a zen token to each commit.
Running `git zen init` installs a commit-msg hook into your repo to add these tokens.

### Status

Fetch details of the user's pull requests from Github.
Display the status of each pull request.
If there are no PRs display "Stack is empty - no PRs found".
Doesn't make any remote changes.
Doesn't make any local changes.

### Push

Compare the local branch's unmerged commits with currently open pull requests in Github.
Create a new pull request for all new commits.
Update the pull request if a commit has been amended.
Where commits are reordered, pull requests will also be reordered to match.

## Requirements

- python 3.7+

## How it Works Example

You have three commits on a branch, that you want to submit for review and merge.
Each commit builds upon the work of the previous commits.
Each commit can be reviewed by different members of your team, based on their expertise.

```bash
git init demo
cd demo
git zen init
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

Each commit will include a `zen-token:.....` in their commit message, added by our commit-msg hook.

Running `git zen push` will:

```bash
git zen push
```

For the first commit:

- create a branch on `origin/main` (or `origin/master`): `gitzen/pr/${github-user}/${zen-token-1}`
- cherry pick the first commit onto this branch
- create a PR from `gitzen/pr/${github-user}/${zen-token-1}` onto `main` (or `master`)

For the second commit:

- create a branch on `gitzen/pr/${github-user}/${zen-token-1}`: `gitzen/pr/${github-user}/${zen-token-2}`
- cherry pick the second commit onto this branch
- create a PR from this branch `gitzen/pr/${github-user}/${zen-token-2}` onto `gitzen/pr/${github-user}/${zen-token-1}`
  - the PR includes a note or a check to not merge manually

For the third commit:

- create a branch on `gitzen/pr/${github-user}/${zen-token-2}`: `gitzen/pr/${github-user}/${zen-token-3}`
- cherry pick the third commit onto this branch
- create a PR from this branch `gitzen/pr/${github-user}/${zen-token-3}` onto `gitzen/pr/${github-user}/${zen-token-2}`
  - the PR includes a note or a check to not merge manually

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

For the first commit:

- the first commit has a zen-token: `zen-token-1`, so the PR branch is `gitzen/pr/${github-user}/${zen-token-1}`
- rebase `gitzen/pr/${github-user}/${zen-token-1}` onto `main` (or `master`)
- the first commit is cherry-picked onto `gitzen/pr/${github-user}/${zen-token-1}`
  - this results in the _changes_ that were made following the review being added as a new commit

For the second commit:

- the second commit has a zen-token: `zen-token-2`, so the PR branch is `gitzen/pr/${github-user}/${zen-token-2}`
- rebase `gitzen/pr/${github-user}/${zen-token-2}` onto `gitzen/pr/${github-user}/${zen-token-1}`
- the branch `gitzen/pr/${github-user}/${zen-token-2}` is rebased onto `gitzen/pr/${github-user}/${zen-token-1}`

For the third commit:

- the third commit has a zen-token: `zen-token-3`, so the PR branch is `gitzen/pr/${github-user}/${zen-token-3}`
- rebase `gitzen/pr/${github-user}/${zen-token-3}` onto `gitzen/pr/${github-user}/${zen-token-3}`
- the branch `gitzen/pr/${github-user}/${zen-token-3}` is rebased onto `gitzen/pr/${github-user}/${zen-token-2}`

The DB admin review your updated PR and approves it.
You can now merge your PR with `git zen merge`:

```bash
git zen merge
```

The default behaviour of git zen merge is to attempt to merge the first PR on your stack.

For the first commit:

- the PR for the branch `gitzen/pr/${github-user}/${zen-token-1}` is checked
  - is it mergable (approved, passing checks, no conflicts, etc)
  - ensure adding our single commit to remote upstream giveS the same tree as merging the branch?
- merge the PR using a squash merge

For the second commit:

- the PR for the branch `gitzen/pr/${github-user}/${zen-token-2}` is updated to
  - target the `main` (or `master`) branch
- for the third commit, there are no changes needed

### Zen Token

As the commits are updated, following review feedback, etc, the zen-token is used to keep track of the branches and prs created for each commit. The zen-token is simply a unique random hash.
