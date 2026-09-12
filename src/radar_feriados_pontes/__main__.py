"""Interface de linha de comando do Radar de Feriados e Pontes."""

import argparse
import sys
from collections.abc import Sequence

from .client import HolidayApiError, fetch_public_holidays
from .service import Holiday, HolidayDataError, build_holidays, normalize_country_code


WEEKDAYS = (
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo",
)


class InputError(ValueError):
    """Indica uso inválido da interface de linha de comando."""


class FriendlyArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        raise InputError(f"Argumento inválido: {message}. Informe um código de país, como BR.")


def create_parser() -> argparse.ArgumentParser:
    parser = FriendlyArgumentParser(prog="radar_feriados_pontes")
    parser.add_argument("country_code", help="código ISO 3166-1 alfa-2, como BR")
    return parser


def render(country_code: str, holidays: list[Holiday]) -> str:
    lines = [f"Feriados nacionais para {country_code}:"]
    if not holidays:
        lines.append("Nenhum feriado nacional foi encontrado.")
        return "\n".join(lines)

    for holiday in holidays:
        weekday = WEEKDAYS[holiday.date.weekday()]
        lines.append(f"{holiday.date.isoformat()} ({weekday}) - {holiday.local_name}")
        if holiday.bridge_day is not None:
            bridge_weekday = WEEKDAYS[holiday.bridge_day.weekday()]
            lines.append(
                "  Sugestão de emenda: folgar em "
                f"{holiday.bridge_day.isoformat()} ({bridge_weekday})."
            )
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = create_parser()
    try:
        arguments = parser.parse_args(argv)
        country_code = normalize_country_code(arguments.country_code)
        holidays = build_holidays(fetch_public_holidays(country_code))
    except SystemExit as exc:
        return int(exc.code)
    except (InputError, HolidayDataError, HolidayApiError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1

    print(render(country_code, holidays))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
