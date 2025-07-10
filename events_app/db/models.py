from sqlalchemy import (
    BigInteger, Boolean, Column,
    Date, DateTime,
    Float, ForeignKey,
    String, Table, Text,
)
from sqlalchemy.sql import func, select
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    column_property,
)

from .database import Base


class SourceUser(Base):
    """Источник регистрации пользователя."""
    __tablename__ = "source_users"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    user: Mapped[list["User"]] = relationship(
        back_populates="source",
        passive_deletes=True
    )


# Таблица для связи "избранное событие — пользователь"
favorite_events = Table(
    'favorite_events',
    Base.metadata,
    Column(
        "user_id",
        BigInteger,
        ForeignKey(
            'users.id',
            ondelete='CASCADE',
        ),
    ),
    Column(
        'event_id',
        BigInteger,
        ForeignKey(
            'event.id',
            ondelete='CASCADE',
        ),
    ),
)


class User(Base):
    """Модель пользователя."""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        index=True,
    )
    username: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        index=True,
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String,
        unique=True,
        index=True,
        nullable=False,
    )
    hashed_password: Mapped[str] = mapped_column(
        String,
        nullable=False,
    )
    first_name: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )
    last_name: Mapped[str | None] = mapped_column(
        String(32),
        nullable=True,
    )
    dob: Mapped[Date | None] = mapped_column(
        Date,
        nullable=True,
    )
    created_at: Mapped[Date] = mapped_column(
        Date,
        server_default=func.now(),
    )
    gender: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="not_specified")
    profile_image: Mapped[str | None] = mapped_column(
        String,
        nullable=True,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )
    source_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "source_users.id",
            ondelete="SET NULL",
                    ),
        nullable=True,
        default=1,
    )

    source: Mapped["SourceUser"] = relationship(
        back_populates="user",
        passive_deletes=True,
    )
    favorites: Mapped[list['Event']] = relationship(
        secondary=favorite_events,
        back_populates='fans',
        lazy='selectin'
    )


class Location(Base):
    """Модель места проведения мероприятия."""
    __tablename__ = 'location'

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        )
    name: Mapped[str] = mapped_column(
        nullable=False,
        )
    address: Mapped[str]
    latitude: Mapped[float] = mapped_column(
        Float,
        nullable=True,
    )
    longitude: Mapped[float] = mapped_column(
        Float,
        nullable=True,
    )
    description: Mapped[str]

    events: Mapped[list["Event"]] = relationship(
        back_populates="location",
        cascade="all,delete-orphan",
        passive_deletes=True,
        )


class Category(Base):
    """Модель категории мероприятия (одна категория для мероприятия)."""
    __tablename__ = 'category'

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        index=True,
        )
    name: Mapped[str] = mapped_column(
        nullable=False,
        )
    plural_name: Mapped[str] = mapped_column(
        nullable=True,
    )

    events: Mapped[list["Event"]] = relationship(
        back_populates='category',
        cascade="all, delete-orphan",
        )


# Таблица для связи "событие — тег"
event_has_tag = Table(
    "event_tag",
    Base.metadata,
    Column(
        "event_id",
        BigInteger,
        ForeignKey(
            "event.id",
            ondelete="CASCADE",
            ),
        primary_key=True,
        ),
    Column(
        "tag_id",
        BigInteger,
        ForeignKey(
            "tag.id",
            ondelete="CASCADE",
            ),
        primary_key=True
        ),
)


class Tag(Base):
    """Модель тега мероприятия (несколько у одного мероприятия)."""
    __tablename__ = 'tag'

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        nullable=False,
    )
    description: Mapped[str] = mapped_column(
        nullable=False,
    )

    events: Mapped[list["Event"]] = relationship(
        "Event",
        secondary=event_has_tag,
        back_populates="tags"
    )


class EventDate(Base):
    """Дата проведения события (может быть несколько на одно событие)."""
    __tablename__ = 'event_date'

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        index=True
    )
    date: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        index=True,
    )

    event_id: Mapped[int] = mapped_column(
        ForeignKey(
            "event.id",
            ondelete="CASCADE"
        ), nullable=False
    )
    event: Mapped["Event"] = relationship(
        back_populates="dates"
    )


class Event(Base):
    """Модель события."""
    __tablename__ = 'event'

    id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        index=True,
        )
    title: Mapped[str] = mapped_column(
        nullable=False,
        )
    description: Mapped[str]
    closest_date: Mapped[DateTime] = column_property(
        select(func.min(EventDate.date))
        .where(EventDate.event_id == id)
        .correlate_except(EventDate)
        .scalar_subquery()
    )
    price: Mapped[str] = mapped_column(
        nullable=False
        )
    url: Mapped[str] = mapped_column(
        nullable=False,
        )
    event_image: Mapped[str | None] = mapped_column(
        nullable=True,
        )
    location_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "location.id",
            ondelete="CASCADE",
                   ),
        nullable=False,
        )
    category_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey(
            "category.id",
            ondelete="CASCADE",
                   ),
        nullable=False,
        )
    tags: Mapped[list["Tag"]] = relationship(
        "Tag",
        secondary=event_has_tag,
        back_populates="events"
        )
    location: Mapped["Location"] = relationship(
        back_populates="events",
        )
    category: Mapped["Category"] = relationship(
        back_populates="events",
        )
    fans: Mapped[list['User']] = relationship(
        secondary=favorite_events,
        back_populates='favorites',
        lazy='selectin'
        )
    dates: Mapped[list["EventDate"]] = relationship(
        back_populates="event", cascade="all, delete-orphan"
    )
