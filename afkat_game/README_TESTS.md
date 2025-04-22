# afkat_game Integration Tests

This directory contains integration tests for the afkat_game app. These tests verify that the API endpoints work correctly and interact with the database as expected.

## Test Coverage

The tests cover the following functionality:

### Game API Tests (`GameAPIIntegrationTests`)

1. **Listing Games**: Tests retrieving a list of games.
2. **Retrieving a Game**: Tests retrieving a single game's details.
3. **Creating a Game**: Tests creating a new game (both authenticated and unauthenticated).
4. **Updating a Game**: Tests updating a game as the owner.
5. **Deleting a Game**: Tests deleting a game (both as owner and non-owner).
6. **Commenting on a Game**: Tests adding a comment to a game.
7. **Rating a Game**: Tests rating a game and verifies the average rating is updated.
8. **Downloading a Game**: Tests downloading a game file and verifies the download count is incremented.

### Game Jam API Tests (`GameJamAPIIntegrationTests`)

1. **Listing Game Jams**: Tests retrieving a list of game jams.
2. **Retrieving a Game Jam**: Tests retrieving a single game jam's details.
3. **Creating a Game Jam**: Tests creating a new game jam (both authenticated and unauthenticated).
4. **Participating in a Game Jam**: Tests joining and leaving a game jam.
5. **Viewing Participants**: Tests retrieving the list of participants in a game jam.
6. **Submitting a Game**: Tests submitting a game to a game jam (as participant/non-participant and owner/non-owner).

## Running the Tests

To run all tests for the afkat_game app:

```bash
python manage.py test afkat_game
```

To run a specific test class:

```bash
python manage.py test afkat_game.tests.GameAPIIntegrationTests
python manage.py test afkat_game.tests.GameJamAPIIntegrationTests
```

To run a specific test method:

```bash
python manage.py test afkat_game.tests.GameAPIIntegrationTests.test_list_games
```

## Test Structure

Each test class follows a similar structure:

1. **setUp**: Initializes test data, including:
   - Creating test users
   - Creating test models (games, tags, game jams)
   - Setting up test files
   - Defining API endpoints

2. **tearDown**: Cleans up after tests, including:
   - Closing temporary files
   - Removing media files created during tests

3. **Test Methods**: Each test method focuses on testing a specific functionality.

## Test Dependencies

The tests require:

1. Django's TestCase
2. Django REST framework's APIClient
3. SimpleUploadedFile for file uploads
4. tempfile for creating temporary files

## Adding More Tests

When adding new tests:

1. Follow the existing pattern of setUp, test methods, and tearDown.
2. Ensure each test is independent and can run on its own.
3. Use descriptive method names that clearly indicate what is being tested.
4. Clean up any resources created during the test.

## Common Issues

1. **File Cleanup**: If tests fail, temporary files might not be properly cleaned up. The tearDown method attempts to handle this, but manual cleanup might be needed in some cases.

2. **URL Patterns**: The tests assume certain URL patterns exist. If URLs change, the tests need to be updated.

3. **Database State**: Each test should create its own data and not rely on data created by other tests.

## Best Practices

1. **Test Both Success and Failure Cases**: Don't just test that things work when used correctly; also test that they fail appropriately when used incorrectly.

2. **Keep Tests Fast**: Integration tests can be slow, so keep them focused and efficient.

3. **Use Mocks When Appropriate**: For external services or slow operations, consider using mocks.

4. **Update Tests When Code Changes**: When you change the code, update the tests to match.