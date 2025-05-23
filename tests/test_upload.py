def test_upload_image(client, authorized_user_token):
    with open("tests/test_image.jpg", "rb") as image:
        response = client.post(
            "/upload/",
            files={"file": ("test_image.jpg", image, "image/jpeg")},
            headers={"Authorization": f"Bearer {authorized_user_token}"}
        )
    assert response.status_code == 200
    assert "url" in response.json()