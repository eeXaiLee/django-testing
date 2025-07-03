from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects
from pytest_lazyfixture import lazy_fixture


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args, method_name',
    (
        ('news:home', None, 'get'),
        ('news:detail', lazy_fixture('news_id_for_args'), 'get'),
        ('users:login', None, 'get'),
        ('users:logout', None, 'post'),
        ('users:signup', None, 'get'),
    ),
)
def test_pages_availability(
    client, name, args, method_name
):
    """Публичные страницы доступны любому пользователю."""
    url = reverse(name, args=args)
    method = getattr(client, method_name)
    response = method(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lazy_fixture('author_client'), HTTPStatus.OK),
        (lazy_fixture('reader_client'), HTTPStatus.NOT_FOUND),
    )
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_availability_for_comment_edit_and_delete(
    parametrized_client, expected_status, name, comment_for_args
):
    """Удаление и редактирование комментария доступны автору комментария."""
    url = reverse(name, args=comment_for_args)
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_redirect_for_anonymous_client(client, name, comment_for_args):
    """Аноним перенаправляется на страницу входа при попытке редактирования."""
    login_url = reverse('users:login')
    url = reverse(name, args=comment_for_args)
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
