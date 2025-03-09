import sys

import pygame
import os
import random
import math
import neat

# HARTH MAJEED
# 3547 Intelligent Agents & Reinforcement Learning
# TERM PROJECT

#init pygame
pygame.init()
pygame.font.init()

#load images
background = pygame.image.load('mars.png')
landingPad = pygame.image.load('landingPad.png')
rocket = pygame.image.load('rocket.png')
rocket_thrust = pygame.image.load('rocket_thrust.png')
rocket_right = pygame.image.load('rocket_right.png')
rocket_left = pygame.image.load('rocket_left.png')

#icon
icon = pygame.image.load('icon.png')
pygame.display.set_icon(icon)

#create screen
screen = pygame.display.set_mode((background.get_width(), background.get_height()))
pygame.display.set_caption("Rocket Booster Agent")

#set landingPad
landingPadX = (background.get_width()/2)-(landingPad.get_width()/2)
landingPadY = background.get_height()-landingPad.get_height()

#variables
global acc_rate
acc_rate = 0.02
fuel_rate = 0.1  # Adjusted fuel consumption rate
y_speed_rate = 1

#class game object
class Rocket:
    #variables needed in class
    thrustBool = False
    leftThrustBool = False
    rightThrustBool = False
    idleThrustBool = False

    def __init__(self):
        self.image = pygame.image.load('rocket.png')
        self.x = random.randint(100, screen.get_width()-100)
        self.y = random.randint(20, 100)
        self.x_speed = 0
        self.y_speed = y_speed_rate
        self.x_acc = 0
        self.y_acc = acc_rate
        self.fuel = 100  # Increased initial fuel
        self.color = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
        self.rect = pygame.Rect(self.x, self.y, self.image.get_width(), self.image.get_height())

    #move the agent rocket
    def move(self):
        self.x_speed += self.x_acc
        self.y_speed += self.y_acc
        self.x += self.x_speed
        self.y += self.y_speed

    #display the agent rocket
    def display(self):
        self.rect = self.image.get_rect()
        self.rect.move_ip(int(self.x), int(self.y))
        screen.blit(self.image, (int(self.x), int(self.y)))
        fuel_text = pygame.font.SysFont('Segoe UI', 16).render(str(int(self.fuel)), False, (0,0,0))
        screen.blit(fuel_text, (int(self.x)+22, int(self.y)+5))
        pygame.draw.rect(screen, self.color, (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 2)
        #pygame.display.update() #this works too

    #set the image of current control
    def set_image(self, image):
        self.image = image

    #reset the values for the rocket
    def reset(self):
        self.x = random.randint(100, screen.get_width()-100)
        self.y = random.randint(20, 100)
        self.x_speed = 0
        self.y_speed = y_speed_rate
        self.fuel = 100
        self.x_acc = 0
        self.y_acc = acc_rate

    #calculates the score
    def score(self):
        score = 0
        score += self.fuel * 20
        x_diff = abs((self.x + (self.image.get_width()/2)) - (landingPadX + (landingPad.get_width()/2)))
        y_diff = (self.y + self.image.get_height()) - landingPadY
        distance = math.sqrt(pow(x_diff,2) + pow(y_diff,2))
        score -= distance * 5  # Reduced penalty for distance
        #print(x_diff, y_diff, distance, score, self.x_speed, self.y_speed)
        # Penalize for high speeds when landing
        if didAgentLand(self) and self.y_speed > 2.0:
            score -= 2000
        # Reward for successful landing
        if didAgentLand(self) and self.y_speed <= 2.0:
            score += 1000
        return int(score)

    #controls of the agent rocket
    def control(self):
        if self.leftThrustBool and self.fuel > 0:
            self.set_image(rocket_left)
            self.x_acc = -acc_rate
        elif self.rightThrustBool and self.fuel > 0:
            self.set_image(rocket_right)
            self.x_acc = acc_rate
        elif self.thrustBool and self.fuel > 0:
            self.set_image(rocket_thrust)
            self.y_acc = -acc_rate
        else:
            self.set_image(rocket)
            self.x_acc = 0
            self.y_acc = acc_rate
        self.thrustBool = False
        self.leftThrustBool = False
        self.rightThrustBool = False
        self.idleThrustBool = False


#functions
def display(image, x, y):
    screen.blit(image, (x, y))

def stopAgent(agent):
    global acc_rate
    agent.x_speed = 0
    agent.y_speed = 0
    acc_rate = 0

def didAgentLand(agent):
    isInsideLandingPad = False
    distanceToLandingPad = landingPadY - agent.y - agent.image.get_height()
    if agent.x >= landingPadX and agent.x <= (landingPadX + landingPad.get_width() - agent.image.get_width()):
        isInsideLandingPad = True
    if distanceToLandingPad <= 0 and isInsideLandingPad:
        return True
    else:
        return False

def didAgentCrash(agent):
    if not didAgentLand(agent) and (agent.y + agent.image.get_height() > landingPadY):
        return True
    else:
        return False

def keepAgentInBounds(agent):
    if agent.x <= 0:
        agent.x = 0
        agent.x_speed = 0
    elif agent.x >= screen.get_width() - agent.image.get_width():
        agent.x = screen.get_width() - agent.image.get_width()
        agent.x_speed = 0
    if agent.y <= 0:
        agent.y = 0
        agent.y_speed = y_speed_rate
    elif agent.y >= screen.get_height() - agent.image.get_height():
        agent.y = screen.get_height() - agent.image.get_height()
        agent.y_speed = -y_speed_rate

#pop a rocket
def remove(index):
    rockets.pop(index)
    ge.pop(index)
    nets.pop(index)

#calc fuel consumption
def adjustFuel(agent):
    if agent.y_acc != acc_rate or agent.x_acc != 0:
        agent.fuel -= fuel_rate
        if agent.fuel <= 0:
            agent.y_acc = acc_rate
            agent.x_acc = 0

#agent step - function that controlls all functions that need to be called per step
def step(agent):
    agent.move()
    adjustFuel(agent)
    keepAgentInBounds(agent)
    agent.control()


#evolution function
def eval_genomes(genomes, config):
    #global variables
    FONT = pygame.font.SysFont('Segoe UI', 16)
    global main_loop
    global acc_rate
    global agent_x_acc
    global agent_y_acc
    global fuel_rate
    global rockets
    global ge
    global nets
    global landingPadCenterX
    global landingPadcenterY

    clock = pygame.time.Clock()

    landingPadCenterX = landingPadX + (landingPad.get_width())
    landingPadCenterY = landingPadY

    rockets = []
    ge = []
    nets = []

    for genome_id, genome in genomes:
        rockets.append(Rocket())
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

    #display stats
    def statistics():
        global dinosaurs, game_speed, ge
        agentsCount = FONT.render(f'Agents Alive:  {str(len(rockets))}', True, (0, 0, 0))
        gen = FONT.render(f'Generation:  {pop.generation+1}', True, (0, 0, 0))
        screen.blit(agentsCount, (50, 50))
        screen.blit(gen, (50, 100))

    main_loop = True
    #main loop
    while main_loop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                main_loop = False
                sys.exit()

        if len(rockets) == 0:
            main_loop = False
            break

        #check if a rocket crashed or landed
        for index, agent in enumerate(rockets):
            if didAgentCrash(agent):
                ge[index].fitness = agent.score() - 20000
                remove(index)
            if didAgentLand(agent) and agent.y_speed <= 2.0:
                ge[index].fitness = agent.score() + 1000
                remove(index) #consider deleting
            elif didAgentLand(agent) and agent.y_speed > 2.0:
                ge[index].fitness = agent.score() - 2000
                remove(index) #consider deleting

        #call/activate the neural net
        for index, agent in enumerate(rockets):
            x_diff = abs((agent.x + (agent.image.get_width() / 2)) - (landingPadX + (landingPad.get_width() / 2)))
            y_diff = (agent.y + agent.image.get_height()) - landingPadY
            distance = math.sqrt(pow(x_diff, 2) + pow(y_diff, 2))
            #calling the net
            output = nets[index].activate((agent.x, agent.y, distance,
                                           agent.x_speed, agent.y_speed,
                                           agent.x_acc, agent.y_acc, agent.fuel,
                                           landingPadCenterX, landingPadCenterY))
            if output[0] > 0.5:
                agent.thrustBool = True
            if output[1] > 0.5:
                agent.leftThrustBool = True
            if output[2] > 0.5:
                agent.rightThrustBool = True
            if output[3] > 0.5:  # Corrected index for idle thrust
                agent.idleThrustBool = True

        for agent in rockets:
            #call this to make the agent react, then display
            step(agent)
            #display agent
            agent.display()
            pygame.display.update()

        # display background and landing pad and call update
        #statistics()
        display(background, 0, 0)
        display(landingPad, landingPadX, landingPadY)
        clock.tick(60) #60 fps, did use 30 before but stuck with 60
        pygame.display.update()


# Setup the NEAT Neural Network
def run(config_path):
    global pop
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    pop = neat.Population(config)

    #for reporting the statistics on the generation
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    pop.run(eval_genomes, 50)

#handle main function
if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)

