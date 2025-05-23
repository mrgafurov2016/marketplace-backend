def test_get_profile(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/profile/", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data
    assert "full_name" in data


def test_update_profile(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    new_data = {
        "full_name": "Updated User",
        "email": "test@example.com",
        "password": "newpassword123"
    }
    response = client.put("/profile/", headers=headers, json=new_data)
    assert response.status_code == 200
    assert response.json()["message"] == "Profile updated successfully"


def test_delete_profile(client, token):
    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete("/profile/", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "Account deleted"