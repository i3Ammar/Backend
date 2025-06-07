
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from afkat_art.models import ArtModel, ArtComment, ArtRating, TagsModel
import tempfile
import os

User = get_user_model()

class ArtModelTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='StrongPassword123!'
        )

        # Create a test tag
        self.tag = TagsModel.objects.create(value='test_tag')

        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.obj')
        self.temp_file.write(b'test content')
        self.temp_file.seek(0)

        # Create a test art model
        self.art = ArtModel.objects.create(
            title='Test Art',
            description='Test Description',
            author=self.user,
            model_file=SimpleUploadedFile(
                name='test_model.obj',
                content=self.temp_file.read(),
                content_type='application/octet-stream'
            )
        )
        self.art.tags.add(self.tag)

    def tearDown(self):
        # Clean up temporary files
        self.temp_file.close()

        # Clean up uploaded files
        if self.art.model_file:
            if os.path.isfile(self.art.model_file.path):
                os.remove(self.art.model_file.path)

        if self.art.thumbnail:
            if os.path.isfile(self.art.thumbnail.path):
                os.remove(self.art.thumbnail.path)

    def test_art_creation(self):
        """Test that an art model can be created"""
        self.assertEqual(self.art.title, 'Test Art')
        self.assertEqual(self.art.description, 'Test Description')
        self.assertEqual(self.art.author, self.user)
        self.assertEqual(self.art.tags.count(), 1)
        self.assertEqual(self.art.tags.first(), self.tag)

    def test_art_string_representation(self):
        """Test the string representation of an art model"""
        self.assertEqual(str(self.art), 'Test Art')

    def test_art_ordering(self):
        """Test that art models are ordered by created_at in descending order"""
        art2 = ArtModel.objects.create(
            title='Test Art 2',
            description='Test Description 2',
            author=self.user,
            model_file=SimpleUploadedFile(
                name='test_model2.obj',
                content=b'test content 2',
                content_type='application/octet-stream'
            )
        )

        arts = ArtModel.objects.all()
        self.assertEqual(arts[0], art2)  # Newest first
        self.assertEqual(arts[1], self.art)

        # Clean up
        if art2.model_file:
            if os.path.isfile(art2.model_file.path):
                os.remove(art2.model_file.path)


class ArtCommentTests(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='StrongPassword123!'
        )

        # Create a test art model
        self.art = ArtModel.objects.create(
            title='Test Art',
            description='Test Description',
            author=self.user,
            model_file=SimpleUploadedFile(
                name='test_model.obj',
                content=b'test content',
                content_type='application/octet-stream'
            )
        )

        # Create a test comment
        self.comment = ArtComment.objects.create(
            art=self.art,
            user=self.user,
            content='Test Comment'
        )

    def tearDown(self):
        # Clean up uploaded files
        if self.art.model_file:
            if os.path.isfile(self.art.model_file.path):
                os.remove(self.art.model_file.path)

    def test_comment_creation(self):
        """Test that a comment can be created"""
        self.assertEqual(self.comment.content, 'Test Comment')
        self.assertEqual(self.comment.user, self.user)
        self.assertEqual(self.comment.art, self.art)

    def test_comment_string_representation(self):
        """Test the string representation of a comment"""
        expected_str = f"Comment by {self.user.username} on {self.art.title}"
        self.assertEqual(str(self.comment), expected_str)

    def test_comment_ordering(self):
        """Test that comments are ordered by created_at in descending order"""
        comment2 = ArtComment.objects.create(
            art=self.art,
            user=self.user,
            content='Test Comment 2'
        )

        comments = ArtComment.objects.all()
        self.assertEqual(comments[0], comment2)  # Newest first
        self.assertEqual(comments[1], self.comment)


