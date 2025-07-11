from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework import status
from afkat_game.models import Game, GameComments, GameRating, GameJam, Tags
import tempfile
import os
from datetime import timedelta
from django.utils import timezone

User = get_user_model()

class GameAPIIntegrationTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        
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
        
        self.tag1 = Tags.objects.create(value='action')
        self.tag2 = Tags.objects.create(value='puzzle')
        
        self.temp_game_file = tempfile.NamedTemporaryFile(suffix='.zip')
        self.temp_game_file.write(b'test game file content')
        self.temp_game_file.seek(0)
        
        self.temp_thumbnail = tempfile.NamedTemporaryFile(suffix='.jpg')
        self.temp_thumbnail.write(b'test thumbnail content')
        self.temp_thumbnail.seek(0)
        
        self.game = Game.objects.create(
            title='Test Game',
            description='A test game description',
            game_file=SimpleUploadedFile(
                name='test_game.zip',
                content=self.temp_game_file.read(),
                content_type='application/zip'
            ),
            thumbnail=SimpleUploadedFile(
                name='test_thumbnail.jpg',
                content=self.temp_thumbnail.read(),
                content_type='image/jpeg'
            ),
            creator=self.user1
        )
        self.game.tags.add(self.tag1)
        
        self.games_list_url = reverse('api/v1/games')
        self.game_detail_url = reverse('game-detail', kwargs={'pk': self.game.pk})
        self.game_comment_url = reverse('game-comment', kwargs={'pk': self.game.pk})
        self.game_rate_url = reverse('game-rate', kwargs={'pk': self.game.pk})
        self.game_download_url = reverse('game-download-game', kwargs={'pk': self.game.pk})
        
    def tearDown(self):
        self.temp_game_file.close()
        self.temp_thumbnail.close()
        
        if self.game.game_file:
            if os.path.isfile(self.game.game_file.path):
                os.remove(self.game.game_file.path)
        
        if self.game.thumbnail:
            if os.path.isfile(self.game.thumbnail.path):
                os.remove(self.game.thumbnail.path)
    
    def test_list_games(self):
        response = self.client.get(self.games_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Game')
    
    def test_retrieve_game(self):
        response = self.client.get(self.game_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Game')
        self.assertEqual(response.data['description'], 'A test game description')
        self.assertEqual(response.data['creator']['username'], 'testuser1')
    
    def test_create_game_authenticated(self):
        self.client.force_authenticate(user=self.user2)
        
        new_game_file = tempfile.NamedTemporaryFile(suffix='.zip')
        new_game_file.write(b'new game file content')
        new_game_file.seek(0)
        
        new_thumbnail = tempfile.NamedTemporaryFile(suffix='.jpg')
        new_thumbnail.write(b'new thumbnail content')
        new_thumbnail.seek(0)
        
        data = {
            'title': 'New Test Game',
            'description': 'A new test game description',
            'game_file': SimpleUploadedFile(
                name='new_test_game.zip',
                content=new_game_file.read(),
                content_type='application/zip'
            ),
            'thumbnail': SimpleUploadedFile(
                name='new_test_thumbnail.jpg',
                content=new_thumbnail.read(),
                content_type='image/jpeg'
            ),
            'tags': [self.tag1.id, self.tag2.id]
        }
        
        response = self.client.post(self.games_list_url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Game.objects.count(), 2)
        self.assertEqual(Game.objects.get(title='New Test Game').creator, self.user2)
        
        new_game_file.close()
        new_thumbnail.close()
    
    def test_create_game_unauthenticated(self):
        data = {
            'title': 'Unauthenticated Game',
            'description': 'This should fail',
        }
        
        response = self.client.post(self.games_list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Game.objects.count(), 1)  # Still only the one from setUp
    
    def test_update_game_owner(self):
        self.client.force_authenticate(user=self.user1)
        
        data = {
            'title': 'Updated Test Game',
            'description': 'An updated test game description',
        }
        
        response = self.client.patch(self.game_detail_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.game.refresh_from_db()
        self.assertEqual(self.game.title, 'Updated Test Game')
        self.assertEqual(self.game.description, 'An updated test game description')
    
    def test_delete_game_owner(self):
        self.client.force_authenticate(user=self.user1)
        
        response = self.client.delete(self.game_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Game.objects.count(), 0)
    
    def test_delete_game_non_owner(self):
        self.client.force_authenticate(user=self.user2)
        
        response = self.client.delete(self.game_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Game.objects.count(), 1)  # Game should still exist
    
    def test_comment_on_game(self):
        self.client.force_authenticate(user=self.user2)
        
        data = {
            'content': 'This is a test comment'
        }
        
        response = self.client.post(self.game_comment_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(GameComments.objects.count(), 1)
        self.assertEqual(GameComments.objects.first().content, 'This is a test comment')
        self.assertEqual(GameComments.objects.first().user, self.user2)
        self.assertEqual(GameComments.objects.first().game, self.game)
    
    def test_rate_game(self):
        self.client.force_authenticate(user=self.user2)
        
        data = {
            'rating': 4
        }
        
        response = self.client.post(self.game_rate_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(GameRating.objects.count(), 1)
        self.assertEqual(GameRating.objects.first().rating, 4)
        self.assertEqual(GameRating.objects.first().user, self.user2)
        self.assertEqual(GameRating.objects.first().game, self.game)
        
        self.game.refresh_from_db()
        self.assertEqual(self.game.rating, 4.0)
    
    def test_download_game(self):
        response = self.client.get(self.game_download_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Disposition'], f'attachment; filename={self.game.game_file.name}')
        
        self.game.refresh_from_db()
        self.assertEqual(self.game.download_count, 1)


class GameJamAPIIntegrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        
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
        
        self.temp_game_file = tempfile.NamedTemporaryFile(suffix='.zip')
        self.temp_game_file.write(b'test game file content')
        self.temp_game_file.seek(0)
        
        self.temp_thumbnail = tempfile.NamedTemporaryFile(suffix='.jpg')
        self.temp_thumbnail.write(b'test thumbnail content')
        self.temp_thumbnail.seek(0)
        
        self.game = Game.objects.create(
            title='Test Game',
            description='A test game description',
            game_file=SimpleUploadedFile(
                name='test_game.zip',
                content=self.temp_game_file.read(),
                content_type='application/zip'
            ),
            thumbnail=SimpleUploadedFile(
                name='test_thumbnail.jpg',
                content=self.temp_thumbnail.read(),
                content_type='image/jpeg'
            ),
            creator=self.user1
        )
        
        now = timezone.now()
        self.game_jam = GameJam.objects.create(
            title='Test Game Jam',
            description='A test game jam description',
            created_by=self.user1,
            start_date=now - timedelta(days=1),
            end_date=now + timedelta(days=7),
            theme='Test Theme',
            prizes='1st place: $100'
        )
        
        # URLs
        self.game_jams_list_url = reverse('gamejam-list')
        self.game_jam_detail_url = reverse('gamejam-detail', kwargs={'pk': self.game_jam.pk})
        self.game_jam_participate_url = reverse('gamejam-participate', kwargs={'pk': self.game_jam.pk})
        self.game_jam_participants_url = reverse('gamejam-participants', kwargs={'pk': self.game_jam.pk})
        self.game_jam_submit_game_url = reverse('gamejam-submit-game', kwargs={'pk': self.game_jam.pk})
        
    def tearDown(self):
        self.temp_game_file.close()
        self.temp_thumbnail.close()
        
        if self.game.game_file:
            if os.path.isfile(self.game.game_file.path):
                os.remove(self.game.game_file.path)
        
        if self.game.thumbnail:
            if os.path.isfile(self.game.thumbnail.path):
                os.remove(self.game.thumbnail.path)
    
    def test_list_game_jams(self):
        response = self.client.get(self.game_jams_list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Game Jam')
    
    def test_retrieve_game_jam(self):
        response = self.client.get(self.game_jam_detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Game Jam')
        self.assertEqual(response.data['description'], 'A test game jam description')
        self.assertEqual(response.data['created_by'], 'testuser1')
        self.assertEqual(response.data['theme'], 'Test Theme')
        self.assertEqual(response.data['prizes'], '1st place: $100')
        self.assertTrue(response.data['is_active'])
    
    def test_create_game_jam_authenticated(self):
        self.client.force_authenticate(user=self.user2)
        
        now = timezone.now()
        data = {
            'title': 'New Test Game Jam',
            'description': 'A new test game jam description',
            'start_date': (now + timedelta(days=1)).isoformat(),
            'end_date': (now + timedelta(days=8)).isoformat(),
            'theme': 'New Test Theme',
            'prizes': '1st place: $200'
        }
        
        response = self.client.post(self.game_jams_list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(GameJam.objects.count(), 2)
        self.assertEqual(GameJam.objects.get(title='New Test Game Jam').created_by, self.user2)
    
    def test_create_game_jam_unauthenticated(self):
        now = timezone.now()
        data = {
            'title': 'Unauthenticated Game Jam',
            'description': 'This should fail',
            'start_date': (now + timedelta(days=1)).isoformat(),
            'end_date': (now + timedelta(days=8)).isoformat(),
            'theme': 'Fail Theme'
        }
        
        response = self.client.post(self.game_jams_list_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(GameJam.objects.count(), 1)
    
    def test_participate_in_game_jam(self):
        self.client.force_authenticate(user=self.user2)
        
        data = {
            'action': 'join'
        }
        
        response = self.client.post(self.game_jam_participate_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'joined game jam')
        self.game_jam.refresh_from_db()
        self.assertTrue(self.game_jam.participants.filter(id=self.user2.id).exists())
        
        data = {
            'action': 'leave'
        }
        
        response = self.client.post(self.game_jam_participate_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'left game jam')
        self.game_jam.refresh_from_db()
        self.assertFalse(self.game_jam.participants.filter(id=self.user2.id).exists())
    
    def test_view_participants(self):
        self.game_jam.participants.add(self.user2)
        
        response = self.client.get(self.game_jam_participants_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['username'], 'testuser2')
    
    def test_submit_game_to_jam(self):
        self.client.force_authenticate(user=self.user1)
        
        self.game_jam.participants.add(self.user1)
        
        data = {
            'game_id': self.game.id
        }
        
        response = self.client.post(self.game_jam_submit_game_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'game submitted successfully')
        self.game_jam.refresh_from_db()
        self.assertTrue(self.game_jam.submitted_games.filter(id=self.game.id).exists())
    
    def test_submit_game_not_participant(self):
        self.client.force_authenticate(user=self.user2)
        
        data = {
            'game_id': self.game.id
        }
        
        response = self.client.post(self.game_jam_submit_game_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.game_jam.refresh_from_db()
        self.assertFalse(self.game_jam.submitted_games.filter(id=self.game.id).exists())
    
    def test_submit_game_not_owner(self):
        self.client.force_authenticate(user=self.user2)
        
        self.game_jam.participants.add(self.user2)
        
        data = {
            'game_id': self.game.id
        }
        
        response = self.client.post(self.game_jam_submit_game_url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.game_jam.refresh_from_db()
        self.assertFalse(self.game_jam.submitted_games.filter(id=self.game.id).exists())