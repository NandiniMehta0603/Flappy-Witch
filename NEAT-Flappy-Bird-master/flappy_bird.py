import pygame
import random
import os
import time
import neat
import visualize #The process of finding trends and correlations in our data by representing it pictorially is called Data Visualization.
import pickle #“Pickling” is the process whereby a Python object hierarchy is converted into a byte stream,
pygame.font.init()  # init font

WIN_WIDTH = 600 #width of the pop-up window
WIN_HEIGHT = 700 #height of the pop-up window
FLOOR = 730
STAT_FONT = pygame.font.SysFont("comicsans", 50)
END_FONT = pygame.font.SysFont("comicsans", 70)
DRAW_LINES = False

WIN = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

pipe_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")).convert_alpha())
bg_img = pygame.transform.scale(pygame.image.load(os.path.join("imgs","newbg3.jpg")).convert_alpha(), (600, 900))
bird_images = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird" + str(x) + ".png"))) for x in range(1,4)]
base_img = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")).convert_alpha())

gen = 0
#creating a bunch of birdes moving all around
class Bird:
    """
    Bird class representing the flappy bird
    """
    MAX_ROTATION = 25
    IMGS = bird_images
    ROT_VEL = 20 #for tilting the bird
    ANIMATION_TIME = 5
    #refering to the starting position of the bird
    def __init__(self, x, y):
        """
        Initialize the object
        :param x: starting x pos (int)
        :param y: starting y pos (int)
        :return: None
        """
        self.x = x
        self.y = y
        self.tilt = 0  # degrees to tilt
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_count = 0
        self.img = self.IMGS[0]
    #we need the bird to flap up and jump
    def jump(self):
        """
        make the bird jump
        :return: None
        """
        self.vel = -10.5 #as we need the bird to go in upward direction...so -ve velocity
        self.tick_count = 0 #to keep track of when we last jumped
        self.height = self.y #keeps track of where the bird jumps from

    def move(self):
        """
        make the bird move
        :return: None
        """
        self.tick_count += 1 #count that we have moved by a frame now...ie how many seconds we have been moving for

        # for downward acceleration
        displacement = self.vel*(self.tick_count) + 0.5*(3)*(self.tick_count)**2  # calculate displacement ie how many pixels we move up or down

        # terminal velocity
        if displacement >= 16: #so that we dont have velocity way too far up or way too down
            displacement = (displacement/abs(displacement)) * 16

        if displacement < 0:
            displacement -= 2 #if we are moving upwards...lets move upward a little bit more

        self.y = self.y + displacement

        if displacement < 0 or self.y < self.height + 50:  # tilt up
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:  # tilt down
            if self.tilt > -90: #rotate the bird completely by 90 degrees now
                self.tilt -= self.ROT_VEL

    def draw(self, win): #win is the window we draw the bird on
        """
        draw the bird
        :param win: pygame window or surface
        :return: None
        """
        self.img_count += 1 #to show how many times we have displayed one image

        # For animation of bird, loop through three images
        if self.img_count <= self.ANIMATION_TIME:
            self.img = self.IMGS[0] #display the first flappy bird image
        elif self.img_count <= self.ANIMATION_TIME*2:
            self.img = self.IMGS[1] #show the second flappy bird image
        elif self.img_count <= self.ANIMATION_TIME*3:
            self.img = self.IMGS[2] #show the third image 
        elif self.img_count <= self.ANIMATION_TIME*4:
            self.img = self.IMGS[1] #show the first image
        elif self.img_count == self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0 #reset the image count now

        # so when bird is nose diving it isn't flapping ie it is tilted at 90 degrees downward...we dont want to show that it is flapping
        if self.tilt <= -80:
            self.img = self.IMGS[1] #display the image when it is on a level
            self.img_count = self.ANIMATION_TIME*2 #ie when it starts again it doesnt look as if it has skipped any frame

        #rotates bird around the center
        # tilt the bird
        blitRotateCenter(win, self.img, (self.x, self.y), self.tilt) #blit the image around a certain position

    def get_mask(self): #to get collision for the current image
        """
        gets the mask for the current image of the bird
        :return: None
        """
        return pygame.mask.from_surface(self.img) #mask() function return an object of same shape as self and whose corresponding entries are from self where cond is False and otherwise are from other object.


