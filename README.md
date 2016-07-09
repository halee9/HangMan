##Game Description:
Hangman is a simple guessing game. Each game begins with a random 'target'
word provided by system. 'Guess' are sent to the 'make_guess' endpoint which will reply
with either: 'match', 'miss', 'you win', or 'game over' (if 6 misses is reached).

##Game Scoring
Your score depends on how many word you've missed. You can get 100 points when you
win, but you can get additional 100 points if you never missed. Your ranking is based
on how many times you win and wins games ratio.

##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will
    raise a ConflictException if a User with that user_name already exists.

 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not.

 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.

 - **get_user_games**
    - Path: 'games/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: All GameForms of an User.
    - Description: Returns all of an individual User's games.

 - **cancel_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: DELETE
    - Parameters: urlsafe_game_key
    - Returns: Message confirming deletion of the Game.
    - Description: Cancel game if the game is not over.

 - **make_guess**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, guess
    - Returns: GameForm with current game state.
    - Description: Accepts a 'guess' and returns the updated state of the game.
    If this causes a game to end, a user's Score entity will be created or updated.

 - **get_high_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: number_of_results (optional)
    - Returns: GameForms order by score descending.
    - Description: Returns all Games in the database order by high score.

 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms.
    - Description: Returns all Scores recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.

 - **get_user_rankings**
    - Path: 'scores/rankings'
    - Method: GET
    - Parameters: number_of_results (optional)
    - Returns: ScoreForms.
    - Description: Returns user's Scores order by win_ratio, number_of_wins

 - **get_game_history**
    - Path: 'history/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: HistoryForms.
    - Description: Returns all Game History recorded by the provided Game.
    Will raise a NotFoundException if the Game does not exist.

##Models Included:
 - **User**
    - Stores unique user_name and email address.

 - **Game**
    - Stores unique game states. Associated with User model via KeyProperty.

 - **Score**
    - Records number of wins and losses and game scores. Associated with Users
    model via KeyProperty.

 - **History**
    - Records game history with guess and message. Associated with Games model
    via KeyProperty.

##Forms Included:
 - **GameForm**
    - Representation of a Game's state (url_safe_key, output_words, match_words,
    miss_words, game_over flag, score, win flag, message, user_name).
 - **GameForms**
    - Multiple GameForm container.
 - **ScoreForm**
    - Representation of a Users game Score (user_name, number of wins,
    number of losses, win ratio, score)
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **HistoryForm**
    - Representation of a game's History (urlsafe_game_key, guess, message)
 - **HistoryForms**
    - Multiple HistoryForm container.
 - **StringMessage**
    - General purpose String container.
