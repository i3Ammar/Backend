
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework import status
from afkat_home.models import Post, Comment
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile
import os

User = get_user_model()

class PostModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='StrongPassword123!'
        )

        self.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            summary='Test Summary',
            content='Test Content',
            author=self.user,
            published_at=timezone.now()
        )

    def test_post_creation(self):
        self.assertEqual(self.post.title, 'Test Post')
        self.assertEqual(self.post.slug, 'test-post')
        self.assertEqual(self.post.summary, 'Test Summary')
        self.assertEqual(self.post.content, 'Test Content')
        self.assertEqual(self.post.author, self.user)
        self.assertIsNotNone(self.post.published_at)

    def test_post_string_representation(self):
        self.assertEqual(str(self.post), 'Test Post')

    def test_post_ordering(self):
        earlier_post = Post.objects.create(
            title='Earlier Post',
            slug='earlier-post',
            summary='Earlier Summary',
            content='Earlier Content',
            author=self.user,
            published_at=timezone.now() - timezone.timedelta(days=1)
        )

        later_post = Post.objects.create(
            title='Later Post',
            slug='later-post',
            summary='Later Summary',
            content='Later Content',
            author=self.user,
            published_at=timezone.now() + timezone.timedelta(days=1)
        )

        posts = Post.objects.all()
        self.assertEqual(posts[0], later_post)
        self.assertEqual(posts[1], self.post)
        self.assertEqual(posts[2], earlier_post)

    def test_post_slug_generation(self):
        post = Post.objects.create(
            title='Auto Slug Test',
            summary='Auto Slug Summary',
            content='Auto Slug Content',
            author=self.user,
            published_at=timezone.now()
        )

        self.assertEqual(post.slug, 'auto-slug-test')

    def test_post_unique_slug(self):
        post2 = Post.objects.create(
            title='Test Post',
            summary='Another Summary',
            content='Another Content',
            author=self.user,
            published_at=timezone.now()
        )

        self.assertNotEqual(post2.slug, self.post.slug)
        self.assertTrue(post2.slug.startswith('test-post-'))

    def test_post_absolute_url(self):
        expected_url = reverse('afkat_home_api:post-detail', kwargs={'pk': self.post.pk})
        self.assertEqual(self.post.get_absolute_url(), expected_url)


class CommentModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='StrongPassword123!'
        )

        self.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            summary='Test Summary',
            content='Test Content',
            author=self.user,
            published_at=timezone.now()
        )

        self.comment = Comment.objects.create(
            creator=self.user,
            content='Test Comment',
            content_object=self.post
        )

    def test_comment_creation(self):
        self.assertEqual(self.comment.content, 'Test Comment')
        self.assertEqual(self.comment.creator, self.user)
        self.assertEqual(self.comment.content_object, self.post)

    def test_comment_on_post(self):
        post_comments = self.post.comments.all()

        self.assertEqual(post_comments.count(), 1)
        self.assertEqual(post_comments.first(), self.comment)


class PostAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='StrongPassword123!'
        )

        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='StrongPassword123!',
            is_staff=True
        )

        self.post = Post.objects.create(
            title='Test Post',
            slug='test-post',
            summary='Test Summary',
            content='Test Content',
            author=self.user,
            published_at=timezone.now()
        )

        self.temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        self.temp_file.write(b'test content')
        self.temp_file.seek(0)

        self.post_list_url = reverse('post-list')
        self.post_detail_url = reverse('post-detail', args=[self.post.id])
        self.post_mine_url = reverse('post-mine')
        self.post_themes_url = reverse('post-themes')
        self.post_like_url = reverse('post-like', args=[self.post.id])

    def tearDown(self):
        self.temp_file.close()

        if self.post.image:
            if os.path.isfile(self.post.image.path):
                os.remove(self.post.image.path)

    def test_list_posts(self):
        response = self.client.get(self.post_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_post(self):
        response = self.client.get(self.post_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Post')

    def test_create_post_authenticated(self):
        self.client.force_authenticate(user=self.user)

        data = {
            'title': 'New Test Post',
            'summary': 'New Test Summary',
            'content': 'New Test Content',
            'published_at': timezone.now().isoformat()
        }

        response = self.client.post(self.post_list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Post.objects.count(), 2)
        self.assertEqual(Post.objects.last().title, 'New Test Post')

    def test_create_post_unauthenticated(self):
        data = {
            'title': 'New Test Post',
            'summary': 'New Test Summary',
            'content': 'New Test Content',
            'published_at': timezone.now().isoformat()
        }

        response = self.client.post(self.post_list_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Post.objects.count(), 1)

    def test_update_post_owner(self):
        self.client.force_authenticate(user=self.user)

        data = {
            'title': 'Updated Test Post',
            'summary': 'Updated Test Summary',
            'content': 'Updated Test Content',
            'published_at': timezone.now().isoformat()
        }

        response = self.client.patch(self.post_detail_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Updated Test Post')

    def test_update_post_non_owner(self):
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='StrongPassword123!'
        )

        self.client.force_authenticate(user=other_user)

        data = {
            'title': 'Updated Test Post',
            'summary': 'Updated Test Summary',
            'content': 'Updated Test Content',
            'published_at': timezone.now().isoformat()
        }

        response = self.client.patch(self.post_detail_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.post.refresh_from_db()
        self.assertEqual(self.post.title, 'Test Post')

    def test_delete_post_owner(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.delete(self.post_detail_url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Post.objects.count(), 0)

    def test_delete_post_non_owner(self):
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='StrongPassword123!'
        )

        self.client.force_authenticate(user=other_user)

        response = self.client.delete(self.post_detail_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Post.objects.count(), 1)

    def test_mine_posts(self):
        self.client.force_authenticate(user=self.user)

        Post.objects.create(
            title='Another Test Post',
            slug='another-test-post',
            summary='Another Test Summary',
            content='Another Test Content',
            author=self.user,
            published_at=timezone.now()
        )

        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='StrongPassword123!'
        )

        Post.objects.create(
            title='Other User Post',
            slug='other-user-post',
            summary='Other User Summary',
            content='Other User Content',
            author=other_user,
            published_at=timezone.now()
        )

        response = self.client.get(self.post_mine_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

    def test_mine_posts_unauthenticated(self):
        response = self.client.get(self.post_mine_url)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_like_post(self):
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.post_like_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['liked'])
        self.assertEqual(response.data['likes_count'], 1)

        self.post.refresh_from_db()
        self.assertTrue(self.post.likes.filter(id=self.user.id).exists())

    def test_unlike_post(self):
        self.client.force_authenticate(user=self.user)

        self.post.likes.add(self.user)

        response = self.client.post(self.post_like_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['liked'])
        self.assertEqual(response.data['likes_count'], 0)

        self.post.refresh_from_db()
        self.assertFalse(self.post.likes.filter(id=self.user.id).exists())
