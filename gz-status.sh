#!/usr/bin/env bash
set -e
echo "\`git zen status\` - prototype"

echo "Querying Github..."
# GraphQL originally from https://github.com/ejoffe/spr/blob/9597afc52354db66d4b419f7ee7a9bd7eacdf70f/github/githubclient/gen/genclient/operations.go#L72
JSON=$(gh api graphql -F repo_owner='{owner}' -F repo_name='{repo}' \
    -f query='query($repo_owner: String!, $repo_name: String!){
		viewer {
			login
			repository(name: $repo_name) {
				pullRequests(first: 100, states: [OPEN]) {
					nodes {
						id
						number
						title
						baseRefName
						headRefName
						mergeable
						reviewDecision
						repository {
							id
						}
						commits(first: 100) {
							nodes {
								commit {
									oid
									messageHeadline
									messageBody
									statusCheckRollup {
										state
									}
								}
							}
						}
					}
				}
			}
		}
		repository(owner: $repo_owner, name: $repo_name) {
			id
		}
    }')

REPO_ID=$(echo ${JSON} | jq .data.repository.id)
MY_PRS=$(echo ${JSON} | jq .data.viewer.repository.pullRequests.nodes)
NUMBER_OF_PRS=$(echo ${MY_PRS} | jq '.|length')

if test $NUMBER_OF_PRS -eq 0
then
    echo "Stack is empty - no PRs found"
    exit
fi

for i in $(seq 0 $(($NUMBER_OF_PRS - 1)))
do
    #echo ${MY_PRS} | jq ".[$i]"
    NUMBER=$(echo ${MY_PRS} | jq ".[$i].number")
    MERGEABLE=$(echo ${MY_PRS} | jq ".[$i].mergeable")
    TITLE=$(echo ${MY_PRS} | jq ".[$i].title")
    echo -n "PR-$NUMBER"
    echo -n " - $MERGEABLE"
    echo -n " - $TITLE"
    echo ""
done
