import pygame
import random
import neat
import os
import math
import pickle
import time

win_w = 500
win_h = 500

# initiating the use of system font and pygame#
pygame.font.init()
pygame.init()

# FPS
clock = pygame.time.Clock()
# initiating game window/surface
window = pygame.display.set_mode((win_w, win_h))

# specifying fonts to use
fontL = pygame.font.SysFont('comicansms', 80)
fontS = pygame.font.SysFont('comicansms', 30)


class snake(object):
    def __init__(self, color, height, width):

        self.color = color
        self.height = height
        self.width = width
        self.dx = 0
        self.dy = 0
        self.count = 0
        self.vel = 10
        self.snake_head = [250, 250]
        self.snake_position = [self.snake_head, [240, 250], [230, 250]]
        self.timer = 0
        self.hunger = 100
        self.dis_list1 = [100]
        self.dis_list2 = [100]
        self.dis_list3 = [100]
        self.dis_list4 = [100]
        self.hunger_list = [100]

    # drawing snake to surface as rect#
    def draw(self, window):
        for pos in self.snake_position:
            pygame.draw.rect(window, self.color, (pos[0], pos[1], self.height, self.width))

    # returning x,y coordinate and height and width#
    def getRec(self):
        return pygame.Rect(self.snake_head[0], self.snake_head[1], self.width, self.height)

    def ate(self, food):
        if food.getRec().colliderect(self.getRec()):
            return True
        else:
            return False

    # Checking collision with food#
    # def ate(self):
    # if food.getRec ().colliderect (self.getRec ()):
    # self.snake_position.insert (0, list (self.snake_head))
    # self.count = self.count + 1
    # self.timer = 0

    # drawing score to surface#
    def score(self):
        score = fontS.render('SCORE: ' + str(self.count), True, (0, 0, 0))
        window.blit(score, (0, 0))

    # checking collision with outer surface#
    def death(self):

        if self.snake_head[0] > win_w - self.width or self.snake_head[0] < 0 + self.width or self.snake_head[
            1] > win_h - self.height or self.snake_head[1] < 0 + self.height:
            youLose = fontL.render('YOU LOST', True, (0, 0, 0))
            restart = fontS.render('Click R to restart', True, (0, 255, 0))
            window.blit(restart, (170, 240))
            window.blit(youLose, (120, 180))
            self.vel = 0
            self.count = 0
            self.timer = 0

    # checking collision with self#
    def collision_self(self):
        self.timer = self.timer + 1
        head = self.snake_position[0]
        if head in self.snake_position[1:] and self.timer > 5:
            youLose = fontL.render('YOU LOST', True, (0, 0, 0))
            restart = fontS.render('Click R to restart', True, (0, 255, 0))
            window.blit(restart, (170, 240))
            window.blit(youLose, (120, 180))
            self.vel = 0
            self.count = 0

    # getting visual of numbers
    def dis_from_edge(self):

        if self.dx == -1:
            print('Your distance from Left edge: ', self.snake_head[0] + 0)
        if self.dx == 1:
            print('Your distance from Right edge: ', self.snake_head[0] - win_w)
        if self.dy == -1:
            print('Your distance from Top edge: ', self.snake_head[1] + 0)
        if self.dy == 1:
            print('Your distance from the Bottom edge: ', self.snake_head[1] - win_h)

    def dis_from(self, dis1, dis2):

        xydis = (self.snake_head[0] - dis1), (self.snake_head[1] - dis2)
        return xydis

    def move_left(self):
        self.snake_head[0] -= self.vel
        self.dx = -1
        self.dy = 0

    def move_right(self):
        self.snake_head[0] += self.vel
        self.dx = 1
        self.dy = 0

    def move_up(self):
        self.snake_head[1] -= self.vel
        self.dx = 0
        self.dy = -1

    def move_down(self):
        self.snake_head[1] += self.vel
        self.dx = 0
        self.dy = 1

    def Xdis(self):
        DisX = 0
        if self.dx == -1:
            DisX = self.snake_head[0]
        if self.dx == 1:
            DisX = self.snake_head[0] - win_w

        return DisX

    def Ydis(self):
        DisY = 0
        if self.dy == -1:
            DisY = self.snake_head[1]
        if self.dy == 1:
            DisY = self.snake_head[1] - win_h

        return DisY


