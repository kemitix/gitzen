from typing import List, Optional

from faker import Faker

from gitzen.models.commit_pr import CommitPr
from gitzen.models.git_commit import GitCommit
from gitzen.models.github_commit import GithubCommit
from gitzen.models.github_pull_request import PullRequest
from gitzen.types import (
    CommitBody,
    CommitHash,
    CommitTitle,
    CommitWipStatus,
    GitBranchName,
    GithubRepoId,
    GithubUsername,
    GitRemoteName,
    PullRequestBody,
    PullRequestId,
    PullRequestMergeable,
    PullRequestNumber,
    PullRequestReviewDecision,
    PullRequestTitle,
    ZenToken,
)

fake = Faker()


def hex(length: int) -> str:
    return fake.hexify("^" * length)


def gen_zen_token() -> ZenToken:
    return ZenToken(hex(8))


def gen_pr_id() -> PullRequestId:
    return PullRequestId(hex(20))


def gen_pr_number() -> PullRequestNumber:
    return PullRequestNumber(fake.numerify("#" * 4))


def gen_pr_title() -> PullRequestTitle:
    return PullRequestTitle(fake.sentence())


def gen_pr_body() -> PullRequestBody:
    return PullRequestBody(fake.paragraphs())


def gen_git_branch_name() -> GitBranchName:
    return GitBranchName(fake.domain_word())


def gen_remote_name() -> GitRemoteName:
    return GitRemoteName(fake.domain_word())


def gen_gh_username() -> GithubUsername:
    return GithubUsername(fake.slug())


def gen_pr_mergeable() -> PullRequestMergeable:
    return PullRequestMergeable(fake.word())


def gen_pr_review_decision() -> PullRequestReviewDecision:
    return PullRequestReviewDecision(fake.word())


def gen_gh_repo_id() -> GithubRepoId:
    return GithubRepoId(hex(10))


def gen_commit_hash() -> CommitHash:
    return CommitHash(hex(40))


def gen_commit_title(wip: bool = False) -> CommitTitle:
    return CommitTitle(fake.sentence())


def gen_commit_body(token: Optional[ZenToken]) -> CommitBody:
    paras: List[str] = fake.paragraphs()
    if token:
        paras.append(f"zen-token:{token.value}")
    body = "\n\n".join(paras)
    return CommitBody(body)


def gen_gh_commit(
    token: Optional[ZenToken],
    wip: bool = False,
) -> GithubCommit:
    if token:
        zen_token = token
    else:
        zen_token = gen_zen_token()
    return GithubCommit(
        zen_token,
        gen_commit_hash(),
        gen_commit_title(wip),
        gen_commit_body(zen_token),
        CommitWipStatus(wip),
    )


def gen_commit(
    token: Optional[ZenToken],
    wip: bool = False,
) -> GitCommit:
    if token:
        zen_token = token
    else:
        zen_token = gen_zen_token()
    return GitCommit(
        zen_token,
        gen_commit_hash(),
        gen_commit_title(wip),
        gen_commit_body(zen_token),
        CommitWipStatus(wip),
    )


def gen_pr(
    token: Optional[ZenToken],
    wip: bool = False,
) -> PullRequest:
    if token:
        zen_token = token
    else:
        zen_token = gen_zen_token()
    commit = gen_gh_commit(zen_token, wip)
    return PullRequest(
        gen_pr_id(),
        zen_token,
        gen_pr_number(),
        gen_gh_username(),
        gen_pr_title(),
        gen_pr_body(),
        gen_git_branch_name(),
        gen_git_branch_name(),
        commit.hash,
        gen_pr_mergeable(),
        gen_pr_review_decision(),
        gen_gh_repo_id(),
        commits=[commit],
    )


def gen_commit_pr() -> CommitPr:
    token = gen_zen_token()
    return CommitPr(gen_commit(token), gen_pr(token))
