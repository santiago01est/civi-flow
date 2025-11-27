# app/repositories/base_repository.py
from typing import Generic, Type, TypeVar, List, Optional, Any
from pydantic import BaseModel
from azure.cosmos import CosmosClient, ContainerProxy
from app.db.session import get_container

T = TypeVar("T", bound=BaseModel)

class BaseRepository(Generic[T]):
    def __init__(self, container_name: str, model: Type[T], container: Optional[ContainerProxy] = None):
        # Allow passing a container (for dependency injection / testing). If not provided,
        # obtain the shared container from app.db.session (requires init_cosmos called at startup).
        if container is None:
            self.container: ContainerProxy = get_container(container_name)
        else:
            self.container = container
        self.model = model

    def create(self, item: T) -> T:
        self.container.create_item(body=item.dict())
        return item

    def get(self, item_id: str, partition_key: str) -> Optional[T]:
        try:
            item = self.container.read_item(item=item_id, partition_key=partition_key)
            return self.model(**item)
        except Exception:
            return None

    def list(self) -> List[T]:
        items = self.container.read_all_items()
        return [self.model(**item) for item in items]

    def update(self, item_id: str, partition_key: str, updates: dict) -> Optional[T]:
        try:
            item = self.container.read_item(item=item_id, partition_key=partition_key)
            item.update(updates)
            self.container.replace_item(item=item_id, body=item)
            return self.model(**item)
        except Exception:
            return None

    def delete(self, item_id: str, partition_key: str):
        self.container.delete_item(item=item_id, partition_key=partition_key)

    def query(self, query: str, parameters: Optional[List[dict]] = None) -> List[T]:
        items = self.container.query_items(
            query=query,
            parameters=parameters,
            enable_cross_partition_query=True
        )
        return [self.model(**item) for item in items]
