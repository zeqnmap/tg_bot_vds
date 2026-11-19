from dataclasses import dataclass
from enum import Enum


class RequestType(str, Enum):
    IDEA = "idea"
    TOP_MEETING = "top_meeting"

    @property
    def label(self) -> str:
        return {
            RequestType.IDEA: "Предложить идею 💡",
            RequestType.TOP_MEETING: "Запрос на встречу с Топом 🖌",
        }[self]


@dataclass(frozen=True, slots=True)
class UserRequest:
    full_name: str
    request_type: RequestType
    telegram_user_id: int
    description: str
    telegram_username: str | None = None
