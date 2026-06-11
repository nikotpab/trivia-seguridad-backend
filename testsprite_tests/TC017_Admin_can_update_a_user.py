import requests
import time

BASE_URL = "http://localhost:8000/api/v1"
ADMIN_EMAIL = "admin@seguridaddeoro.co"
ADMIN_PASSWORD = "Password123!"
TIMEOUT = 30

def test_tc017_admin_can_update_user():
    # Step 1: Login as admin to get access_token
    login_resp = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD},
        timeout=TIMEOUT,
    )
    assert login_resp.status_code == 200, f"Login failed: {login_resp.text}"
    login_data = login_resp.json()
    access_token = login_data.get("access_token")
    assert isinstance(access_token, str) and access_token, "access_token missing or empty"
    headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

    # Step 2: Create a fresh user with unique email
    unique_email = f"qa.user.{int(time.time()*1000)}@seguridaddeoro.co"
    create_payload = {
        "email": unique_email,
        "full_name": "Usuario QA",
        "role": "guarda",
        "password": "Password123!"
    }

    user_id = None
    try:
        create_resp = requests.post(
            f"{BASE_URL}/users",
            json=create_payload,
            headers=headers,
            timeout=TIMEOUT,
        )
        assert create_resp.status_code == 201, f"User creation failed: {create_resp.text}"
        created_user = create_resp.json().get("user")
        assert created_user, "Created user data missing"
        user_id = created_user.get("id")
        assert user_id, "Created user id missing"

        # Step 3: Update the user's full_name with PATCH
        update_payload = {"full_name": "Nombre Actualizado"}
        patch_resp = requests.patch(
            f"{BASE_URL}/users/{user_id}",
            json=update_payload,
            headers=headers,
            timeout=TIMEOUT,
        )
        assert patch_resp.status_code == 200, f"User update failed: {patch_resp.text}"
        updated_user = patch_resp.json().get("user")
        assert updated_user, "Updated user data missing"
        assert updated_user.get("full_name") == "Nombre Actualizado", (
            f"User full_name not updated, got: {updated_user.get('full_name')}"
        )
    finally:
        # Cleanup: Delete the created user if created
        if user_id:
            requests.delete(
                f"{BASE_URL}/users/{user_id}",
                headers=headers,
                timeout=TIMEOUT,
            )

test_tc017_admin_can_update_user()