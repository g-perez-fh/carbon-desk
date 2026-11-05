import pytest


@pytest.mark.django_db
def test_project_user_hashes_password_and_authenticates(client, django_user_model):
    user = django_user_model.objects.create_user(
        username="student", password="a-test-password-only"
    )
    assert user.password != "a-test-password-only"
    assert client.login(username="student", password="a-test-password-only")