class Food(object):
    def __init__(self, height, width):
        self.x = random.randint(15, 485)
        self.y = random.randint(15, 485)
        self.height = height
        self.width = width

    # drawing food to surface#
    def draw(self, window):
        pie = pygame.image.load('pie4.jpg')
        pie = pygame.transform.scale(pie, (self.width, self.height))
        window.blit(pie, (self.x, self.y))

    # getting x,y coordinate and width,height
    def getRec(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    # checking collision with snake
    # def ate(self):
    # if main.getRec ().colliderect (self.getRec ()):
    # self.x = random.randint (50, 450)
    # self.y = random.randint (50, 450)


# drawing everything to surface#
def draw_window(food, snakes, score):
    window.fill((255, 255, 255))
    for s in snakes:
        s.draw(window)

    food.draw(window)
    scored = fontS.render('SCORE: ' + str(score), True, (0, 0, 0))
    alive = fontS.render('Alive: ' + str(len(snakes)), True, (0, 0, 0))
    window.blit(scored, (0, 0))
    window.blit(alive, (0, 25))

    pygame.display.update()


newNum = 2
gen = 0


def main(genomes, config):
    global window, gen, newNum
    nets = []
    ge = []
    snakes = []

    # implementing NEAT
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        snakes.append(snake((0, 0, 0), 20, 20))
        genome.fitness = 0
        ge.append(genome)

    food = Food(24, 24)
    clock = pygame.time.Clock()
    score = 0

    run = True
    while run:

        # starting direction and continuous movement#

        clock.tick(13)
        keys = pygame.key.get_pressed()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
        if len(snakes) > 0:
            run = True
        else:
            break

        for x, s in enumerate(snakes):
            # inserting new snake head and deleting the tale for movement

            # inputs
            s.x = s.snake_head[0]
            s.y = s.snake_head[1]
            snakeheadBottomDis = win_h - s.y
            snakeheadRightDis = win_w - s.x
            snake_length = len(s.snake_position)
            snakefoodDistEuclidean = math.sqrt((s.x - food.x) ** 2 + (s.y - food.y) ** 2)
            snakefoodDisManhattan = abs(s.x - food.x) + abs(s.y - food.y)
            xdis = s.Xdis()
            ydis = s.Ydis()
            s.dis_list1.append(snakefoodDistEuclidean)
            s.dis_list2.append(snakefoodDisManhattan)
            s.dis_list3.append(s.Xdis())
            s.dis_list4.append(s.Ydis())
            s.hunger_list.append(s.hunger)
            # print('Euclidean: ', dis_list1[-1])
            # print('Manhattan: ', dis_list2[-1])
            # print('X distance from Wall: ', dis_list3[-1])
            # print('Y distance from Wall: ', dis_list4[-1])

            output = nets[snakes.index(s)].activate((s.hunger, s.x, s.y, food.x, food.y, snakeheadBottomDis,
                                                     snakeheadRightDis, snake_length, xdis, ydis,
                                                     snakefoodDisManhattan, snakefoodDistEuclidean, s.dis_list1[-1],
                                                     s.dis_list1[-2],
                                                     s.dis_list2[-1], s.dis_list2[-2], s.dis_list3[-1], s.dis_list3[-2],
                                                     s.dis_list4[-1], s.dis_list4[-2], s.hunger_list[-1],
                                                     s.hunger_list[-2]))

            # snake moving animation
            s.snake_position.insert(0, list(s.snake_head))
            s.snake_position.pop()
            s.hunger -= 1

            # Checking distance Euclidean and Manhattan current and last
            if s.dis_list1[-1] > s.dis_list1[-2]:
                ge[x].fitness -= 1

            if s.dis_list1[-1] < s.dis_list1[-2]:
                ge[x].fitness += 0.5

            if s.dis_list1[-1] > s.dis_list2[-2]:
                ge[x].fitness -= 1

            if s.dis_list1[-1] < s.dis_list2[-2]:
                ge[x].fitness += 0.5

            # checking hunger number and if its decreasing
            if s.hunger_list[-1] < s.hunger_list[-2]:
                ge[x].fitness -= 0.1

            # move right
            if output[0] >= 0 and output[1] < 0 and output[2] < 0 and output[
                3] < 0:
                # and s.x < win_w - s.width and s.y > 0 + s.height:
                # ge[x].fitness += 0.5
                s.move_right()

            # move left
            if output[1] >= 0 and output[0] < 0 and output[2] < 0 and output[
                3] < 0:
                # and s.x < 500 - s.width and s.y > 0 + s.height:
                # ge[x].fitness += 0.5
                s.move_left()

            # move down
            if output[2] >= 0 and output[1] < 0 and output[0] < 0 and output[
                3] < 0:
                # and s.x < 500 - s.width and s.y > 0 + s.height:
                # ge[x].fitness += 0.5
                s.move_down()

            # move up
            if output[3] >= 0 and output[1] < 0 and output[2] < 0 and output[
                3] < 0:
                # and s.x < 500 - s.width and s.y > 0 + s.height:
                # ge[x].fitness += 0.5
                s.move_up()

            # adding more fitness if axis aligns
            if s.snake_head[0] == food.x:
                ge[x].fitness += 0.1
            if s.snake_head[1] == food.x:
                ge[x].fitness += 0.1

            # checking the activation function tanh
            # print ('output 0: ', output[0])
            # print('output 1: ', output[1])
            # print ('output 2: ', output[1])
            # print ('output 3: ', output[1])

            # snake poping on other side of screen if screen limit reached
            if s.snake_head[0] >= win_w - s.width:
                s.snake_head[0] = 12
            if s.snake_head[0] <= 11 + s.width:
                s.snake_head[0] = win_w - s.width - 1
            if s.snake_head[1] >= win_h - s.height:
                s.snake_head[1] = s.height + 15
            if s.snake_head[1] <= 11 + s.height:
                s.snake_head[1] = win_h - s.height - 1

            head = s.snake_position[0]
            # s.x < 0 + s.width or s.x > win_w - s.width or s.y < 0 + s.height or \
            # s.y > win_h - s.height or

            # if run into self you die
            if head in s.snake_position[1:]:
                ge[x].fitness -= 10
                snakes.pop(x)
                nets.pop(x)
                ge.pop(x)

            # if hunger reaches 0 you die
            if s.hunger == 0:
                ge[x].fitness -= 5
                snakes.pop(x)
                nets.pop(x)
                ge.pop(x)

            # if snake collides with food award fitness
            if s.getRec().colliderect(food.getRec()):
                ge[x].fitness += 100
                s.hunger = 100
                score += 1
                s.snake_position.insert(0, list(s.snake_head))
                food.y = random.randint(0 + 24, 500 - 24)
                food.x = random.randint(0 + 24, 500 - 24)

        # print(s.hunger)

        draw_window(food, snakes, score)

        # save best
        if score > newNum:
            pickle.dump(nets[0], open("best3.pickle", "wb"))
            newNum += 1

            break


def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,

                                neat.DefaultSpeciesSet, neat.DefaultStagnation,

                                config_file)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(main, 50000)
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)

    config_path = os.path.join(local_dir, 'NEAT_config.txt')

    run(config_path)
