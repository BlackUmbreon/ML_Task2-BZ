# This Code is Heavily Inspired By The YouTuber: Cheesy AI
# Code Changed, Optimized And Commented By: NeuralNine (Florian Dedov)
# This code has again been hoisted by the CGS Digital Innovation Department
# giving credit to the above authors for the benfit of our education in ML

import math
import random
import sys
import os

import neat
import pygame

# Constants
WIDTH = 1000
HEIGHT = 580

WIDTH = 1920
HEIGHT = 1080


CAR_SIZE_X = 60
CAR_SIZE_Y = 60

BORDER_COLOR = (255, 255, 255, 255)  # Color To Crash on Hit

current_generation = 0  # Generation counter
"""
The Car Class is used by every individual car to run functions and store variables regarding its speed rotation position etc.
It contains every function apart from the run_simulation function as that is the only function that runs without the need of a car to target
This class is used by the run_simulation function in order to easily allow calculations and functions to be performed differently for each car without the need of having to loop through lists and check statements for each car
It also displays each car and its radars.

The things this functions does not do includes containing data on the cars neural network as this is handled separately
It also does not include variables or functions that involve multiple car's data.



Throughout this section, you will need to explore each function
and provide extenive comments in the spaces denoted by the 
triple quotes(block quotes) """ """.
Your comments should describe each function and what it is doing, 
why it is necessary and where it is being used in the rest of the program.

"""


