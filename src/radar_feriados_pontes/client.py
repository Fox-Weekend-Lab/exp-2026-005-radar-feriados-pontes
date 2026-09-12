"""Cliente HTTP isolado para a API Nager.Date."""

import os
from typing import Any, Callable

import requests


class HolidayApiError(RuntimeError):
    """Indica falha de configuração ou comunicação com a API de feriados."""


def fetch_public_holidays(
    country_code: str,
    request_get: Callable[..., requests.Response] | None = None,
) -> Any:
    """Busca os próximos feriados públicos para o país informado."""
    base_url = os.getenv("NAGER_API_BASE_URL", "").strip()
    if not base_url:
        raise HolidayApiError(
            "Configuração ausente. Defina a variável NAGER_API_BASE_URL com a URL da API."
        )

    url = f"{base_url.rstrip('/')}/api/v3/NextPublicHolidays/{country_code}"
    requester = request_get or requests.get
    try:
        response = requester(url, timeout=10)
    except requests.RequestException as exc:
        raise HolidayApiError(
            "Não foi possível consultar a API de feriados. Verifique a conexão e tente novamente."
        ) from exc

    try:
        response.raise_for_status()
    except requests.RequestException as exc:
        raise HolidayApiError(
            "A API de feriados respondeu com erro. Tente novamente mais tarde."
        ) from exc

    try:
        return response.json()
    except (ValueError, requests.RequestException) as exc:
        raise HolidayApiError("A API de feriados retornou uma resposta JSON inválida.") from exc
