#!/usr/bin/env bash
set -e
echo "\`git zen status\` - prototype"

JSON=$(gh pr list --json id,number,title,baseRefName,headRefName,mergeable,reviewDecision,headRepository,headRepositoryOwner,commits,statusCheckRollup)
NUMBER_OF_PRS=$(echo ${JSON} | jq '.|length')

if test $NUMBER_OF_PRS -eq 0
then
    echo "Stack is empty - no PRs found"
    exit
fi

for i in $(seq 0 $(($NUMBER_OF_PRS - 1)))
do
    echo ${PRJSON} | jq ".[$i]"
    NUMBER=$(echo ${JSON} | jq ".[$i].number")
    MERGEABLE=$(echo ${JSON} | jq ".[$i].mergeable")
    TITLE=$(echo ${JSON} | jq ".[$i].title")
    echo -n "PR-$NUMBER"
    echo -n " - $MERGEABLE"
    echo -n " - $TITLE"
    echo ""
done
