from pydantic import BaseModel, Field
from datetime import datetime, timezone

class RepositoryRecord(BaseModel):
    id: int
    name: str
    owner_id: int
    owner_login: str
    description: str | None = None
    forks_count: int
    stargazers_count: int
    watchers_count: int
    topics: str  # stored as comma-separated string e.g. "deep-learning,gpu,python"
    created_at: datetime
    pushed_at: datetime
    repo_category: str # 'legacy' or 'llm'
    load_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def from_api_response(cls, data: dict, category: str) -> "RepositoryRecord":
        return cls(
            id=data["id"],
            name=data["name"],
            owner_id=data["owner"]["id"],
            owner_login=data["owner"]["login"],
            description=data.get("description"),
            forks_count=data["forks_count"],
            stargazers_count=data["stargazers_count"],
            watchers_count=data["watchers_count"],
            topics=",".join(data.get("topics", [])),
            created_at=data["created_at"],
            pushed_at=data["pushed_at"],
            repo_category=category
        )

class StarRecord(BaseModel):
    repo_id: int
    repo_full_name: str
    user_id: int
    user_login: str
    starred_at: datetime
    load_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def from_api_response(cls, data: dict, repo_id: int, repo_full_name: str) -> "StarRecord":
        return cls(
            repo_id=repo_id,
            repo_full_name=repo_full_name,
            user_id=data["user"]["id"],
            user_login=data["user"]["login"],
            starred_at=data["starred_at"]
        )

class CommitRecord(BaseModel):
    sha: str
    commit_date: datetime
    author_id: int | None = None
    author_login: str | None = None
    committer_id: int | None = None
    committer_login: str | None = None
    repo_id: int
    load_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @classmethod
    def from_api_response(cls, data: dict, repo_id: int) -> "CommitRecord":
        return cls(
            sha=data["sha"],
            repo_id=repo_id,
            commit_date=data.get("commit", {}).get("author", {}).get("date"),
            author_id=data.get("author", {}).get("id"),
            author_login=data.get("author", {}).get("login"),
            committer_id=data.get("committer", {}).get("id"),
            committer_login=data.get("committer", {}).get("login")
        )