from app.main import database_ready


def test_db_ready_true(session_factory) -> None:
    assert database_ready(session_factory) is True


def test_db_ready_false_on_broken_factory() -> None:
    def boom():
        raise RuntimeError("no db")

    assert database_ready(boom) is False
