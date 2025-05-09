# afkat_game/services/game_jam_service.py
from django.db import transaction
from django.utils import timezone
from rest_framework.exceptions import ValidationError

@transaction.atomic
def join_game_jam(user, game_jam):
    now = timezone.now()
    if now > game_jam.end_date:
        raise ValidationError("Cannot join a game jam that has already ended")
    if game_jam.participants.filter(id=user.id).exists():
        raise ValidationError("You are already a participant in this game jam")

    game_jam.participants.add(user)

def leave_game_jam(user, game_jam):
    game_jam.participants.remove(user)
