def test_add_to_favorites(client, authorized_user_token):
    response = client.post(
        "/favorites/1",
        headers={"Authorization": f"Bearer {authorized_user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Added to favorites"