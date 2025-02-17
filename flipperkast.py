import pymunk
import paho.mqtt.client as mqtt

class Flipperkast:
    def __init__(self, broker="3cf02da39de440298d7f92ca74c6890c.s1.eu.hivemq.cloud", port=8883, username="JOUW_GEBRUIKERSNAAM", password="JOUW_WACHTWOORD", use_mqtt=True):
        self.space = pymunk.Space()
        self.space.gravity = (0.0, -900.0)

        self.bal = self.create_ball()
        self.bumper = self.create_bumper()

        self.score = 0
        self.highscore = 0

        # Collision handler fix
        self.space.add_collision_handler(1, 2).post_solve = self.on_collision

        if use_mqtt:
            self.client = mqtt.Client()
            self.client.username_pw_set(username, password)
            self.client.tls_set()
            self.client.connect(broker, port, 60)
        else:
            self.client = None

    def create_ball(self):
        body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 10))
        body.position = (100, 400)
        shape = pymunk.Circle(body, 10)
        shape.elasticity = 0.8
        shape.collision_type = 1  # Zorg dat de bal collision type 1 heeft
        self.space.add(body, shape)
        return body

    def create_bumper(self):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = (200, 200)
        shape = pymunk.Circle(body, 20)
        shape.elasticity = 1.2
        shape.collision_type = 2  # Bumper collision type 2
        self.space.add(body, shape)
        return shape

    def on_collision(self, arbiter, space, data):
        """Wordt aangeroepen bij botsing tussen bal en bumper."""
        self.add_score(50)

    def add_score(self, points):
        self.score += points
        if self.score > self.highscore:
            self.highscore = self.score

        if self.client:
            message = f'{{"score": {self.score}, "highscore": {self.highscore}}}'
            self.client.publish("flipperkast/score_update", message)

    def launch_ball(self, force=500):
        self.bal.apply_impulse_at_local_point((0, force))
        if self.client:
            self.client.publish("flipperkast/launch", f'{{"speed": {force}}}')
