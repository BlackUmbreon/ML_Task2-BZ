# This Code is Heavily Inspired By The YouTuber: Cheesy AI
# Code Changed, Optimized And Commented By: NeuralNine (Florian Dedov)
# This code has again been hoisted by the CGS Digital Innovation Department
# giving credit to the above authors for the benefit of our education in ML

# Import necessary libraries
import math
import random
import sys
import os
import neat
import pygame

# Constants
WIDTH = 1800  # Width of the game window
HEIGHT = 1080  # Height of the game window

CAR_SIZE_X = 60  # Width of the car sprite
CAR_SIZE_Y = 60  # Height of the car sprite

BORDER_COLOR = (255, 255, 255, 255)  # Color that indicates a collision with a border

current_generation = 0  # Generation counter

# Define the Car class
class Car:
    def __init__(self):
        # Load and initialize the car sprite
        self.sprite = pygame.image.load("car.png").convert()  # Load the car sprite
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))  # Resize the sprite
        self.rotated_sprite = self.sprite  # Initialize the rotated sprite

        # Initial car position, angle, and speed
        self.position = [830, 920]  # Starting Position
        self.angle = 0  # Initial angle
        self.speed = 0  # Initial speed

        self.speed_set = False  # Flag to set the speed only once

        # Calculate the center of the car
        self.center = [self.position[0] + CAR_SIZE_X / 2, self.position[1] + CAR_SIZE_Y / 2]

        self.radars = [[(1,1),1]]  # List to store sensor positions and distances
        self.drawing_radars = []  # Radars to be drawn

        self.alive = True  # Boolean to check if the car is crashed

        self.distance = 0  # Distance driven
        self.time = 0  # Time passed

    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.position)  # Draw the car sprite
        self.draw_radar(screen)  # Optional: Draw sensors/radars

    def draw_radar(self, screen):
        # Optionally draw all sensors/radars
        for radar in self.radars:
            position = radar[0]
            pygame.draw.line(screen, (0, 255, 0), self.center, position, 1)  # Draw radar lines
            pygame.draw.circle(screen, (0, 255, 0), position, 5)  # Draw radar points

    def check_collision(self, game_map):
        self.alive = True
        for point in self.corners:
            # If any corner touches the border color, it's considered a collision
            if game_map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOR:
                self.alive = False
                break

    def check_radar(self, degree, game_map):
        length = 0
        x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
        y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        # While we don't hit BORDER_COLOR and length < 300 (just a max), continue going further and further
        while not game_map.get_at((x, y)) == BORDER_COLOR and length < 300:
            length = length + 1
            x = int(self.center[0] + math.cos(math.radians(360 - (self.angle + degree))) * length)
            y = int(self.center[1] + math.sin(math.radians(360 - (self.angle + degree))) * length)

        # Calculate the distance to the border and append it to the radars list
        dist = int(math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2)))
        self.radars.append([(x, y), dist])

    def update(self, game_map):
        # Set the speed to 20 for the first time, only when having 4 output s with speed up and down
        if not self.speed_set:
            self.speed = 2
            self.speed_set = True

        # Get rotated sprite and move into the right X-Direction
        # Ensure the car doesn't go closer than 20px to the edge
        self.rotated_sprite = self.rotate_center(self.sprite, self.angle)
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.position[0] = max(self.position[0], 20)
        self.position[0] = min(self.position[0], WIDTH - 120)

        # Increase distance and time
        self.distance += self.speed
        self.time += 1

        # Update Y-Position in the same way as X-Position
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], 20)
        self.position[1] = min(self.position[1], WIDTH - 120)

        # Calculate new center and corners of the car
        self.center = [int(self.position[0]) + CAR_SIZE_X / 2, int(self.position[1]) + CAR_SIZE_Y / 2]

        length = 0.5 * CAR_SIZE_X  # Length is half the side of the car
        left_top = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 30))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 30))) * length,
        ]
        right_top = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 150))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 150))) * length,
        ]
        left_bottom = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 210))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 210))) * length,
        ]
        right_bottom = [
            self.center[0] + math.cos(math.radians(360 - (self.angle + 330))) * length,
            self.center[1] + math.sin(math.radians(360 - (self.angle + 330))) * length,
        ]
        self.corners = [left_top, right_top, left_bottom, right_bottom]  # Store the corners of the car

        # Check for collisions and clear the radars
        self.check_collision(game_map)
        self.radars.clear()

        # From -90 to 120 with step-size 60,
        # Check radar at various angles
        for d in range(-90, 120, 60):
            self.check_radar(d, game_map)

    def get_data(self):
        # Get distances to borders from the radar readings
        radars = self.radars
        return_values = [0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1] / 30)

        return return_values

    def is_alive(self):
        # Basic alive function
        return self.alive

    def get_reward(self):
        # Calculate the reward based on the distance traveled
        return self.distance / (CAR_SIZE_X / 2)

    def rotate_center(self, image, angle):
        # Rotate the car sprite
        rectangle = image.get_rect()
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rectangle = rectangle.copy()
        rotated_rectangle.center = rotated_image.get_rect().center
        rotated_image = rotated_image.subsurface(rotated_rectangle).copy()
        return rotated_image


def run_simulation(genomes, config):
    # Empty collections for neural networks (nets) and cars
    nets = []
    cars = []

    # Initialize PyGame and the display
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    # For all genomes passed, create a new neural network and car
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        cars.append(Car())

    # Clock settings
    # Font settings & loading map
    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 30)
    alive_font = pygame.font.SysFont("Arial", 20)
    n = random.randint(2, 5)
    game_map = pygame.image.load("map" + str(2) + ".png").convert()  # Convert speeds up loading

    global current_generation
    current_generation += 1

    # Simple counter to roughly limit time (not good practice)
    counter = 0

    while True:
        # Exit on quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        # For each car, get the action it takes based on neural network output
        for i, car in enumerate(cars):
            output = nets[i].activate(car.get_data())
            choice = output.index(max(output))
            if choice == 0:
                car.angle += 10  # Turn left
            elif choice == 1:
                car.angle -= 10  # Turn right
            elif choice == 2:
                if car.speed - 2 >= 12:
                    car.speed -= 2  # Slow down
            else:
                car.speed += .2  # Speed up

        # Check if car is still alive, increase fitness if yes, and break loop if not
        still_alive = 0
        for i, car in enumerate(cars):
            if car.is_alive():
                still_alive += 1
                car.update(game_map)
                genomes[i][1].fitness += car.get_reward()

        if still_alive == 0:
            break

        counter += 1
        if counter == 30 * 40:  # Stop after about 20 seconds
            break

        # Draw map and all cars that are alive
        screen.blit(game_map, (0, 0))
        for car in cars:
            if car.is_alive():
                car.draw(screen)

        # Display info
        text = generation_font.render(
            "Generation: " + str(current_generation), True, (0, 0, 0)
        )
        text_rect = text.get_rect()
        text_rect.center = (900, 450)
        screen.blit(text, text_rect)

        text = alive_font.render("Still Alive: " + str(still_alive), True, (0, 0, 0))
        text_rect = text.get_rect()
        text_rect.center = (900, 490)
        screen.blit(text, text_rect)

        pygame.display.flip()
        clock.tick(60)  # 60 FPS


if __name__ == "__main__":
    # Load config
    config_path = "./config.txt"
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path,
    )

    # Create population and add reporters
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    # Run simulation for a maximum of 1000 generations
    population.run(run_simulation, 1000)
