import pytest
from datetime import datetime, timedelta

from django.conf import settings
from django.test.client import Client
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News


def pytest_collection_modifyitems(items):
    for item in items:
        item.add_marker('django_db')


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости',
        date=timezone.now(),
    )
    return news


@pytest.fixture
def news_list():
    today = datetime.today()
    news_list = [
        News(
            title=f'Новость {index}',
            text='Просто текст.',
            date=today - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    News.objects.bulk_create(news_list)


@pytest.fixture
def news_id_for_args(news):
    return (news.id,)


@pytest.fixture
def comment(news, author):
    comment = Comment.objects.create(
        news=news,
        text='Текст новости',
        created=timezone.now(),
        author=author,
    )
    return comment


@pytest.fixture
def comment_list(news, author):
    now = timezone.now()
    # Создаём комментарии в цикле.
    for index in range(10):
        # Создаём объект и записываем его в переменную.
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        # Сразу после создания меняем время создания комментария.
        comment.created = now + timedelta(days=index)
        # И сохраняем эти изменения.
        comment.save()


@pytest.fixture
def comment_id_for_args(news):
    return (news.id,)


@pytest.fixture
def comment_form_data():
    return {
        'text': 'Новый текст',
        'created': timezone.now(),
    }


@pytest.fixture
def detail_url(news):
    detail_url = reverse('news:detail', args=(news.id,))
    return detail_url
