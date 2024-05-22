from http import HTTPStatus
from pytest_django.asserts import assertRedirects, assertFormError

import pytest
from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment, News


def test_anonymous_user_cant_create_comment(news, client, comment_form_data):
    url = reverse('news:detail', args=(news.id,))
    client.post(url, data=comment_form_data)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_can_create_comment(
    news, author, author_client, comment_form_data
):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=comment_form_data)
    assertRedirects(response, f'{url}#comments')
    comments_count = Comment.objects.count()
    assert comments_count == 1
    comment = Comment.objects.get()
    assert comment.text == comment_form_data['text']
    assert comment.news == news
    assert comment.author == author


def test_user_cant_use_bad_words(
    news, author, author_client, comment_form_data
):
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_author_can_delete_comment(news, author_client, comment):
    delete_url = reverse('news:delete', args=(comment.id,))
    url_to_comments = reverse('news:detail', args=(news.id,)) + '#comments'
    response = author_client.delete(delete_url)
    assertRedirects(response, url_to_comments)
    comments_count = Comment.objects.count()
    assert comments_count == 0


def test_user_cant_delete_comment_of_another_user(not_author_client, comment):
    delete_url = reverse('news:delete', args=(comment.id,))
    response = not_author_client.delete(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == 1


def test_author_can_edit_comment(
    news, author_client, comment, comment_form_data
):
    edit_url = reverse('news:edit', args=(comment.id,))
    url_to_comments = reverse('news:detail', args=(news.id,)) + '#comments'
    comment_form_data['text'] = 'Новый текст'
    response = author_client.post(edit_url, data=comment_form_data)
    assertRedirects(response, url_to_comments)
    comment.refresh_from_db()
    assert comment.text == comment_form_data['text']


def test_user_cant_edit_comment_of_another_user(
    not_author_client, comment, comment_form_data
):
    edit_url = reverse('news:edit', args=(comment.id,))
    old_text = comment.text
    comment_form_data['text'] = 'Новый текст'
    response = not_author_client.post(edit_url, data=comment_form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == old_text
