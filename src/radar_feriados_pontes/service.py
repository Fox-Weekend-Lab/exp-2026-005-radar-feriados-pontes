"""Regras puras para validar feriados nacionais e sugerir pontes."""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any


class HolidayDataError(ValueError):
    """Indica dados de feriados inválidos ou argumentos inválidos."""


@dataclass(frozen=True)
class Holiday:
    date: date
    local_name: str
    bridge_day: date | None


def normalize_country_code(value: str) -> str:
    """Valida e normaliza um código ISO 3166-1 alfa-2."""
    country_code = value.strip()
    if len(country_code) != 2 or not country_code.isascii() or not country_code.isalpha():
        raise HolidayDataError(
            "Código de país inválido. Informe um código ISO de duas letras, como BR."
        )
    return country_code.upper()


def build_holidays(items: Any) -> list[Holiday]:
    """Converte a resposta da API em feriados nacionais validados."""
    if not isinstance(items, list):
        raise HolidayDataError("A resposta da API deve ser uma lista de feriados.")

    holidays: list[Holiday] = []
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise HolidayDataError(f"O feriado na posição {index} deve ser um objeto.")

        _require_fields(item, index)
        is_global = item["global"]
        if not isinstance(is_global, bool):
            raise HolidayDataError(
                f"O campo global do feriado na posição {index} deve ser booleano."
            )

        holiday_date = _parse_date(item["date"], index)
        local_name = item["localName"]
        if not isinstance(local_name, str) or not local_name.strip():
            raise HolidayDataError(
                f"O campo localName do feriado na posição {index} deve ser um texto não vazio."
            )

        if is_global:
            holidays.append(
                Holiday(
                    date=holiday_date,
                    local_name=local_name.strip(),
                    bridge_day=_bridge_day(holiday_date),
                )
            )

    return holidays


def _require_fields(item: dict[str, Any], index: int) -> None:
    missing = [field for field in ("date", "localName", "global") if field not in item]
    if missing:
        fields = ", ".join(missing)
        raise HolidayDataError(
            f"O feriado na posição {index} não contém os campos obrigatórios: {fields}."
        )


def _parse_date(value: Any, index: int) -> date:
    if not isinstance(value, str):
        raise HolidayDataError(f"A data do feriado na posição {index} deve ser texto ISO.")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise HolidayDataError(
            f"A data do feriado na posição {index} é inválida. Use AAAA-MM-DD."
        ) from exc
    if parsed.isoformat() != value:
        raise HolidayDataError(
            f"A data do feriado na posição {index} deve usar o formato AAAA-MM-DD."
        )
    return parsed


def _bridge_day(holiday_date: date) -> date | None:
    if holiday_date.weekday() == 1:
        return holiday_date - timedelta(days=1)
    if holiday_date.weekday() == 3:
        return holiday_date + timedelta(days=1)
    return None
