from datetime import date, datetime, time, timedelta, timezone
from typing import Optional

from sqlalchemy import (
    and_, func, insert, select,
)
from sqlalchemy.orm import selectinload
# from sqlalchemy.sql.expression import false

from .base_repo import Repository
from events_app.db.models import (
    Category, Event, EventDate, Location, Tag, event_has_tag
)
from events_app.schemas import SearchResult


class EventRepository(Repository[Event]):
    model = Event

    async def create(
            self,
            data: dict,
    ) -> Event | None:
        clean_data = data.copy()
        tags = clean_data.pop("tags", [])
        event_dates_data = clean_data.pop("dates", [])

        res = await self.session.execute(
            insert(self.model)
            .values(**clean_data)
            .returning(self.model.id)
        )
        event_id = res.scalar_one()

        if tags:
            await self._add_tags(event_id, tags)

        if event_dates_data:
            await self._add_event_dates(event_id, event_dates_data)

        return await self.get(event_id)

    async def get(
            self,
            id: int,
    ) -> Event | None:
        stmt = (
            select(self.model)
            .where(self.model.id == id)
            .options(
                selectinload(self.model.location),
                selectinload(self.model.category),
                selectinload(self.model.tags),
                selectinload(self.model.dates),
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_all(
            self,
            offset: int,
            limit: int
    ) -> list[Event]:
        return await self._find_filtered(
            filters=[], offset=offset, limit=limit)

    async def count_all(self) -> int:
        return await self._count_filtered([])

    async def find_by_location(
            self,
            location_id: int,
            offset: int,
            limit: int,
    ) -> list[Event]:
        filters = [self.model.location_id == location_id]
        return await self._find_filtered(
            filters=filters,
            offset=offset,
            limit=limit
        )

    async def count_by_location(
            self,
            location_id: int,
    ) -> int:
        return await self._count_filtered(
            [self.model.location_id == location_id]
        )

    async def find_by_category(
            self,
            category_id: int,
            offset: int,
            limit: int,
    ) -> list[Event]:
        filters = [self.model.category_id == category_id]
        return await self._find_filtered(
            filters=filters,
            offset=offset,
            limit=limit
        )

    async def count_by_category(self, category_id: int) -> int:
        return await self._count_filtered(
            [self.model.category_id == category_id]
        )

    async def find_by_date_filter(
        self,
        date: Optional[date],
        date_from: Optional[date],
        date_to: Optional[date],
        hour: Optional[int],
        offset: int,
        limit: int,
    ) -> list[Event]:
        filters = self._build_date_filters(
            date, date_from, date_to, hour)
        return await self._find_filtered(
            filters=filters,
            offset=offset,
            limit=limit
        )

    async def count_filtered(
        self,
        date: Optional[date],
        date_from: Optional[date],
        date_to: Optional[date],
        hour: Optional[int],
    ) -> int:
        filters = self._build_date_filters(
            date, date_from, date_to, hour)
        return await self._count_filtered(filters)

    async def update_image(
            self,
            event: Event,
            image_path: str,
    ) -> Event:
        event.event_image = image_path
        await self.session.flush()
        await self.session.refresh(event)
        return event

    async def search_titles_and_locations(
            self,
            query: str,
    ) -> list[SearchResult]:
        like_expr = f"{query}%"

        events_stmt = (
            select(self.model.id, self.model.title.label("name"))
            .where(self.model.title.ilike(like_expr))
        )
        locations_stmt = (
            select(Location.id, Location.name)
            .where(Location.name.ilike(like_expr))
        )

        events_result = await self.session.execute(events_stmt)
        locations_result = await self.session.execute(locations_stmt)

        event_results = [
            SearchResult(id=row.id, name=row.name, type='event')
            for row in events_result
        ]
        location_results = [
            SearchResult(id=row.id, name=row.name, type='location')
            for row in locations_result
        ]

        return event_results + location_results

    async def _add_tags(self, event_id: int, tag_ids: list[int]):
        values = [
            {"event_id": event_id, "tag_id": tag_id}
            for tag_id in tag_ids
        ]
        await self.session.execute(insert(event_has_tag).values(values))

    async def _add_event_dates(self, event_id: int, dates_data: list[datetime]):
        values = [
            {"event_id": event_id, "date": dt}
            for dt in dates_data
        ]
        if values:
            await self.session.execute(insert(EventDate).values(values))

    async def _find_filtered(
            self,
            filters: list,
            offset: int,
            limit: int,
    ) -> list[Event]:
        upcoming_filter = self.model.closest_date >= datetime.now(timezone.utc)
        all_filters = [upcoming_filter] + filters

        stmt = (
            select(self.model)
            .where(and_(*all_filters))
            .options(selectinload(self.model.location))
            .order_by(self.model.closest_date.asc())
            .offset(offset).limit(limit)
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def _count_filtered(
            self,
            filters: list,
    ) -> int:
        upcoming_filter = self.model.closest_date >= datetime.now(timezone.utc)
        all_filters = [upcoming_filter] + filters

        stmt = (
            select(func.count()).select_from(self.model)
            .where(and_(*all_filters))
        )
        result = await self.session.execute(stmt)
        return result.scalar_one()

    def _build_date_filters(
        self,
        date: Optional[date],
        date_from: Optional[date],
        date_to: Optional[date],
        hour: Optional[int],
    ) -> list:
        filters = []

        if date:
            if hour is not None:
                start_dt = datetime.combine(
                    date, time(hour, 0, 0), tzinfo=timezone.utc)
                end_dt = start_dt + timedelta(hours=1)
                filters.append(self.model.closest_date >= start_dt)
                filters.append(self.model.closest_date < end_dt)
            else:
                start_of_day = datetime.combine(
                    date, time.min, tzinfo=timezone.utc)
                end_of_day = start_of_day + timedelta(days=1)
                filters.append(self.model.closest_date >= start_of_day)
                filters.append(self.model.closest_date < end_of_day)
        elif date_from and date_to:
            start_dt = datetime.combine(
                date_from, time.min, tzinfo=timezone.utc)
            end_dt = datetime.combine(
                date_to, time(23, 59, 59, 999999), tzinfo=timezone.utc)
            filters.append(self.model.closest_date >= start_dt)
            filters.append(self.model.closest_date <= end_dt)

        return filters


class LocationRepository(Repository[Location]):
    model = Location


class CategoryRepository(Repository[Category]):
    model = Category


class TagRepository(Repository[Tag]):
    model = Tag
