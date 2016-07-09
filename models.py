"""models.py - This file contains the class definitions for the Datastore
entities used by the Game. Because these classes are also regular Python
classes they can include methods (such as 'to_form' and 'new_game')."""

import random
from google.appengine.ext import ndb

TARGETWORDS = [
    'HANGMAN', 'MESSAGE', 'TOMATO', 'BANANA', 'DATABASE',
    'SOFTWARE', 'INTERNET', 'EXPLORER', 'LIBRARY', 'SUPERMAN'
]

MAX_MISSES_COUNT = 5

class User(ndb.Model):
    """User profile"""
    name = ndb.StringProperty(required=True)
    email =ndb.StringProperty()


class Game(ndb.Model):
    """Game object"""
    target = ndb.StringProperty(required=True)
    output_words = ndb.StringProperty(repeated=True)
    matches = ndb.StringProperty(repeated=True)
    misses = ndb.StringProperty(repeated=True)
    game_over = ndb.BooleanProperty(required=True, default=False)
    won = ndb.BooleanProperty()
    score = ndb.IntegerProperty(required=True)
    user = ndb.KeyProperty(required=True, kind='User')

    @classmethod
    def new_game(cls, user):
        """Creates and returns a new game"""
        target = TARGETWORDS[random.choice(range(1, len(TARGETWORDS)))]
        output = []
        for x in list(target):
            output.append('_')
        game = Game(user=user,
                    target=target,
                    output_words=output,
                    matches=[],
                    misses=[],
                    game_over=False,
                    score=0)
        game.put()
        return game

    def to_form(self, message):
        """Returns a GameForm representation of the Game"""
        form = GameForm()
        form.urlsafe_key = self.key.urlsafe()
        form.user_name = self.user.get().name
        form.output_words = self.output_words
        form.matches = self.matches
        form.misses = self.misses
        form.game_over = self.game_over
        form.won = self.won
        form.score = self.score
        form.message = message
        return form

    def end_game(self, won=False):
        """Ends the game - if won is True, the player won. - if won is False,
        the player lost."""
        self.game_over = True
        self.won = won
        if self.won:
            self.score = 100 + (MAX_MISSES_COUNT - len(self.misses)) * 20
        self.put()
        # Add the game result to the score
        score = Score.query(Score.user == self.user).get()
        if not score:
            score = Score.new_score(self.user)
        if self.won:
            score.number_of_wins = score.number_of_wins + 1
            score.score = score.score + self.score
        else:
            score.number_of_losses = score.number_of_losses + 1
        score.win_ratio = score.number_of_wins / (score.number_of_wins+score.number_of_losses) * 100
        score.put()

class History(ndb.Model):
    """Game Histroy object"""
    game = ndb.KeyProperty(required=True, kind='Game')
    number_of_tries = ndb.IntegerProperty(required=True)
    guess = ndb.StringProperty(required=True)
    message = ndb.StringProperty(required=True)

    @classmethod
    def push(cls, game, guess, message):
        qry = cls.query(cls.game == game).order(-cls.key)
        latest = qry.fetch(1)
        if latest:
            new_number_of_tries = latest[0].number_of_tries + 1
        else:
            new_number_of_tries = 1
        history = History(game=game,
                      number_of_tries=new_number_of_tries,
                      guess=guess,
                      message=message)
        history.put()
        return history

    def to_form(self):
        print self.message
        return HistoryForm(urlsafe_game_key=self.game.urlsafe(),
                           number_of_tries=self.number_of_tries,
                           guess=self.guess,
                           message=self.message)

class Score(ndb.Model):
    """Score object"""
    user = ndb.KeyProperty(required=True, kind='User')
    number_of_wins = ndb.IntegerProperty(required=True)
    number_of_losses = ndb.IntegerProperty(required=True)
    win_ratio = ndb.IntegerProperty(required=True)
    score = ndb.IntegerProperty(required=True)

    @classmethod
    def new_score(cls, user):
        score = Score(user=user,
                      number_of_wins=0,
                      number_of_losses=0,
                      win_ratio=0,
                      score=0)
        score.put()
        return score

    def to_form(self):
        return ScoreForm(user_name=self.user.get().name,
                         number_of_wins=self.number_of_wins,
                         number_of_losses=self.number_of_losses,
                         win_ratio=self.win_ratio,
                         score=self.score)

