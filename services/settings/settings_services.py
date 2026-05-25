from typing import Any, Dict

from sqlalchemy.orm import Session

from app.model import AppConfigTable
from app.schema import GlobalResponse


class SettingsServices:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _normalize_value(value: Any) -> Any:
        if isinstance(value, dict):
            return {
                str(key): SettingsServices._normalize_value(val)
                for key, val in value.items()
            }

        if isinstance(value, list):
            return [SettingsServices._normalize_value(item) for item in value]

        if isinstance(value, (str, int, float, bool)) or value is None:
            return value

        return str(value)

    def get_settings(self) -> GlobalResponse:
        configs = self.db.query(AppConfigTable).order_by(AppConfigTable.key.asc()).all()
        settings = {config.key: config.value for config in configs}

        return GlobalResponse(
            success=True,
            message="Settings fetched successfully",
            data={"settings": settings}
        )

    def update_setting(self, key: str, payload: Dict[str, Any]) -> GlobalResponse:
        config = self.db.query(AppConfigTable).filter(AppConfigTable.key == key).first()

        if not config:
            return GlobalResponse(
                success=False,
                message="Settings key not found",
                data={}
            )

        current_value = config.value if isinstance(config.value, dict) else {}
        new_value = {
            **current_value,
            **self._normalize_value(payload)
        }

        config.value = new_value
        self.db.commit()
        self.db.refresh(config)

        return GlobalResponse(
            success=True,
            message="Settings updated successfully",
            data={"key": config.key, "value": config.value}
        )
