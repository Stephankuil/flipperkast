import pytest
import pymunk
from flipperkast import Flipperkast

@pytest.fixture
def game():
    return Flipperkast()

def test_ball_launch(game):
    """Test of de bal een opwaartse kracht krijgt bij lancering."""
    initial_y = game.bal.position.y
    game.launch_ball(500)
    game.space.step(1/60)  # Simuleer een frame
    assert game.bal.position.y > initial_y  # Bal moet omhoog bewegen

def test_bumper_collision(game):
    """Test of een botsing met een bumper punten oplevert."""
    initial_score = game.score
    game.bal.position = game.bumper.body.position  # Simuleer botsing
    game.check_collisions()
    assert game.score == initial_score + 50  # 50 punten voor bumper hit

def test_mqtt_publish(mocker, game):
    """Test of MQTT een bericht stuurt bij score-update."""
    mock_publish = mocker.patch.object(game.client, "publish")
    game.add_score(50)
    mock_publish.assert_called_with("flipperkast/score_update", "{'score': 50, 'highscore': 50}")

