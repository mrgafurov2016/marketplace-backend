def test_create_article(client, authorized_user_token):
    response = client.post(
        "/articles/",
        json={"title": "Test Article", "content": "Some content", "category_id": 1},
        headers={"Authorization": f"Bearer {authorized_user_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Article"
    assert "id" in data


def test_get_article(client, authorized_user_token):
    # Сначала создаем статью
    create_response = client.post(
        "/articles/",
        json={"title": "Article to Read", "content": "Text", "category_id": 1},
        headers={"Authorization": f"Bearer {authorized_user_token}"}
    )
    article_id = create_response.json()["id"]

    # Потом получаем
    response = client.get(f"/articles/{article_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Article to Read"


def test_update_article(client, authorized_user_token):
    # Создаем
    create_response = client.post(
        "/articles/",
        json={"title": "Old Title", "content": "Old Content", "category_id": 1},
        headers={"Authorization": f"Bearer {authorized_user_token}"}
    )
    article_id = create_response.json()["id"]

    # Обновляем
    response = client.put(
        f"/articles/{article_id}",
        json={"title": "New Title", "content": "New Content", "category_id": 1},
        headers={"Authorization": f"Bearer {authorized_user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"


def test_delete_article(client, authorized_user_token):
    create_response = client.post(
        "/articles/",
        json={"title": "To be deleted", "content": "Trash", "category_id": 1},
        headers={"Authorization": f"Bearer {authorized_user_token}"}
    )
    article_id = create_response.json()["id"]

    response = client.delete(
        f"/articles/{article_id}",
        headers={"Authorization": f"Bearer {authorized_user_token}"}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Article deleted"