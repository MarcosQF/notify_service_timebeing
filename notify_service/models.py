import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from .database import reg


@reg.mapped_as_dataclass
class Notification:
    __tablename__ = 'notification'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    email: Mapped[str] = mapped_column(nullable=False)
    task_title: Mapped[str]
    notify_at: Mapped[str]
    created_at: Mapped[datetime.datetime] = mapped_column(
        init=False, nullable=False, server_default=func.now()
    )
