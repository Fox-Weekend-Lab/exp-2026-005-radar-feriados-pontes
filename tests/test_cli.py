import responses

from radar_feriados_pontes.__main__ import main


BASE_URL = "https://date.nager.at"


def test_cli_prints_national_holidays_and_bridge_with_normalized_country(monkeypatch, capsys):
    monkeypatch.setenv("NAGER_API_BASE_URL", BASE_URL)
    url = f"{BASE_URL}/api/v3/NextPublicHolidays/BR"
    payload = [
        {"date": "2025-07-08", "localName": "Feriado de Terça", "global": True},
        {"date": "2025-07-09", "localName": "Regional", "global": False},
    ]

    with responses.RequestsMock() as mock:
        mock.add(responses.GET, url, json=payload, status=200)

        exit_code = main(["br"])

        assert len(mock.calls) == 1
        assert mock.calls[0].request.url == url

    captured = capsys.readouterr()
    assert exit_code == 0
    assert captured.err == ""
    assert "Feriados nacionais para BR:" in captured.out
    assert "2025-07-08 (terça-feira) - Feriado de Terça" in captured.out
    assert "Sugestão de emenda: folgar em 2025-07-07 (segunda-feira)." in captured.out
    assert "Regional" not in captured.out


def test_cli_rejects_invalid_country_code_without_request(capsys):
    exit_code = main(["B1"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "Código de país inválido" in captured.err


def test_cli_reports_api_failure_in_portuguese(monkeypatch, capsys):
    monkeypatch.setenv("NAGER_API_BASE_URL", BASE_URL)
    url = f"{BASE_URL}/api/v3/NextPublicHolidays/BR"

    with responses.RequestsMock() as mock:
        mock.add(responses.GET, url, json={"message": "failure"}, status=500)

        exit_code = main(["BR"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "Erro:" in captured.err
    assert "API de feriados respondeu com erro" in captured.err


def test_cli_reports_invalid_api_payload(monkeypatch, capsys):
    monkeypatch.setenv("NAGER_API_BASE_URL", BASE_URL)
    url = f"{BASE_URL}/api/v3/NextPublicHolidays/BR"

    with responses.RequestsMock() as mock:
        mock.add(responses.GET, url, json={"not": "a list"}, status=200)

        exit_code = main(["BR"])

    captured = capsys.readouterr()
    assert exit_code == 1
    assert captured.out == ""
    assert "A resposta da API deve ser uma lista de feriados" in captured.err
