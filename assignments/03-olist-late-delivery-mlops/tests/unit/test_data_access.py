from src.qafza_mlops.data_access import PredictionLogRepository


class FakeResult:
    rowcount = 1


class FakeMappingResult:
    def mappings(self):
        return self

    def one(self):
        return {"n": 4, "late_rate": 0.25}


class FakeConnection:
    def __init__(self):
        self.parameters = None

    def execute(self, statement, parameters=None):
        self.parameters = parameters
        if parameters and "hours" in parameters:
            return FakeMappingResult()
        return FakeResult()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback):
        return False


class FakeEngine:
    def __init__(self):
        self.connection = FakeConnection()
        self.disposed = False

    def begin(self):
        return self.connection

    def connect(self):
        return self.connection

    def dispose(self):
        self.disposed = True


def test_repository_records_outcome_and_reads_recent_stats():
    engine = FakeEngine()
    repository = PredictionLogRepository(engine)

    assert repository.record_outcome("abc", 1) is True
    count, rate = repository.recent_prediction_stats(hours=24)

    assert count == 4
    assert rate == 0.25
    assert engine.connection.parameters == {"hours": 24}

    repository.close()
    assert engine.disposed is True