class Pipe():
    """
    represents a pipe object
    """
    GAP = 200 #space in between the pipes
    VEL = 5 #how fast the pipes move

    def __init__(self, x): #not y because height of these tubes will be completely random 
        """
        initialize pipe object
        :param x: int
        :param y: int
        :return" None
        """
        self.x = x
        self.height = 0

        # where the top and bottom of the pipe is
        self.top = 0
        self.bottom = 0

        self.PIPE_TOP = pygame.transform.flip(pipe_img, False, True)
        self.PIPE_BOTTOM = pipe_img #store the flipped image of the pipe

        self.passed = False

        self.set_height()

    def set_height(self):
        """
        set the height of the pipe, from the top of the screen
        :return: None
        """
        self.height = random.randrange(50, 450) #random number where the tp of the pipe would be 
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self): #move the pipes
        """
        move pipe based on vel
        :return: None
        """
        self.x -= self.VEL

    def draw(self, win):
        """
        draw both the top and bottom of the pipe
        :param win: pygame window/surface
        :return: None
        """
        # draw top
        win.blit(self.PIPE_TOP, (self.x, self.top))
        # draw bottom
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))


    def collide(self, bird, win):
        """
        returns if a point is colliding with the pipe
        :param bird: Bird object
        :return: Bool
        """
        #we consider the objects inside imaginary boxes and check if boxes collide...we do this witht the help of masks...masks is the array of the pixels inside the box
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))#round as you cannot have negative or decimal numbers here
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))
        #offset-how far away these masks are from each other
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)# here we find the point of collision
        t_point = bird_mask.overlap(top_mask,top_offset) #if no collision point then it returns none

        if b_point or t_point: #ie it is not none
            return True

        return False

class Base:
    """
    Represnts the moving floor of the game
    """
    VEL = 5
    WIDTH = base_img.get_width()
    IMG = base_img

    def __init__(self, y): #the axis moves in the x direction, so we do not need to find the x coordinate
        """
        Initialize the object
        :param y: int
        :return: None
        """
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH

    def move(self):
        """
        move floor so it looks like its scrolling
        :return: None
        """
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        if self.x1 + self.WIDTH < 0: 
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:#we check if any one of them is off-screen so that we could take that image at the end
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        """
        Draw the floor. This is two images that move together.
        :param win: the pygame surface/window
        :return: None
        """
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def blitRotateCenter(surf, image, topleft, angle):
    """
    Rotate a surface and blit it to the window
    :param surf: the surface to blit to
    :param image: the image surface to rotate
    :param topLeft: the top left position of the image
    :param angle: a float value for angle
    :return: None
    """
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center = image.get_rect(topleft = topleft).center)

    surf.blit(rotated_image, new_rect.topleft)

def draw_window(win, birds, pipes, base, score, gen, pipe_ind): #draw the background image and then draw the bird image over it
    """
    draws the windows for the main game loop
    :param win: pygame window surface
    :param bird: a Bird object
    :param pipes: List of pipes
    :param score: score of the game (int)
    :param gen: current generation
    :param pipe_ind: index of closest pipe
    :return: None
    """
    if gen == 0:
        gen = 1
    win.blit(bg_img, (0,0)) #top-left position of the image

    for pipe in pipes:
        pipe.draw(win)

    base.draw(win)
    for bird in birds:
        # draw lines from bird to pipe
        if DRAW_LINES:
            try:
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_TOP.get_width()/2, pipes[pipe_ind].height), 5)
                pygame.draw.line(win, (255,0,0), (bird.x+bird.img.get_width()/2, bird.y + bird.img.get_height()/2), (pipes[pipe_ind].x + pipes[pipe_ind].PIPE_BOTTOM.get_width()/2, pipes[pipe_ind].bottom), 5)
            except:
                pass
        # draw bird
        bird.draw(win)

    # score
    score_label = STAT_FONT.render("Score: " + str(score),1,(255,255,255))
    win.blit(score_label, (WIN_WIDTH - score_label.get_width() - 15, 10))

    # generations
    score_label = STAT_FONT.render("Gens: " + str(gen-1),1,(255,255,255))
    win.blit(score_label, (10, 10))

    # alive
    score_label = STAT_FONT.render("Alive: " + str(len(birds)),1,(255,255,255))
    win.blit(score_label, (10, 50))

    pygame.display.update()


