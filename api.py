# -*- coding: utf-8 -*-`
"""api.py - Create and configure the Game API exposing the resources.
This can also contain game logic. For more complex games it would be wise to
move game logic to another file. Ideally the API will be simple, concerned
primarily with communication to/from the API's users."""

import logging
import endpoints

from protorpc import remote, messages
from google.appengine.api import memcache
from google.appengine.api import taskqueue

from models import User, Game, Score, History
from forms import StringMessage, GameForm, ScoreForms, GameForms, HistoryForms
from utils import get_by_urlsafe

NEW_GAME_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1,required=True))
GET_GAME_REQUEST = endpoints.ResourceContainer(urlsafe_game_key=messages.StringField(1,required=True))
CANCEL_GAME_REQUEST = endpoints.ResourceContainer(urlsafe_game_key=messages.StringField(1,required=True))
MAKE_GUESS_REQUEST = endpoints.ResourceContainer(urlsafe_game_key=messages.StringField(1,required=True),
                                                guess=messages.StringField(2,required=True))
USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1,required=True))
NEW_USER_REQUEST = endpoints.ResourceContainer(user_name=messages.StringField(1,required=True),
                                               email=messages.StringField(2,required=True))
SCORE_REQUEST = endpoints.ResourceContainer(number_of_results=messages.StringField(1))
MEMCACHE_MOVES_REMAINING = 'MOVES_REMAINING'

@endpoints.api(name='hang_man', version='v1')
class HangManApi(remote.Service):
    """Game API"""
    @endpoints.method(request_message=NEW_USER_REQUEST,
                      response_message=StringMessage,
                      path='user',
                      name='create_user',
                      http_method='POST')
    def create_user(self, request):
        """Create a User. Requires a unique username"""
        if User.query(User.name == request.user_name).get():
            raise endpoints.ConflictException(
                    'A User with that name already exists!')
        user = User(name=request.user_name, email=request.email)
        user.put()
        return StringMessage(message='User {} created!'.format(
                request.user_name))

    @endpoints.method(request_message=NEW_GAME_REQUEST,
                      response_message=GameForm,
                      path='game',
                      name='new_game',
                      http_method='POST')
    def new_game(self, request):
        """Creates new game"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        try:
            game = Game.new_game(user.key)

        # Use a task queue to update the average attempts remaining.
        # This operation is not needed to complete the creation of a new game
        # so it is performed out of sequence.
        # taskqueue.add(url='/tasks/cache_average_attempts')

    	except ValueError:
    		print 'game error'
    	else:
        	return game.to_form('Good luck playing Hangman!')

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='get_game',
                      http_method='GET')
    def get_game(self, request):
        """Return the current game state."""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            return game.to_form('Time to make a move!')
        else:
            raise endpoints.NotFoundException('Game not found!')

        #--------------------------
    @endpoints.method(request_message=CANCEL_GAME_REQUEST,
                      response_message=StringMessage,
                      path='game/{urlsafe_game_key}',
                      name='cancel_game',
                      http_method='DELETE')
    def cancel_game(self, request):
        """Cancel game if the game is not over"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game:
            if game.game_over:
                raise endpoints.ForbiddenException('Illegal action: Game is already over.')
            else:
                game.key.delete()
                return StringMessage(message='The game was deleted')
        else:
            raise endpoints.NotFoundException('Game not found!')


    @endpoints.method(request_message=USER_REQUEST,
                      response_message=GameForms,
                      path='games/user/{user_name}',
                      name='get_user_games',
                      http_method='GET')
    def get_user_games(self, request):
        """Returns all of an individual User's games"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        games = Game.query(Game.user == user.key)
        return GameForms(items=[game.to_form('') for game in games])



    @endpoints.method(request_message=MAKE_GUESS_REQUEST,
                      response_message=GameForm,
                      path='game/{urlsafe_game_key}',
                      name='make_guess',
                      http_method='PUT')
    def make_guess(self, request):
        """Makes a move. Returns a game state with message"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if game.game_over:
            return game.to_form('Game already over!')

        guess = request.guess[0].upper()
        """The Guess is only a character"""
        if not guess.isalpha():
            msg = 'Should put an alphabet!'
            return game.to_form(msg)

        """The Guess is already used"""
        if guess in game.matches + game.misses:
            msg = 'Already used!'
            return game.to_form(msg)

        """The Guess is in the taget word"""
        if guess in list(game.target):
            game.matches.append(guess)
            msg = "Wonderful!"
            # Set the Guess is in the output words list"""
            i = 0
            for x in list(game.target):
                if x == guess:
                    game.output_words[i] = x
                i += 1
            if '_' not in game.output_words:
                game.end_game(True)
                return game.to_form(msg + ' You win!')
        else:
        	# The Guess is not in the taget word"""
        	game.misses.append(guess)
        	msg = "You missed!"
        	if len(game.misses) >= 6:
        		game.end_game(False)
        		return game.to_form(msg + ' Game over!')

        game.put()
        History.push(game.key, guess, msg)
        return game.to_form(msg)


    @endpoints.method(request_message=SCORE_REQUEST,
                      response_message=GameForms,
                      path='scores',
                      name='get_high_scores',
                      http_method='GET')
    def get_high_scores(self, request):
        """Return all scores order by score descending"""
        qry = Game.query(Game.game_over == True).order(-Game.score)
        if request.number_of_results:
            number_of_results = int(request.number_of_results)
            return GameForms(items=[game.to_form("") for game in qry.fetch(number_of_results)])
        else:
            return GameForms(items=[game.to_form("") for game in qry])

    @endpoints.method(request_message=SCORE_REQUEST,
                      response_message=ScoreForms,
                      path='scores/rankings',
                      name='get_user_rankings',
                      http_method='GET')
    def get_user_rankings(self, request):
        """Return user ranking"""
        qry = Score.query().order(-Score.win_ratio, -Score.number_of_wins, -Score.score)
        if request.number_of_results:
            number_of_results = int(request.number_of_results)
            return ScoreForms(items=[score.to_form() for score in qry.fetch(number_of_results)])
        else:
            return ScoreForms(items=[score.to_form() for score in qry])

    @endpoints.method(request_message=USER_REQUEST,
                      response_message=ScoreForms,
                      path='scores/user/{user_name}',
                      name='get_user_scores',
                      http_method='GET')
    def get_user_scores(self, request):
        """Returns all of an individual User's scores"""
        user = User.query(User.name == request.user_name).get()
        if not user:
            raise endpoints.NotFoundException(
                    'A User with that name does not exist!')
        scores = Score.query(Score.user == user.key)
        return ScoreForms(items=[score.to_form() for score in scores])

    @endpoints.method(request_message=GET_GAME_REQUEST,
                      response_message=HistoryForms,
                      path='history/{urlsafe_game_key}',
                      name='get_game_history',
                      http_method='GET')
    def get_game_history(self, request):
        """Returns all of the game history"""
        game = get_by_urlsafe(request.urlsafe_game_key, Game)
        if not game:
            raise endpoints.NotFoundException(
                    'A Game with that game key does not exist!')
        qry = History.query(History.game == game.key)
        return HistoryForms(items=[history.to_form() for history in qry])

api = endpoints.api_server([HangManApi])