class Car:
    """1. This Function creates the base model and sprite for the cars as well as defining different variables for the specified car
            The function defines key variables are unique to each indivual car and the variables are used all throughout the code.
            Every variable is clearly defined below with no further explanation needed
    """

    def __init__(self):
        # Load Car Sprite and Rotate
        self.sprite = pygame.image.load("car.png").convert()  # Convert Speeds Up A Lot
        self.sprite = pygame.transform.scale(self.sprite, (CAR_SIZE_X, CAR_SIZE_Y))
        self.rotated_sprite = self.sprite

        # self.position = [690, 740] # Starting Position
        self.position = [830, 920]  # Starting Position
        self.angle = 0 #Angle of car
        self.speed = 0 #Speed of car

        self.speed_set = False  # Flag For Default Speed Later on

        self.center = [
            self.position[0] + CAR_SIZE_X / 2,
            self.position[1] + CAR_SIZE_Y / 2,
        ]  # Calculate Center

        self.radars = []  # List For Sensors / Radars
        self.drawing_radars = []  # Radars To Be Drawn

        self.alive = True  # Boolean To Check If Car is Crashed

        self.distance = 0  # Distance Driven
        self.time = 0  # Time Passed

    """ 2. This Function draws the sprite and radars for the specific car that is called using pygame functions
            - The inputs are the car's variables (self) as well as screen
            - It first draws sprites using the blit function
            - It then calls the draw_radar function (defined below) to draw the radars
        It is only used by the run_simulation function
    """

    def draw(self, screen):
        screen.blit(self.rotated_sprite, self.position)  # Draw Sprite
        self.draw_radar(screen)  # OPTIONAL FOR SENSORS

    """ 3. This Function draws the radars on screen for the specific called car
            - It begins by looping through for every radar
            - It draws the radars by aligning with the centre of the car then extending outwards to draw the circle
            - It repeats this process for every radar
        It is only used by the function above
    """

    def draw_radar(self, screen):
        # Optionally Draw All Sensors / Radars
        for radar in self.radars:
            position = radar[0]
            pygame.draw.line(screen, (0, 255, 0), self.center, position, 1)
            pygame.draw.circle(screen, (0, 255, 0), position, 5)

    """ 4. This Function Checks to see if there has been a collision and changing the variable self.alive to be an output rather than returning a value.
            - It begins by setting the car to be alive by default
            - It proceeds to check if the pixel on the map png with the car's x and y coordinates in black and setting self.alive to false (This basically kills the car)
        Whilst this function is only called once per tick (In the update function) the variables it updates are used multiple times
    """

    def check_collision(self, game_map):
        self.alive = True
        for point in self.corners:
            # If Any Corner Touches Border Color -> Crash
            # Assumes Rectangle
            if game_map.get_at((int(point[0]), int(point[1]))) == BORDER_COLOR:
                self.alive = False
                break

    """ 5. This Function is the radar function and it finds how long a radar is due to whether or not its hit a wall
            It handles the bulk of the calculations and nessasary processes for the radars
            - It begins by defining 3 variables
                - Length: how long the radar is
                - X: the current x coorindate for the end of the radar
                - Y: the current y coordinate for the end of the radar
                Both X and Y are calculated through trignometric functions using the radar degree and the length of the radar (+angle of car)
            - Afterwards it begins a loop
                - The loops increases the length of the radar each time and checking if the additional length makes it hit a wall
                - Once the radar does hit a wall it breaks from the loop
            - Finally it updates self.radars

         Whilst this function is only called once per tick (In the update function) the variables it updates are used multiple times
    """

    def check_radar(self, degree, game_map):
        length = 0
        x = int(
            self.center[0]
            + math.cos(math.radians(360 - (self.angle + degree))) * length
        )
        y = int(
            self.center[1]
            + math.sin(math.radians(360 - (self.angle + degree))) * length
        )

        # While We Don't Hit BORDER_COLOR AND length < 300 (just a max) -> go further and further
        while not game_map.get_at((x, y)) == BORDER_COLOR and length < 300:
            length = length + 1
            x = int(
                self.center[0]
                + math.cos(math.radians(360 - (self.angle + degree))) * length
            )
            y = int(
                self.center[1]
                + math.sin(math.radians(360 - (self.angle + degree))) * length
            )

        # Calculate Distance To Border And Append To Radars List
        dist = int(
            math.sqrt(math.pow(x - self.center[0], 2) + math.pow(y - self.center[1], 2))
        )
        self.radars.append([(x, y), dist])

    """ 6. This Function updates all variables by running the different calculations required for each tick of the game to run
            It is basically the functions that runs the entire simulation with each iteration of this equating to a single tick of simulation time
            - It begins by updating it's angle and speed
            - It uses these updates values to update its position and distance traveled
            - It updates simulation time by 1
            - It now calculates updated variables for the car (centre + position of corners of car)
            - Finally it checks if the car has collided with something
    """

    def update(self, game_map):
        # Set The Speed To 20 For The First Time
        # Only When Having 4 Output Nodes With Speed Up and Down
        if not self.speed_set:
            self.speed = 20
            self.speed_set = True

        # Get Rotated Sprite And Move Into The Right X-Direction
        # Don't Let The Car Go Closer Than 20px To The Edge
        self.rotated_sprite = self.rotate_center(self.sprite, self.angle)
        self.position[0] += math.cos(math.radians(360 - self.angle)) * self.speed
        self.position[0] = max(self.position[0], 20)
        self.position[0] = min(self.position[0], WIDTH - 120)

        # Increase Distance and Time
        self.distance += self.speed
        self.time += 1

        # Same For Y-Position
        self.position[1] += math.sin(math.radians(360 - self.angle)) * self.speed
        self.position[1] = max(self.position[1], 20)
        self.position[1] = min(self.position[1], WIDTH - 120)

        # Calculate New Center
        self.center = [
            int(self.position[0]) + CAR_SIZE_X / 2,
            int(self.position[1]) + CAR_SIZE_Y / 2,
        ]

        # Calculate Four Corners
        # Length Is Half The Side
        length = 0.5 * CAR_SIZE_X
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
        self.corners = [left_top, right_top, left_bottom, right_bottom]

        # Check Collisions And Clear Radars
        self.check_collision(game_map)
        self.radars.clear()

        # From -90 To 120 With Step-Size 45 Check Radar
        for d in range(-90, 120, 45):
            self.check_radar(d, game_map)

    """ 7. This Function is used to get values of the data from the nodes of the car. The values from each node is equivlant to the distance the node is from the wall
            This data is then used within an individuals neural network to calculate its next action
            - It recieves data on the car (self)
            - It then creates a list (return_values) that will contain the 5 values from the different nodes
            - It iterates over a loop, each time finding the value for a node and adding it into return_values
            - Once it has completed this process it returns the values
    """

    def get_data(self):
        # Get Distances To Border
        radars = self.radars
        return_values = [0, 0, 0, 0, 0]
        for i, radar in enumerate(radars):
            return_values[i] = int(radar[1] / 30)

        return return_values

    """ 8. This Function checks the state of the car whether it's supposed to be dead or alive. It is used to check if a program should do a specific action
            - It simply returns the self.alive variable
    
    """

    def is_alive(self):
        # Basic Alive Function
        return self.alive

    """ 9. This is the reward function that calculates the reward (How well a specific individual has done). This reward is then used to determine which individuals will die or reproduce
            -It recieves data on the specific car (self)
            -Afterwards it calculates the rewards primarily through the self.distance variable
            -It returns this value back
    """

    def get_reward(self):
        # Calculate Reward (Maybe Change?)
        # return self.distance / 50.0
        return self.distance / (CAR_SIZE_X / 2)

    """ 10. This Function rotates the car image so that it if facing the correct way when drawn
            -It begins by recieving the car sprite (image) and what angle it should be facing
            -It then rotates the car around its centre point
            -It finally returns the rotated image
    """

    def rotate_center(self, image, angle):
        # Rotate The Rectangle
        rectangle = image.get_rect()
        rotated_image = pygame.transform.rotate(image, angle)
        rotated_rectangle = rectangle.copy()
        rotated_rectangle.center = rotated_image.get_rect().center
        rotated_image = rotated_image.subsurface(rotated_rectangle).copy()
        return rotated_image


