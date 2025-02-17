print("hello world")

import pymunk
import paho.mqtt.client as mqtt

class Flipperkast:
    def __init__(self, broker="localhost", port=1883, topic="flipperkast"):
        self.space = pymunk.Space()
        self.space.gravity = (0.0, -900.0)
        self.bal = self.create_ball()
        self.bumper = self.create_bumper()

        #mqtt Setup
        self.client = mqtt.Client()
        self.client.on_connect(broker, port, 60)


        self.score = 0
        self.highscore = 0

        def create_ball(self):
            """Maakt een bal die door de zwaartekracht valt."""
            body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 10))
            body.position = (100, 400)
            shape = pymunk.Circle(body, 10)
            shape.elasticity = 0.8  # Bounciness
            self.space.add(body, shape)
            return body

        def create_bumper(self):
            """Maakt een bumper in het speelveld."""
            body = pymunk.Body(body_type=pymunk.Body.STATIC)
            body.position = (200, 200)
            shape = pymunk.Circle(body, 20)
            shape.elasticity = 1.2  # Extra bounce
            shape.collision_type = 1
            self.space.add(body, shape)
            return shape

        def update(self, dt=1 / 60):
            """Simuleert een stap van de physics-engine."""
            self.space.step(dt)
            self.check_collisions()

        def check_collisions(self):
            """Controleert of de bal een bumper raakt."""
            for arbiter in self.space.ongoing_contacts:
                if arbiter.shapes[1] == self.bumper:
                    self.add_score(50)

        def add_score(self, points):
            """Voegt punten toe en stuurt een MQTT-bericht."""
            self.score += points
            if self.score > self.highscore:
                self.highscore = self.score

            self.client.publish("flipperkast/score_update", f"{{'score': {self.score}, 'highscore': {self.highscore}}}")

        def launch_ball(self, force=500):
            """Lanceert de bal omhoog."""
            self.bal.apply_impulse_at_local_point((0, force))
            self.client.publish("flipperkast/launch", f"{{'speed': {force}}}")

