"""Plan Sentinela UI actions from a parsed intent."""

from __future__ import annotations

from sentinel_suisse.schemas.sentinela import (
    SentinelaAction,
    SentinelaTurnRequest,
    SentinelaTurnResponse,
)
from sentinel_suisse.services.sentinela_parse import parse_turn


def _filters_payload(intent) -> dict:
    payload: dict = {}
    if intent.mode:
        payload["mode"] = intent.mode
    if intent.zone:
        payload["zone"] = intent.zone
    if intent.city:
        payload["city"] = intent.city
    if intent.rooms:
        payload["rooms"] = intent.rooms
    if intent.price_max is not None:
        payload["price_max"] = str(intent.price_max)
    if intent.has_parking is not None:
        payload["has_parking"] = intent.has_parking
    if intent.under_construction is not None:
        payload["under_construction"] = intent.under_construction
    if intent.sort:
        payload["sort"] = intent.sort
    return payload


def _slots(intent) -> dict[str, str]:
    slots: dict[str, str] = {}
    if intent.city:
        slots["ville"] = intent.city
    if intent.rooms:
        slots["pieces"] = intent.rooms
    if intent.price_max is not None:
        slots["prix"] = str(intent.price_max)
    if intent.unknown_city:
        slots["ville"] = intent.unknown_city
    return slots


def plan_turn(request: SentinelaTurnRequest) -> SentinelaTurnResponse:
    ctx = request.ui_context
    open_listing = ctx.open_listing
    intent = parse_turn(
        request.message,
        ui_mode=ctx.mode,
        ui_zone=ctx.zone,
        has_open_listing=open_listing is not None,
    )
    slots = _slots(intent)
    chips = list(intent.chips)
    actions: list[SentinelaAction] = []

    if intent.intent == "unknown_city":
        return SentinelaTurnResponse(
            actions=[],
            say_id="unknown_city",
            slots=slots,
            chips=[],
        )
    if intent.intent == "need_city":
        payload = _filters_payload(intent)
        if payload:
            actions.append(SentinelaAction(type="apply_filters", payload=payload))
        return SentinelaTurnResponse(
            actions=actions,
            say_id="need_city",
            slots=slots,
            chips=[],
        )
    if intent.intent == "map":
        actions.append(SentinelaAction(type="switch_tab", payload={"tab": "map"}))
        actions.append(SentinelaAction(type="focus_map", payload={}))
        return SentinelaTurnResponse(actions=actions, say_id="map", slots=slots, chips=chips)
    if intent.intent == "alert":
        actions.append(SentinelaAction(type="compose_alert", payload={}))
        actions.append(SentinelaAction(type="point_to", payload={"target": "alerts"}))
        return SentinelaTurnResponse(actions=actions, say_id="alert", slots=slots, chips=chips)
    if intent.intent == "open_first":
        actions.append(SentinelaAction(type="open_listing", payload={"which": "first"}))
        actions.append(SentinelaAction(type="highlight_listings", payload={"which": "first"}))
        return SentinelaTurnResponse(actions=actions, say_id="open_first", slots=slots, chips=chips)
    if intent.intent == "how_apply":
        if open_listing:
            if open_listing.location:
                slots["lieu"] = open_listing.location
            if open_listing.price is not None:
                slots["prix"] = str(int(open_listing.price))
        return SentinelaTurnResponse(
            actions=[],
            say_id="open_listing",
            slots=slots,
            chips=chips,
        )
    if intent.intent in {"search", "cheaper"}:
        payload = _filters_payload(intent)
        if intent.mode:
            actions.append(SentinelaAction(type="set_mode", payload={"mode": intent.mode}))
        if payload:
            actions.append(SentinelaAction(type="apply_filters", payload=payload))
        actions.append(SentinelaAction(type="run_search", payload={}))
        actions.append(SentinelaAction(type="switch_tab", payload={"tab": "list"}))
        return SentinelaTurnResponse(
            actions=actions,
            say_id="filtered",
            slots=slots,
            chips=chips or ["see_first", "create_alert", "on_map"],
        )

    return SentinelaTurnResponse(
        actions=[],
        say_id="out_of_scope",
        slots=slots,
        chips=chips or ["look_home", "look_job"],
    )
