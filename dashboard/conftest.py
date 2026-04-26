import pytest

from django.contrib.auth.models import Permission, User
from django.http import HttpResponse


@pytest.fixture
def user_without_permissions(client):
    user = User.objects.create_user(username="no_perm", password="password")
    client.login(username="no_perm", password="password")
    return user


@pytest.fixture
def user_can_change_commitment(client):
    user = User.objects.create_user(username="change_commitment", password="password")
    permission = Permission.objects.get(
        codename="change_commitment",
        content_type__app_label="projects",
    )
    user.user_permissions.add(permission)
    client.login(username="change_commitment", password="password")
    return user


@pytest.fixture
def user_can_change_projectobjectivecondition(client):
    user = User.objects.create_user(
        username="change_projectobjectivecondition", password="password"
    )
    permission = Permission.objects.get(
        codename="change_projectobjectivecondition",
        content_type__app_label="projects",
    )
    user.user_permissions.add(permission)
    client.login(username="change_projectobjectivecondition", password="password")
    return user


@pytest.fixture
def user_can_change_projectobjective(client):
    user = User.objects.create_user(
        username="change_projectobjective", password="password"
    )
    permission = Permission.objects.get(
        codename="change_projectobjective",
        content_type__app_label="projects",
    )
    user.user_permissions.add(permission)
    client.login(username="change_projectobjective", password="password")
    return user


@pytest.fixture
def user_can_change_workcycle(client):
    user = User.objects.create_user(username="change_workcycle", password="password")
    permission = Permission.objects.get(
        codename="change_workcycle",
        content_type__app_label="framework",
    )
    user.user_permissions.add(permission)
    client.login(username="change_workcycle", password="password")
    return user


@pytest.fixture
def user_can_view_workcycle(client):
    user = User.objects.create_user(username="view_workcycle", password="password")
    permission = Permission.objects.get(
        codename="view_workcycle",
        content_type__app_label="framework",
    )
    user.user_permissions.add(permission)
    client.login(username="view_workcycle", password="password")
    return user


@pytest.fixture
def user_is_staff(client):
    user = User.objects.create_user(
        username="staffmember", password="password", is_staff=True
    )
    client.login(username="staffmember", password="password")
    return user
