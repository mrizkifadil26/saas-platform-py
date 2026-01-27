from packages.taskqueue.src.taskqueue.in_memory import InMemoryTaskQueue
from packages.taskqueue.src.taskqueue.job import JobEnvelope


def test_put_reserve_fifo_order():
    q = InMemoryTaskQueue()

    j1 = JobEnvelope(type="a", payload={"data": 1}).to_json()
    j2 = JobEnvelope(type="b", payload={"data": 2}).to_json()

    id1 = q.put("q1", j1)
    id2 = q.put("q1", j2)

    r1 = q.reserve("q1")
    r2 = q.reserve("q1")
    r3 = q.reserve("q1")

    assert r1 is not None and r2 is not None
    assert r3 is None

    assert r1.provider_job_id == id1
    assert r2.provider_job_id == id2

    env1 = JobEnvelope.from_json(r1.body)
    env2 = JobEnvelope.from_json(r2.body)

    assert env1.payload["data"] == 1
    assert env2.payload["data"] == 2


def test_queues_are_isolated():
    q = InMemoryTaskQueue()

    q.put("q1", JobEnvelope(type="a", payload={"q": 1}).to_json())
    q.put("q2", JobEnvelope(type="b", payload={"q": 2}).to_json())

    r1 = q.reserve("q1")
    r2 = q.reserve("q2")

    assert r1 is not None and r2 is not None
    assert JobEnvelope.from_json(r1.body).payload["q"] == 1
    assert JobEnvelope.from_json(r2.body).payload["q"] == 2


def test_delete_records_job_id():
    q = InMemoryTaskQueue()

    jid = q.put("q1", JobEnvelope(type="a").to_json())
    r = q.reserve("q1")
    assert r is not None
    assert r.provider_job_id == jid

    q.delete(jid)
    assert jid in q.deleted


def test_delayed_jobs_are_not_visible_until_tick_delay():
    q = InMemoryTaskQueue()

    delayed_body = JobEnvelope(type="delayed").to_json()
    jid = q.put("q1", delayed_body, delay=10)

    # Not visible yet
    assert q.reserve("q1") is None

    # After tick_delay, it becomes visible
    q.tick_delay("q1")
    r = q.reserve("q1")
    assert r is not None
    assert r.provider_job_id == jid

    env = JobEnvelope.from_json(r.body)
    assert env.type == "delayed"


def test_tick_delay_only_affects_selected_queue():
    q = InMemoryTaskQueue()

    q.put("q1", JobEnvelope(type="a").to_json(), delay=5)
    q.put("q2", JobEnvelope(type="b").to_json(), delay=5)

    # Release only q1 delayed jobs
    q.tick_delay("q1")

    assert q.reserve("q1") is not None
    assert q.reserve("q2") is None

    q.tick_delay("q2")
    assert q.reserve("q2") is not None