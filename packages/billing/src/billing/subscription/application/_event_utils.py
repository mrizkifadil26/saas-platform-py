def pull_events(aggregate: object) -> list[object]:
    pull_domain_events = getattr(aggregate, "pull_domain_events", None)
    if callable(pull_domain_events) and hasattr(aggregate, "_domain_events"):
        return list(pull_domain_events())

    pull_events_fn = getattr(aggregate, "pull_events", None)
    if callable(pull_events_fn):
        return list(pull_events_fn())

    events = list(getattr(aggregate, "_events", []))
    if hasattr(aggregate, "_events"):
        getattr(aggregate, "_events").clear()
    return events
