import pygame
import os
import random
import math

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
main_loop = True
end_loop = False
global acc_rate
acc_rate = 0.00015
fuel_rate = 0.01

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
        self.y_speed = 0.01
        self.x_acc = 0
        self.y_acc = acc_rate
        self.fuel = 100
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

    #set the image of current control
    def set_image(self, image):
        self.image = image

    #reset the values for the rocket
    def reset(self):
        self.x = random.randint(100, screen.get_width()-100)
        self.y = random.randint(20, 100)
        self.x_speed = 0
        self.y_speed = 0.01
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
        score -= distance * 10
        print(x_diff, y_diff, distance)
        return int(score)

    #controls of the agent rocket
    def control(self):
        if self.leftThrustBool and self.fuel > 0:
            self.set_image(rocket_left)
            self.x_acc = -acc_rate
        if self.rightThrustBool and self.fuel > 0:
            self.set_image(rocket_right)
            self.x_acc = acc_rate
        if self.thrustBool and self.fuel > 0:
            self.set_image(rocket_thrust)
            self.y_acc = -acc_rate
        if self.idleThrustBool:
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
    if (agent.x < landingPadX or agent.x > (landingPadX + landingPad.get_width())):
        if agent.y + agent.image.get_height() > landingPadY:
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
        agent.y_speed = 0.01
    elif agent.y >= screen.get_height() - agent.image.get_height():
        agent.y = screen.get_height() - agent.image.get_height()
        agent.y_speed = -0.01

#pop a rocket
def remove(index):
    agents.pop(index)

#calc fuel consumption
def adjustFuel(agent):
    if agent.y_acc != acc_rate or agent.x_acc != 0:
        agent.fuel -= fuel_rate
        if agent.fuel <= 0:
            agent.y_acc = acc_rate
            agent.x_acc = 0

#agent step - function that controlls all functions that need to be called per step
def step(agent):
    agent.control()
    adjustFuel(agent)
    keepAgentInBounds(agent)
    agent.move()


def main():
    #global variables
    global main_loop
    global end_loop
    global acc_rate
    global fuel_rate
    global agents

    agents = [Rocket()]

    #creating rocket
    agent = Rocket()

    #main loop -
    while main_loop:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                main_loop = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and agent.fuel > 0:
                    agent.leftThrustBool = True
                if event.key == pygame.K_RIGHT and agent.fuel > 0:
                    agent.rightThrustBool = True
                if event.key == pygame.K_UP and agent.fuel > 0:
                    agent.thrustBool = True
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    agent.idleThrustBool = True
                if event.key == pygame.K_UP:
                    agent.idleThrustBool = True

        step(agent)

        #display
        display(background, 0, 0)
        display(landingPad, landingPadX, landingPadY)

        if didAgentLand(agent) or didAgentCrash(agent):
            agent.set_image(rocket)
            print('Score: ', agent.score())
            agent.reset()

        agent.display()
        pygame.display.update()

main()

