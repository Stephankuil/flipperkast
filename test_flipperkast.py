import pytest
import pymunk
from flipperkast import Flipperkast


@pytest.fixture
def game():
    """Flipperkast instantie zonder MQTT (voor tests)."""
    return Flipperkast(use_mqtt=False)

def test_ball_launch(game):
    assert hasattr(game, 'bal'), "Flipperkast moet een bal-object hebben"
    initial_y = game.bal.position.y
    game.launch_ball(500)
    game.space.step(1/60)
    assert game.bal.position.y > initial_y

def test_bumper_collision(game):
    """Test of een botsing met een bumper punten oplevert."""
    assert hasattr(game, 'bumper'), "Flipperkast moet een bumper hebben"
    initial_score = game.score
    game.on_collision(None, None, None)  # Directe aanroep van de collision handler
    assert game.score == initial_score + 50  # 50 punten voor bumper hit


def test_mqtt_publish(monkeypatch):
    """Test of MQTT een bericht stuurt (zonder mocker)."""
    game = Flipperkast(use_mqtt=True)  # Zorg dat er een echte MQTT-client is

    def mock_publish(topic, message):
        """Mockfunctie om publish calls te vangen."""
        assert topic == "flipperkast/score_update"
        assert message == '{"score": 50, "highscore": 50}'

    monkeypatch.setattr(game.client, "publish", mock_publish)  # Mock de methode
    game.add_score(50)  # Dit roept mock_publish aan
