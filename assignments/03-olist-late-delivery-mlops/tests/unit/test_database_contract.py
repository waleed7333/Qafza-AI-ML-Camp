from src.qafza_mlops.database import DDL


def test_prediction_request_id_has_database_uniqueness_contract():
    assert "CREATE UNIQUE INDEX IF NOT EXISTS prediction_logs_request_id_uidx" in DDL
    assert "ON serving.prediction_logs (request_id)" in DDL
