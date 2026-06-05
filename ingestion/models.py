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