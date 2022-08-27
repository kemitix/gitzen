#!/usr/bin/env python

import subprocess
import json
import jmespath

print("`git zen status` - prototype")

query = """
query($repo_name: String!){
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
}
"""
print("Querying Github...")
# GraphQL originally from https://github.com/ejoffe/spr/blob/9597afc52354db66d4b419f7ee7a9bd7eacdf70f/github/githubclient/gen/genclient/operations.go#L72
json = json.loads(subprocess.run(['gh', 'api', 'graphql', '-F', "repo_name={repo}", '-f', f"query={query}"], stdout=subprocess.PIPE).stdout)

myPRs = jmespath.search('data.viewer.repository.pullRequests.nodes', json)
numPRs = len(myPRs)
if numPRs == 0:
	print('Stack is empty - no PRs found')
	exit

for pr in myPRs:
	n = pr['number']
	m = pr['mergeable']
	t = pr['title']
	print(f'PR-{n} - {m} - {t}')
