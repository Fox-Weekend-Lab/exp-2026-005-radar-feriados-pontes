import requests
import pytest
import responses

from radar_feriados_pontes.client import HolidayApiError, fetch_public_holidays


BASE_URL = "https://date.nager.at"


def test_fetch_public_holidays_uses_nager_url_and_returns_json(monkeypatch):
    monkeypatch.setenv("NAGER_API_BASE_URL", BASE_URL)
    expected_url = f"{BASE_URL}/api/v3/NextPublicHolidays/BR"
    payload = [{"date": "2025-07-08", "localName": "Feriado", "global": True}]

    with responses.RequestsMock() as mock:
        mock.add(responses.GET, expected_url, json=payload, status=200)

        result = fetch_public_holidays("BR")

        assert result == payload
        assert len(mock.calls) == 1
        assert mock.calls[0].request.url == expected_url


def test_fetch_public_holidays_converts_http_error(monkeypatch):
    monkeypatch.setenv("NAGER_API_BASE_URL", BASE_URL)
    url = f"{BASE_URL}/api/v3/NextPublicHolidays/BR"

    with responses.RequestsMock() as mock:
        mock.add(responses.GET, url, json={"message": "unavailable"}, status=503)

        with pytest.raises(HolidayApiError, match="respondeu com erro"):
            fetch_public_holidays("BR")


def test_fetch_public_holidays_converts_transport_failure(monkeypatch):
    monkeypatch.setenv("NAGER_API_BASE_URL", BASE_URL)
    url = f"{BASE_URL}/api/v3/NextPublicHolidays/BR"

    with responses.RequestsMock() as mock:
        mock.add(responses.GET, url, body=requests.ConnectionError("offline"))

        with pytest.raises(HolidayApiError, match="Não foi possível consultar"):
            fetch_public_holidays("BR")


def test_fetch_public_holidays_converts_invalid_json(monkeypatch):
    monkeypatch.setenv("NAGER_API_BASE_URL", BASE_URL)
    url = f"{BASE_URL}/api/v3/NextPublicHolidays/BR"

    with responses.RequestsMock() as mock:
        mock.add(
            responses.GET,
            url,
            body="{invalid json",
            content_type="application/json",
            status=200,
        )

        with pytest.raises(HolidayApiError, match="JSON inválida"):
            fetch_public_holidays("BR")


def test_fetch_public_holidays_requires_configured_base_url(monkeypatch):
    monkeypatch.delenv("NAGER_API_BASE_URL", raising=False)

    with pytest.raises(HolidayApiError, match="NAGER_API_BASE_URL"):
        fetch_public_holidays("BR")
