def test_add_comment(client, authorized_user_token):
    response = client.post(
        "/comments/",
        json={"article_id": 1, "content": "Nice post!"},
        headers={"Authorization": f"Bearer {authorized_user_token}"}
    )
    assert response.status_code == 200
    assert "id" in response.json()


# Комментарии: ошибка, если статья не найдена
def test_comment_on_missing_article(client, auth_headers):
    response = client.post("/comments/", json={"article_id": 99999, "content": "Test"}, headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["detail"] == "Article not found"

# Ошибка при удалении чужого комментария
def test_delete_foreign_comment(client, auth_headers, create_other_user_comment):
    response = client.delete(f"/comments/{create_other_user_comment}", headers=auth_headers)
    assert response.status_code == 403
    assert response.json()["detail"] == "Permission denied"