class ArtRatingTests(TestCase):
    def setUp(self):
        # Create test users
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='StrongPassword123!'
        )

        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='StrongPassword123!'
        )

        # Create a test art model
        self.art = ArtModel.objects.create(
            title='Test Art',
            description='Test Description',
            author=self.user1,
            model_file=SimpleUploadedFile(
                name='test_model.obj',
                content=b'test content',
                content_type='application/octet-stream'
            )
        )

    def tearDown(self):
        # Clean up uploaded files
        if self.art.model_file:
            if os.path.isfile(self.art.model_file.path):
                os.remove(self.art.model_file.path)

    def test_rating_creation(self):
        """Test that a rating can be created"""
        rating = ArtRating.objects.create(
            art=self.art,
            user=self.user2,
            rating=4
        )

        self.assertEqual(rating.rating, 4)
        self.assertEqual(rating.user, self.user2)
        self.assertEqual(rating.art, self.art)

        # Check that the art's rating was updated
        self.art.refresh_from_db()
        self.assertEqual(self.art.rating, 4.0)

    def test_rating_update(self):
        """Test that updating a rating updates the art's average rating"""
        # Create initial rating
        rating = ArtRating.objects.create(
            art=self.art,
            user=self.user2,
            rating=4
        )

        # Update rating
        rating.rating = 5
        rating.save()

        # Check that the art's rating was updated
        self.art.refresh_from_db()
        self.assertEqual(self.art.rating, 5.0)

    def test_multiple_ratings(self):
        """Test that multiple ratings are averaged correctly"""
        # Create ratings from different users
        ArtRating.objects.create(
            art=self.art,
            user=self.user1,
            rating=5
        )

        ArtRating.objects.create(
            art=self.art,
            user=self.user2,
            rating=3
        )

        # Check that the art's rating is the average
        self.art.refresh_from_db()
        self.assertEqual(self.art.rating, 4.0)

    def test_rating_string_representation(self):
        """Test the string representation of a rating"""
        rating = ArtRating.objects.create(
            art=self.art,
            user=self.user2,
            rating=4
        )

        expected_str = f"{self.user2.username} rated {self.art.title}: {rating.rating}/5"
        self.assertEqual(str(rating), expected_str)


class ArtAPITests(TestCase):
    def setUp(self):
        # Create a test client
        self.client = APIClient()

        # Create test users
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='StrongPassword123!'
        )

        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='StrongPassword123!'
        )

        # Create a test tag
        self.tag = TagsModel.objects.create(value='test_tag')

        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(suffix='.obj')
        self.temp_file.write(b'test content')
        self.temp_file.seek(0)

        # Create a test art model
        self.art = ArtModel.objects.create(
            title='Test Art',
            description='Test Description',
            author=self.user,
            model_file=SimpleUploadedFile(
                name='test_model.obj',
                content=self.temp_file.read(),
                content_type='application/octet-stream'
            )
        )
        self.art.tags.add(self.tag)

        # Define API endpoints
        self.art_list_url = reverse('art-list')
        self.art_detail_url = reverse('art-detail', args=[self.art.id])
        self.art_comment_url = reverse('art-comment', args=[self.art.id])
        self.art_rate_url = reverse('art-rate', args=[self.art.id])

    def tearDown(self):
        # Clean up temporary files
        self.temp_file.close()

        # Clean up uploaded files
        if self.art.model_file:
            if os.path.isfile(self.art.model_file.path):
                os.remove(self.art.model_file.path)

        if self.art.thumbnail:
            if os.path.isfile(self.art.thumbnail.path):
                os.remove(self.art.thumbnail.path)

    def test_list_arts(self):
        """Test retrieving a list of arts"""
        response = self.client.get(self.art_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_art(self):
        """Test retrieving a single art"""
        response = self.client.get(self.art_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Art')

    def test_create_art_authenticated(self):
        """Test creating an art when authenticated"""
        self.client.force_authenticate(user=self.user)

        # Create a new temporary file
        with tempfile.NamedTemporaryFile(suffix='.obj') as temp_file:
            temp_file.write(b'new test content')
            temp_file.seek(0)

            data = {
                'title': 'New Test Art',
                'description': 'New Test Description',
                'model_file': temp_file,
                'tags': [self.tag.id]
            }

            response = self.client.post(self.art_list_url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ArtModel.objects.count(), 2)
        self.assertEqual(ArtModel.objects.last().title, 'New Test Art')

        # Clean up
        new_art = ArtModel.objects.last()
        if new_art.model_file:
            if os.path.isfile(new_art.model_file.path):
                os.remove(new_art.model_file.path)

    def test_create_art_unauthenticated(self):
        """Test creating an art when unauthenticated"""
        # Create a new temporary file
        with tempfile.NamedTemporaryFile(suffix='.obj') as temp_file:
            temp_file.write(b'new test content')
            temp_file.seek(0)

            data = {
                'title': 'New Test Art',
                'description': 'New Test Description',
                'model_file': temp_file,
                'tags': [self.tag.id]
            }

            response = self.client.post(self.art_list_url, data, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(ArtModel.objects.count(), 1)

    def test_comment_on_art(self):
        """Test commenting on an art"""
        self.client.force_authenticate(user=self.user)

        data = {
            'content': 'Test Comment'
        }

        response = self.client.post(self.art_comment_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ArtComment.objects.count(), 1)
        self.assertEqual(ArtComment.objects.first().content, 'Test Comment')

    def test_rate_art(self):
        """Test rating an art"""
        self.client.force_authenticate(user=self.user)

        data = {
            'rating': 4
        }

        response = self.client.post(self.art_rate_url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(ArtRating.objects.count(), 1)
        self.assertEqual(ArtRating.objects.first().rating, 4)

        # Check that the art's rating was updated
        self.art.refresh_from_db()
        self.assertEqual(self.art.rating, 4.0)
