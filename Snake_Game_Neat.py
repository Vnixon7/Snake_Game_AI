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
        self.hunger = 50
        self.dis_list1 = [100]
        self.dis_list2 = [100]
        self.dis_list3 = [100]
        self.dis_list4 = [100]

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

    def move_left(self):
        self.snake_head[0] -= self.vel
        self.dx = -1
        self.dy = 0

    def move_right(self):
        self.snake_head[0] += self.vel
        self.dx = 0
        self.dy = 1

    def move_up(self):
        self.snake_head[1] -= self.vel
        self.dx = 0
        self.dy = -1

    def move_down(self):
        self.snake_head[1] += self.vel
        self.dx = 0
        self.dy = 1

    def Xdis(self, food):

        DisX = abs(food.x - self.snake_head[0] - self.width)

        return DisX

    def Ydis(self, food):

        DisY = abs(food.y - self.snake_head[1] - self.height)

        return DisY

    def move(self):
        if self.dx == 0 and self.dy == 0:
            self.snake_head[0] += self.vel
        self.snake_position.insert(0, list(self.snake_head))
        self.snake_position.pop()

    def disWall(self):
        dis = 0
        if self.dx == 1:
            dis = win_w - self.snake_head[0] - self.width

        if self.dx == -1:
            dis = self.snake_head[0] + self.width

        if self.dy == 1:
            dis = win_h - self.snake_head[1] - self.height

        if self.dy == -1:
            dis = self.snake_head[1] + self.height
        return dis


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


newNum = 50
gen = 0


def main(genomes, config):
    global window, gen, newNum
    nets = []
    ge = []
    snakes = []
    load_in = open('best3.pickle', 'rb')
    bestnet = pickle.load(load_in)
    # implementing NEAT
    for genome_id, genome in genomes:
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(bestnet)
        # nets.append(net)
        snakes.append(snake((0, 0, 0), 30, 30))
        genome.fitness = 0
        ge.append(genome)

    food = Food(30, 30)
    clock = pygame.time.Clock()
    score = 0

    run = True
    while run:

        # starting direction and continuous movement#
        dtime = 0
        clock.tick(13)

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
            xdis = s.Xdis(food)
            ydis = s.Ydis(food)
            wallDis = s.disWall()

            s.dis_list1.append(int(snakefoodDistEuclidean))
            s.dis_list2.append(snakefoodDisManhattan)
            s.dis_list3.append(xdis)
            s.dis_list4.append(ydis)

            output = nets[snakes.index(s)].activate(
                (wallDis, s.dx, s.dy, s.x, s.y, food.x, food.y, snakeheadBottomDis,
                 snakeheadRightDis, snake_length, xdis, ydis, snakefoodDistEuclidean,
                 s.dis_list1[-1], s.dis_list1[-2]))

            # snake moving animation
            s.move()
            s.hunger -= 1

            # moving conditions

            if output[0] > 0.5 and s.dx != -1 and s.x < food.x:
                # ge[x].fitness += 0.1
                s.move_right()

            if output[1] > 0.5 and s.dx != 1 and s.x > food.x:
                # ge[x].fitness += 0.1
                s.move_left()

            if output[2] > 0.5 and s.dy != 1 and s.y > food.y:
                # ge[x].fitness += 0.1
                s.move_up()

            if output[3] > 0.5 and s.dy != -1 and s.y < food.y:
                # ge[x].fitness += 0.1
                s.move_down()

            # fitness conditions

            if s.getRec().colliderect(food.getRec()):
                ge[x].fitness += 10
                s.hunger += 100
                score += 1
                s.count = s.count + 1
                s.snake_position.insert(0, list(s.snake_head))
                food.y = random.randint(0 + 24, 500 - 24)
                food.x = random.randint(0 + 24, 500 - 24)

            if s.dis_list1[-1] >= s.dis_list1[-2]:
                ge[x].fitness -= 1

            if s.dis_list1[-1] < s.dis_list1[-2]:
                ge[x].fitness += .1
            # current and last x distance check
            if s.dis_list3[-1] <= s.dis_list3[-2]:
                ge[x].fitness += .1
            # if s.dis_list3[-1] > s.dis_list3[-2]:
            # ge[x].fitness -= 1
            # current and last y distance check
            if s.dis_list4[-1] <= s.dis_list4[-2]:
                ge[x].fitness += .1
            # if s.dis_list4[-1] > s.dis_list4[-2]:
            # ge[x].fitness -= 1

            head = s.snake_position[0]

            if s.dis_list3[-1] == s.dis_list3[-2] and s.dis_list4[-1] == s.dis_list4[-2]:
                s.timer += 1
            else:
                s.timer = 0

            if s.timer > 5 or s.hunger <= 0 or s.x < 0 + s.width or s.x > win_w - s.width or s.y < 0 + s.height or s.y > win_h - s.height:
                ge[x].fitness -= 10
                s.timer = 0
                snakes.pop(x)
                nets.pop(x)
                ge.pop(x)

        draw_window(food, snakes, score)

        # save best
        if score > newNum:
            pickle.dump(nets[0], open("best3.pickle", "wb"))
            newNum += 50

            break


def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,

                                neat.DefaultSpeciesSet, neat.DefaultStagnation,

                                config_file)

    p = neat.Population(config)
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    winner = p.run(main, 5000000)
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)

    config_path = os.path.join(local_dir, 'NEAT_config.txt')

    run(config_path)
