import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm

pytestmark = pytest.mark.django_db


def test_news_count(client, news_list):
    """Количество новостей на главной не превышает заданный лимит."""
    url = reverse('news:home')

    response = client.get(url)
    object_list = response.context['object_list']

    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client):
    """Новости на главной странице отсортированы от новых к старым."""
    url = reverse('news:home')

    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]

    assert all_dates == sorted(all_dates, reverse=True)


def test_comments_order(client, news, news_id_for_args, comments_list):
    """Комментарии на странице новости отсортированы от старых к новым."""
    url = reverse('news:detail', args=news_id_for_args)

    response = client.get(url)
    news = response.context['news']
    all_timestamps = [comment.created for comment in news.comment_set.all()]

    assert all_timestamps == sorted(all_timestamps)


def test_anonymous_client_has_no_form(client, news_id_for_args):
    """Анонимному пользователю недоступна форма для отправки комментария."""
    url = reverse('news:detail', args=news_id_for_args)

    response = client.get(url)

    assert 'form' not in response.context


def test_authorized_user_has_form(author_client, news_id_for_args):
    """Авторизованному пользователю доступна форма для отправки комментария."""
    url = reverse('news:detail', args=news_id_for_args)

    response = author_client.get(url)

    assert 'form' in response.context
    assert isinstance(response.context['form'], CommentForm)
