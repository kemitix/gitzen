#!/usr/bin/env bash

set -e

DIR=$(mktemp -d)
function cleanup() {
	rm -rf "${DIR}"
}
trap cleanup EXIT
echo "Workdir: ${DIR}"

# create repo
cd "${DIR}"
git init

mkdir -p .git/refs/gitzen/patches

# create initial stack
touch file1
git add file1
git commit -m"Add file 1"

touch file2
git add file2
git commit -m"Add file 2"

touch file3
git add file3
git commit -m"Add file 3"

# gitzen push
# patches do not exists - create them
# create a patch for each commit
git rev-parse HEAD~2 >.git/refs/gitzen/patches/token1
git rev-parse HEAD~1 >.git/refs/gitzen/patches/token2
git rev-parse HEAD >.git/refs/gitzen/patches/token3
# we use origin-* to simulate remote branches origin/*
# given that all branch are local we will not use git push to update them
# create pr branches
git branch gitzen/pr/kemitix/master/token1 refs/gitzen/patches/token1
# pr: merge gitzen/pr/kemitix/master/token1 onto master
git branch gitzen/pr/kemitix/token1/token2 refs/gitzen/patches/token2
# pr: merge gitzen/pr/kemitix/token1/token2 onto gitzen/pr/kemitix/master/token1
git branch gitzen/pr/kemitix/token2/token3 refs/gitzen/patches/token3
# pr: merge gitzen/pr/kemitix/token2/token3 onto gitzen/pr/kemitix/token1/token2

# now amend file1 and push again
# simulate a git rebase
git reset --hard HEAD~2
date >file1
git add file1
git commit --amend --no-edit

# continue with simulate git rebase --continue
git cherry-pick refs/gitzen/patches/token2
git cherry-pick refs/gitzen/patches/token3

# continue with gitzen push
# patches already exists - update them
git rev-parse HEAD~2 >.git/refs/gitzen/patches/token1
git rev-parse HEAD~1 >.git/refs/gitzen/patches/token2
git rev-parse HEAD >.git/refs/gitzen/patches/token3

# add new patches to each PR branch
git switch gitzen/pr/kemitix/master/token1
# git rebase origin/master
git cherry-pick -x refs/gitzen/patches/token1

git switch gitzen/pr/kemitix/token1/token2
git rebase gitzen/pr/kemitix/master/token1
git cherry-pick -x refs/gitzen/patches/token2 || git cherry-pick --skip

git switch gitzen/pr/kemitix/token2/token3
git rebase gitzen/pr/kemitix/token1/token2
git cherry-pick -x refs/gitzen/patches/token3 || git cherry-pick --skip

# finally - log
git switch master
git log --all --graph --decorate --patch
