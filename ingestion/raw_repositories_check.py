from raw_repositories import get_repository_data
from models import RepositoryRecord

raw = get_repository_data("pytorch/pytorch")
record = RepositoryRecord.from_api_response(raw)
print(record.model_dump())