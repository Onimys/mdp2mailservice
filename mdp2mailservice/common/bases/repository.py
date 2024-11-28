import uuid
from typing import Any, Generic, Type, TypeVar

from sqlalchemy import BinaryExpression, ColumnElement, select
from sqlalchemy.ext.asyncio import AsyncSession

from mdp2mailservice.common.bases.models import Base

ModelType = TypeVar("ModelType", bound=Base, covariant=True)


class RepositoryBase(Generic[ModelType]):
    """Repository for performing database queries."""

    model: Type[ModelType]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(self, data: dict[Any, Any] | ModelType) -> ModelType:
        if isinstance(data, dict):
            instance = self.model(**data)
        else:
            instance = data

        self.session.add(instance)
        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def update(
        self,
        instance: ModelType | None = None,
        data: dict[Any, Any] | None = None,
        id_: uuid.UUID | int | None = None,
    ) -> ModelType:
        if not instance:
            if id_:
                instance = await self.get(id_)
                if not instance:
                    raise Exception(
                        f"{self.model.__tablename__} pk={id_} not found.",
                    )

            else:
                raise Exception("Always pass id_ parameter if 'instance' is None.")

        if data:
            for k, v in data.items():
                setattr(instance, k, v)

        await self.session.commit()
        await self.session.refresh(instance)
        return instance

    async def get(self, pk: uuid.UUID | int) -> ModelType | None:
        return await self.session.get(self.model, pk)

    async def get_all(self, limit: int | None = None, offset: int | None = None) -> list[ModelType]:
        query = select(self.model)

        if limit:
            query = query.limit(limit)

        if offset:
            query = query.offset(offset)

        return list(await self.session.scalars(query))

    async def filter(
        self,
        *expressions: BinaryExpression[Any] | ColumnElement[Any],
    ) -> list[ModelType]:
        query = select(self.model)
        if expressions:
            query = query.where(*expressions)
        return list(await self.session.scalars(query))

    async def delete(
        self,
        *expressions: BinaryExpression[Any] | ColumnElement[Any],
    ) -> None:
        query = select(self.model)
        if expressions:
            query = query.where(*expressions)

        for item in await self.session.scalars(query):
            await self.session.delete(item)
        await self.session.commit()
