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

- python 3.10  (developed against python 3.10.6, but may work on earlier versions)

