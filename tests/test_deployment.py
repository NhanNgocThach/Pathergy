from fastapi.testclient import TestClient


def test_cloud_health_check_is_small_and_public(client: TestClient) -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
