import pygame
import pymunk
import pymunk.pygame_util
import paho.mqtt.client as mqtt

# Pygame setup
WIDTH, HEIGHT = 600, 800
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

class Flipperkast:
    def __init__(self, broker="3cf02da39de440298d7f92ca74c6890c.s1.eu.hivemq.cloud", port=8883, username="JOUW_GEBRUIKERSNAAM", password="JOUW_WACHTWOORD", use_mqtt=True):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("2D Flipperkast")
        self.clock = pygame.time.Clock()

        # Physics setup
        self.space = pymunk.Space()
        self.space.gravity = (0.0, -900.0)

        self.bal = self.create_ball()
        self.bumper = self.create_bumper()
        self.left_flipper = self.create_flipper(x=150, is_left=True)
        self.right_flipper = self.create_flipper(x=450, is_left=False)

        # Collision handling
        self.space.add_collision_handler(1, 2).post_solve = self.on_collision

        self.score = 0
        self.highscore = 0

        # MQTT Setup
        if use_mqtt:
            self.client = mqtt.Client()
            self.client.username_pw_set(username, password)
            self.client.tls_set()
            self.client.connect(broker, port, 60)
        else:
            self.client = None

    def create_ball(self):
        body = pymunk.Body(1, pymunk.moment_for_circle(1, 0, 10))
        body.position = (300, 600)
        shape = pymunk.Circle(body, 10)
        shape.elasticity = 0.8
        shape.collision_type = 1
        self.space.add(body, shape)
        return body

    def create_bumper(self):
        body = pymunk.Body(body_type=pymunk.Body.STATIC)
        body.position = (300, 400)
        shape = pymunk.Circle(body, 30)
        shape.elasticity = 1.5
        shape.collision_type = 2
        self.space.add(body, shape)
        return shape

    def create_flipper(self, x, is_left=True):
        """Maakt een flipper en zet deze vast met een scharnier (pivot joint)."""
        mass = 10
        size = (80, 20)
        moment = pymunk.moment_for_box(mass, size)

        body = pymunk.Body(mass, moment)
        body.position = (x, 100)  # Onderkant van de flipperkast
        shape = pymunk.Poly.create_box(body, size)
        shape.elasticity = 0.5

        # Maak een scharnier (pivot joint) zodat de flippers op hun plek blijven
        pivot = pymunk.PinJoint(self.space.static_body, body, (x, 100), (0, 0))

        # Beperk de rotatie met een Limit Joint (zodat ze niet rondvliegen)
        limit = pymunk.RotaryLimitJoint(
            self.space.static_body, body, -0.5 if is_left else 0.5, 0.5 if is_left else -0.5
        )

        self.space.add(body, shape, pivot, limit)
        return body

    def on_collision(self, arbiter, space, data):
        self.add_score(50)

    def add_score(self, points):
        self.score += points
        if self.score > self.highscore:
            self.highscore = self.score

        if self.client:
            message = f'{{"score": {self.score}, "highscore": {self.highscore}}}'
            self.client.publish("flipperkast/score_update", message)

    def launch_ball(self):
        self.bal.apply_impulse_at_local_point((0, 300))

    def move_flippers(self, left=False, right=False):
        """Beweegt de flippers omhoog door een impuls toe te voegen."""
        impulse = 30000  # Sterkte van de klap
        if left:
            self.left_flipper.apply_impulse_at_local_point((0, impulse))
        if right:
            self.right_flipper.apply_impulse_at_local_point((0, -impulse))

    def draw(self):
        self.screen.fill(WHITE)
        pygame.draw.circle(self.screen, BLUE, (int(self.bal.position.x), HEIGHT - int(self.bal.position.y)), 10)
        pygame.draw.circle(self.screen, RED, (int(self.bumper.body.position.x), HEIGHT - int(self.bumper.body.position.y)), 30)
        pygame.draw.rect(self.screen, BLUE, pygame.Rect(self.left_flipper.position.x - 40, HEIGHT - self.left_flipper.position.y - 10, 80, 20))
        pygame.draw.rect(self.screen, BLUE, pygame.Rect(self.right_flipper.position.x - 40, HEIGHT - self.right_flipper.position.y - 10, 80, 20))
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            self.space.step(1/60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.launch_ball()
                    elif event.key == pygame.K_LEFT:
                        self.move_flippers(left=True)
                    elif event.key == pygame.K_RIGHT:
                        self.move_flippers(right=True)

            self.draw()
            self.clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    game = Flipperkast()
    game.run()
