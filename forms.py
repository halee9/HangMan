"""forms.py - This file contains the class definitions for the forms
used by the Game."""

from protorpc import messages

class ScoreForm(messages.Message):
    """ScoreForm for outbound Score information"""
    user_name = messages.StringField(1, required=True)
    number_of_wins = messages.IntegerField(2, required=True)
    number_of_losses = messages.IntegerField(3, required=True)
    win_ratio = messages.IntegerField(4, required=True)
    score = messages.IntegerField(5, required=True)

class ScoreForms(messages.Message):
    """Return multiple ScoreForms"""
    items = messages.MessageField(ScoreForm, 1, repeated=True)

class GameForm(messages.Message):
    """GameForm for outbound game state information"""
    urlsafe_key = messages.StringField(1, required=True)
    output_words = messages.StringField(2, repeated=True)
    matches = messages.StringField(3, repeated=True)
    misses = messages.StringField(4, repeated=True)
    game_over = messages.BooleanField(5, required=True)
    won = messages.BooleanField(6)
    score = messages.IntegerField(7)
    message = messages.StringField(8)
    user_name = messages.StringField(9, required=True)

class GameForms(messages.Message):
    """Return multiple GameForms"""
    items = messages.MessageField(GameForm, 1, repeated=True)

class HistoryForm(messages.Message):
    """HistoryForm for outbound History information"""
    urlsafe_game_key = messages.StringField(1, required=True)
    number_of_tries = messages.IntegerField(2, required=True)
    guess = messages.StringField(3, required=True)
    message = messages.StringField(4, required=True)

class HistoryForms(messages.Message):
    """Return multiple HistoryForms"""
    items = messages.MessageField(HistoryForm, 1, repeated=True)

class StringMessage(messages.Message):
    """StringMessage-- outbound (single) string message"""
    message = messages.StringField(1, required=True)
