"""Sentinela turn planner tests — no LLM, no database."""

from sentinel_suisse.schemas.sentinela import SentinelaTurnRequest, SentinelaUiContext
from sentinel_suisse.services.sentinela_parse import parse_turn
from sentinel_suisse.services.sentinela_turn import plan_turn


def _types(response) -> list[str]:
    return [item.type for item in response.actions]


def test_parse_geneva_rooms_price() -> None:
    intent = parse_turn("3.5 Genève 2200")
    assert intent.mode == "housing"
    assert intent.city == "Geneva"
    assert intent.rooms == "3.5"
    assert intent.price_max == 2200
    assert intent.intent == "search"


def test_plan_geneva_applies_filters() -> None:
    response = plan_turn(
        SentinelaTurnRequest(message="3.5 Genève 2200", locale="fr"),
    )
    assert "apply_filters" in _types(response)
    assert "run_search" in _types(response)
    filters = next(item.payload for item in response.actions if item.type == "apply_filters")
    assert filters["city"] == "Geneva"
    assert filters["rooms"] == "3.5"
    assert filters["price_max"] == "2200"
    assert response.say_id == "filtered"
    assert "see_first" in response.chips


def test_map_and_alert_and_first() -> None:
    mapped = plan_turn(SentinelaTurnRequest(message="en el mapa", locale="es"))
    assert mapped.actions[0].payload["tab"] == "map"

    alert = plan_turn(SentinelaTurnRequest(message="avísame", locale="es"))
    assert alert.actions[0].type == "compose_alert"
    assert alert.say_id == "alert"

    first = plan_turn(SentinelaTurnRequest(message="el primero", locale="es"))
    assert first.actions[0].payload["which"] == "first"


def test_job_annemasse() -> None:
    intent = parse_turn("empleo cerca de Annemasse")
    assert intent.mode == "job"
    assert intent.city == "Annemasse"
    assert intent.zone == "FR"


def test_unknown_city_does_not_search() -> None:
    response = plan_turn(SentinelaTurnRequest(message="piso en Atlantis", locale="es"))
    assert response.say_id == "unknown_city"
    assert "run_search" not in _types(response)


def test_need_city_when_rooms_without_place() -> None:
    response = plan_turn(SentinelaTurnRequest(message="busco un 3.5 hasta 2000", locale="es"))
    assert response.say_id == "need_city"
    assert "run_search" not in _types(response)


def test_look_housing_sets_mode() -> None:
    response = plan_turn(SentinelaTurnRequest(message="Je cherche un logement", locale="fr"))
    assert response.say_id == "need_city"
    mode = next(
        (item.payload.get("mode") for item in response.actions if item.type == "apply_filters"),
        None,
    )
    assert mode == "housing"


def test_keeps_current_mode_when_ambiguous() -> None:
    response = plan_turn(
        SentinelaTurnRequest(
            message="algo en Ginebra",
            locale="es",
            ui_context=SentinelaUiContext(mode="job"),
        )
    )
    assert response.say_id == "filtered"
    set_mode = next(item for item in response.actions if item.type == "set_mode")
    assert set_mode.payload["mode"] == "job"
