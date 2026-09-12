from datetime import date

import pytest

from radar_feriados_pontes.service import HolidayDataError, build_holidays, normalize_country_code


def test_build_holidays_filters_regional_items_converts_dates_and_suggests_bridges():
    holidays = build_holidays(
        [
            {"date": "2025-07-08", "localName": "Terça", "global": True},
            {"date": "2025-07-10", "localName": "Quinta", "global": True},
            {"date": "2025-07-14", "localName": "Segunda", "global": True},
            {"date": "2025-07-09", "localName": "Regional", "global": False},
        ]
    )

    assert [holiday.local_name for holiday in holidays] == ["Terça", "Quinta", "Segunda"]
    assert holidays[0].date == date(2025, 7, 8)
    assert holidays[0].bridge_day == date(2025, 7, 7)
    assert holidays[1].date == date(2025, 7, 10)
    assert holidays[1].bridge_day == date(2025, 7, 11)
    assert holidays[2].bridge_day is None


@pytest.mark.parametrize(
    ("items", "message"),
    [
        ({"date": "2025-07-08"}, "deve ser uma lista"),
        ([{"date": "08-07-2025", "localName": "Teste", "global": True}], "inválida"),
        ([{"date": "2025-07-08", "global": True}], "campos obrigatórios"),
        ([{"date": "2025-07-08", "localName": "Teste", "global": "true"}], "booleano"),
    ],
)
def test_build_holidays_rejects_invalid_api_data(items, message):
    with pytest.raises(HolidayDataError, match=message):
        build_holidays(items)


@pytest.mark.parametrize(
    ("value", "expected"),
    [("br", "BR"), (" Br ", "BR"), ("us", "US")],
)
def test_normalize_country_code_returns_uppercase_iso_code(value, expected):
    assert normalize_country_code(value) == expected


@pytest.mark.parametrize("value", ["B", "BRA", "B1", "çç", "  "])
def test_normalize_country_code_rejects_invalid_values(value):
    with pytest.raises(HolidayDataError, match="Código de país inválido"):
        normalize_country_code(value)