""" This Function runs the entire simulation with it calling different functions and updating specific variables to do so
- It begins with defining a list of each car (car) and it's neural network (net)
- It then displays the simulation by initialises Pygame
- Afterwards it creates a neural network by for each car by using neat and data from the config file each loop
- More variables defined which all are used to display information onto the simulation
- the global variable (current_generation) is defined to keep track of how many generations have happened
- The main loop of the simulation is run after all the setting up. Within this loop contains:
    - A quit event to exit the simulation
    - A loop that iterates through each car and updating its speed / rotation based on its neural network's output
    - A loop that iterates through each car and checks how many are still alive as well as updating the simulation and the car's fitness score
    - 2 checks that both stop the current generation if either no cars are still alive or if the maximum time limit has been reached
    - A section that draws the map and all alive cars onto the simulation
    - The final main section of this loop displays all other information such as current generation and amount of cars still alive
    - Finally it limits the simulation to run at 60fps
"""


def run_simulation(genomes, config):
    # Empty Collections For Nets and Cars
    nets = []
    cars = []

    # Initialize PyGame And The Display
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    # For All Genomes Passed Create A New Neural Network
    for i, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        g.fitness = 0

        cars.append(Car())

    # Clock Settings
    # Font Settings & Loading Map
    clock = pygame.time.Clock()
    generation_font = pygame.font.SysFont("Arial", 30)
    alive_font = pygame.font.SysFont("Arial", 20)
    game_map = pygame.image.load("map3.png").convert()  # Convert Speeds Up A Lot

    global current_generation
    current_generation += 1

    # Simple Counter To Roughly Limit Time (Not Good Practice)
    counter = 0

    while True:
        # Exit On Quit Event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)

        # For Each Car Get The Acton It Takes
        for i, car in enumerate(cars):
            output = nets[i].activate(car.get_data())
            choice = output.index(max(output))
            if choice == 0:
                car.angle += 10  # Left  
            elif choice == 1:
                car.angle -= 10  # Right
            elif choice == 2:
                if car.speed - 2 >= 12:
                    car.speed -= 2  # Slow Down
            else:
                car.speed += 2  # Speed Up

        # Check If Car Is Still Alive
        # Increase Fitness If Yes And Break Loop If Not
        still_alive = 0
        for i, car in enumerate(cars):
            if car.is_alive():
                still_alive += 1
                car.update(game_map)
                genomes[i][1].fitness += car.get_reward()

        if still_alive == 0:
            break

        counter += 1
        if counter == 30*40:  # Stop After About 20 Seconds
            break

        # Draw Map And All Cars That Are Alive
        screen.blit(game_map, (0, 0))
        for car in cars:
            if car.is_alive():
                car.draw(screen)

        # Display Info
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


""" 1. This Section contains 2 sections. 
            The first loads the information from the config file into python.
            The config file as the name suggests contains data on how the simulation should be run and what values different constants are
                DefaultGenome: This contains data on how the nodes within a neural network should be run
                DefaultReproduction: Contains data on how each population kills of individuals or replicating genes
                DefaultSpeciesSet: Defines how different species should be defined
                DefaultStagnation: Defines a variety of variables on how genes should be selected to be passed on
            The second section creates and runs the population
                It begins by defining different stats for the population needed to run the simulation
                Then the final line of code runs the entire simulation for up to 1000 generations
"""
abcdef = 0
while abcdef < 3:
    if __name__ == "__main__":
        # Load Config
        config_path = "./config.txt"
        config = neat.config.Config(
            neat.DefaultGenome,
            neat.DefaultReproduction,
            neat.DefaultSpeciesSet,
            neat.DefaultStagnation,
            config_path,
        )

        # Create Population And Add Reporters
        population = neat.Population(config)
        population.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        population.add_reporter(stats)

        # Run Simulation For A Maximum of 1000 Generations
        population.run(run_simulation, 16)
        abcdef += 1
