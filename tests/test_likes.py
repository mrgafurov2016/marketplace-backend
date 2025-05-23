def test_like_article(client, authorized_user_token):
    response = client.post(
        "/likes/articles/1",
        headers={"Authorization": f"Bearer {authorized_user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Article liked"