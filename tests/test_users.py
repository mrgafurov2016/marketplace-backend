def test_get_user_by_id(client):
    response = client.get("/users/1")
    assert response.status_code == 200
    assert "email" in response.json()