def pull_events(aggregate: object) -> list[object]:
    events = list(getattr(aggregate, "_events", []))
    if hasattr(aggregate, "_events"):
        getattr(aggregate, "_events").clear()
    return events