def eval_genomes(genomes, config):
    """
    runs the simulation of the current population of
    birds and sets their fitness based on the distance they
    reach in the game.
    """
    #this fitness function is going to take all of the genomes and is going to evaluate all of them..what happens to one bird can happen to all
    global WIN, gen
    win = WIN
    gen += 1

    # start by creating lists holding the genome itself, the
    # neural network associated with the genome and the
    # bird object that uses that network to play
    nets = [] #you need to keep track of all the genomes that if they have passed or change the fitness according to how far they have moved
    birds = []
    ge = []
    # we are setting up a neural network for our genome, start, give it the config file, append it to list and append the bird object into the list and then put the genome on the same position as the bird so that we can keep track of its fitness value as we desire
    for genome_id, genome in genomes:
        genome.fitness = 0  # start with fitness level of 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(230,350)) #standard bird starting at a position 
        ge.append(genome) #append this genome into a ge list

    base = Base(FLOOR)
    pipes = [Pipe(700)]
    score = 0

    clock = pygame.time.Clock() #to monitor how fast the bird moves

    run = True
    while run and len(birds) > 0:
        clock.tick(30) #atmost 30 ticks every second...so if the bird falls...it falls at a slower rate and looks better

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit() #to quit the game
                quit()
                break
        #problem is do we look at only 1 pipe or both the pipes while the bird moves.
        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():  # determine whether to use the first or second pip
                pipe_ind = 1                                                                 # pipe on the screen for neural network input
                #else if none birds coud cross the first pipe, instead of quitting the game we generate a new generation

        for x, bird in enumerate(birds):  # give each bird a fitness of 0.1 for each frame it stays alive..kinda encouraging the bird to keep moving forward.
            ge[x].fitness += 0.1 #such small value bec this 0.1 will be multiplied by the clock tine ie 30 times.
            bird.move()

            # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
            output = nets[birds.index(bird)].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
                bird.jump()

        base.move()

        rem = []
        add_pipe = False
        for pipe in pipes:
            pipe.move()
            # check for collision
            for bird in birds:
                if pipe.collide(bird, win):
                    ge[birds.index(bird)].fitness -= 1 #every time bird hits a pipe, it removes 1 from the fitness score so that we don't make it to the birds that are not fit enough..ie if there are 2 birds...1 hits the pipe and the other which doesn't and both are at the same level then we favor the one which doesn't hit the pipe. SO we remove the bird, the neural network associated to it and the genome
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:#if the pipe is completely off the screen
                rem.append(pipe)

            if not pipe.passed and pipe.x < bird.x:#check if we have passed the pipe
                pipe.passed = True
                add_pipe = True

        if add_pipe: #as soon as we pass one pipe another will be created
            score += 1
            # can add this line to give more reward for passing through a pipe (not required)
            #if the bird makes it through the pipe, we give it +5 fitness score
            for genome in ge:
                genome.fitness += 5
            pipes.append(Pipe(WIN_WIDTH))

        for r in rem:
            pipes.remove(r)

        for bird in birds:
            if bird.y + bird.img.get_height() - 10 >= FLOOR or bird.y < -50: #this condition also checks for if the bird umps over the pipes from the top so as to never die
                #when the bird hits the ground, rather than removing the fitness value or something, we remove the bird from the list only 
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        draw_window(WIN, birds, pipes, base, score, gen, pipe_ind)

        # break if score gets large enough
        '''if score > 20:
            pickle.dump(nets[0],open("best.pickle", "wb"))
            break'''

#by generating a 100 birds in a generation, we generate almost every possible neural network
def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """

    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True)) #gives out some output and some stats
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))
    #we assume fittest on the basis that how far the bird goes.
    # Run for up to 50 generations.
    winner = p.run(eval_genomes, 50)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))


if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path) #absolute path to the file
