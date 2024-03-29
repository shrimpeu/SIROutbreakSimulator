import pygame, sys
import numpy as np
import pygame.sysfont

# define colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
GREEN = (50, 150, 50)
PURPLE = (130, 0, 130)
GREY = (230, 230, 230)
HORRIBLE_YELLOW = (190, 175, 50)
RED = (255, 0, 0)

# Caption and Icon
pygame.display.set_caption("SIROutbreakSimulator")
icon = pygame.image.load("logo.ico")
pygame.display.set_icon(icon)


# Initializing and Defining Font
font_style = "Arial.tff"
font_size = 36
pygame.init()

font = pygame.font.SysFont(font_style, font_size)


# Background for the Image
s_width = 600
s_height = 480
screen = pygame.display.set_mode((s_width, s_height))
bg_image = pygame.image.load("grass.jpeg")
bg_image = pygame.transform.scale(bg_image, (900, 600))

# Set the window title
pygame.display.set_caption("SIR Outbreak Simulator")


# Red = Infected , Blue = Susceptible and Quarantined, Purple = Recovered, Yellow = Death

# This class creates a dot object that is used in the simulation
class Dot(pygame.sprite.Sprite):
    # Initialize the dot object with given parameters
    def __init__(
            self,
            x,
            y,
            width,
            height,
            color=BLACK,
            radius=5,
            velocity=[0, 0],
            randomize=False,
    ):
        super().__init__()
        # Creates a surface to draw a circle on
        self.image = pygame.Surface([radius * 2, radius * 2])
        self.image.fill(GREEN)
        pygame.draw.circle(
            self.image, color, (radius, radius), radius
        )

        self.rect = self.image.get_rect()
        self.pos = np.array([x, y], dtype=np.float64)
        self.vel = np.asarray(velocity, dtype=np.float64)

        self.killswitch_on = False
        self.recovered = False
        self.randomize = randomize

        self.WIDTH = width
        self.HEIGHT = height

    # Update the position and state of the dot
    def update(self):
        # Update the position based on the velocity
        self.pos += self.vel

        x, y = self.pos

        # Periodic boundary conditions
        # If the dot goes off the left edge of the screen, wrap it around to the right side
        if x < 0:
            self.pos[0] = self.WIDTH
            x = self.WIDTH
        # If the dot goes off the right edge of the screen, wrap it around to the left side
        if x > self.WIDTH:
            self.pos[0] = 0
            x = 0
        # If the dot goes off the top edge of the screen, wrap it around to the bottom side
        if y < 0:
            self.pos[1] = self.HEIGHT
            y = self.HEIGHT
        # If the dot goes off the bottom edge of the screen, wrap it around to the top side
        if y > self.HEIGHT:
            self.pos[1] = 0
            y = 0

        # Set the position of the dot's rectangle
        self.rect.x = x
        self.rect.y = y

        # Normalize the velocity if it is too high
        vel_norm = np.linalg.norm(self.vel)
        if vel_norm > 3:
            self.vel /= vel_norm

        # Add randomness to the velocity
        if self.randomize:
            self.vel += np.random.rand(2) * 2 - 1

        # Update the killswitch
        if self.killswitch_on:
            self.cycles_to_fate -= 1

            # Check if the killswitch has expired and decide
            # whether to kill or recover the dot
            if self.cycles_to_fate <= 0:
                self.killswitch_on = False
                some_number = np.random.rand()
                if self.mortality_rate > some_number:
                    self.kill()
                else:
                    self.recovered = True

    # Respawn the dot at a new location with the same velocity and color
    def respawn(self, color, radius=5):
        return Dot(
            self.rect.x,
            self.rect.y,
            self.WIDTH,
            self.HEIGHT,
            color=color,
            velocity=self.vel,
        )

    """
    Sets a "killswitch" on the dot, which will cause it to be
    killed or recover after a certain number of cycles
    """

    def killswitch(self, cycles_to_fate=20, mortality_rate=0.2):
        self.killswitch_on = True
        # Set the number of cycles until the fate of the dot is decided
        self.cycles_to_fate = cycles_to_fate
        # Set the mortality rate of the dot
        # (the probability that the dot will be killed if the killswitch is triggered)
        self.mortality_rate = mortality_rate


# sets up and simulates the spread of an infectious disease in a population of people represented by Dot objects.
class Simulation:
    """
    Initializes the width and height of the simulation,
    as well as the number of susceptible, infected,
    recovered individuals, total number of time steps 'T',
    the number of cycles before a dot's fate is determined,
    and the mortality rate
    """

    def __init__(self, width=600, height=480):
        self.WIDTH = width
        self.HEIGHT = height

        self.susceptible_container = pygame.sprite.Group()
        self.infected_container = pygame.sprite.Group()
        self.recovered_container = pygame.sprite.Group()
        self.all_container = pygame.sprite.Group()

        self.n_susceptible = 20
        self.n_infected = 1
        self.n_quarantined = 0
        self.T = 3000
        self.cycles_to_fate = 20
        self.mortality_rate = 0.2

    """
    Initializes Pygame and creates Dot objects for each individual in the
    population, with randomly assigned positions and velocities. It also
    sets up a clock and a stats surface for tracking the progress of the
    simulation
    """

    def start(self, randomize=False):
        self.N = (
                self.n_susceptible + self.n_infected + self.n_quarantined
        )

        pygame.init()
        screen = pygame.display.set_mode([self.WIDTH, self.HEIGHT])

        # For the Legend of the Graph -> Better Comprehension

        window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        font = pygame.font.SysFont('Arial', 14)
        legend = font.render('Legend for Graph:', True, (WHITE))
        red = font.render('Red: Infected', True, (WHITE))
        suscep = font.render('Blue: Susceptible', True, (WHITE))
        recov = font.render('Purple: Recovered', True, (WHITE))
        dead = font.render('Yellow: Dead', True, (WHITE))

        legend_rect = legend.get_rect()
        red_rect = red.get_rect()
        suscep_rect = suscep.get_rect()
        recov_rect = recov.get_rect()
        dead_rect = dead.get_rect()

        legend_rect.bottomleft = (260, self.HEIGHT)
        red_rect.bottomleft = (260, self.HEIGHT)
        suscep_rect.bottomleft = (260, self.HEIGHT)
        recov_rect.bottomleft = (260, self.HEIGHT)
        dead_rect.bottomleft = (260, self.HEIGHT)

        legend_rect.move_ip(0, -530 - legend_rect.height)
        red_rect.move_ip(0, -505 - red_rect.height)
        suscep_rect.move_ip(0, -485 - suscep_rect.height)
        recov_rect.move_ip(0, -465 - recov_rect.height)
        dead_rect.move_ip(0, -445 - dead_rect.height)

        # Dot for Susceptible
        for i in range(self.n_susceptible):
            x = np.random.randint(0, self.WIDTH + 1)
            y = np.random.randint(0, self.HEIGHT + 1)
            vel = np.random.rand(2) * 2 - 1
            guy = Dot(
                x,
                y,
                self.WIDTH,
                self.HEIGHT,
                color=BLUE,
                velocity=vel,
                randomize=randomize,
            )
            self.susceptible_container.add(guy)
            self.all_container.add(guy)

        # Dot for Quarantined
        for i in range(self.n_quarantined):
            x = np.random.randint(0, self.WIDTH + 1)
            y = np.random.randint(0, self.HEIGHT + 1)
            vel = [0, 0]
            guy = Dot(
                x,
                y,
                self.WIDTH,
                self.HEIGHT,
                color=BLUE,
                velocity=vel,
                randomize=False,
            )
            self.susceptible_container.add(guy)
            self.all_container.add(guy)

        # Dot for Infected
        for i in range(self.n_infected):
            x = np.random.randint(0, self.WIDTH + 1)
            y = np.random.randint(0, self.HEIGHT + 1)
            vel = np.random.rand(2) * 2 - 1
            guy = Dot(
                x,
                y,
                self.WIDTH,
                self.HEIGHT,
                color=RED,
                velocity=vel,
                randomize=randomize,
            )
            self.infected_container.add(guy)
            self.all_container.add(guy)

        # stats for graph
        stats = pygame.Surface((self.WIDTH // 4, self.HEIGHT // 4))
        stats.fill(GREY)
        stats.set_alpha(230)
        stats_pos = (self.WIDTH // 40, self.HEIGHT // 40)

        clock = pygame.time.Clock()

        for i in range(self.T):
            # handles quitting the simulation if the user closes the window
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
            # updates the positions of the dots and the stats surface in each time step
            self.all_container.update()

            screen.fill(WHITE)

            # Blit the background image to the screen
            screen.blit(bg_image, (0, 0))

            # Update stats
            stats_height = stats.get_height()
            stats_width = stats.get_width()
            n_inf_now = len(self.infected_container)
            n_pop_now = len(self.all_container)
            n_rec_now = len(self.recovered_container)
            t = int((i / self.T) * stats_width)
            y_infect = int(
                stats_height - (n_inf_now / n_pop_now) * stats_height
            )
            y_dead = int(
                ((self.N - n_pop_now) / self.N) * stats_height
            )
            y_recovered = int((n_rec_now / n_pop_now) * stats_height)
            stats_graph = pygame.PixelArray(stats)
            stats_graph[t, y_infect:] = pygame.Color(*RED)
            stats_graph[t, :y_dead] = pygame.Color(*HORRIBLE_YELLOW)
            stats_graph[
            t, y_dead: y_dead + y_recovered
            ] = pygame.Color(*PURPLE)

            # New infections?
            collision_group = pygame.sprite.groupcollide(
                self.susceptible_container,
                self.infected_container,
                True,
                False,
            )

            for guy in collision_group:
                new_guy = guy.respawn(RED)
                new_guy.vel *= -1
                new_guy.killswitch(
                    self.cycles_to_fate, self.mortality_rate
                )
                self.infected_container.add(new_guy)
                self.all_container.add(new_guy)

            # Any recoveries?
            recovered = []
            for guy in self.infected_container:
                if guy.recovered:
                    new_guy = guy.respawn(PURPLE)
                    self.recovered_container.add(new_guy)
                    self.all_container.add(new_guy)
                    recovered.append(guy)

            if len(recovered) > 0:
                self.infected_container.remove(*recovered)
                self.all_container.remove(*recovered)

            self.all_container.draw(screen)

            del stats_graph
            stats.unlock()
            window.blit(legend, legend_rect)
            window.blit(red, red_rect)
            window.blit(suscep, suscep_rect)
            window.blit(recov, recov_rect)
            window.blit(dead, dead_rect)
            screen.blit(stats, stats_pos)
            pygame.display.flip()
            pygame.display.update()
    
            clock.tick(30)

        pygame.quit()

# For code reausability in other python scripts
if __name__ == "__main__":
    disease = Simulation(900, 600)
    disease.n_susceptible = int(input("Enter number of Susceptible people:"))
    disease.n_quarantined = int(input("Enter number of Quarantined people:"))
    disease.n_infected = int(input("Enter number of Infected people: "))
    cycles_var = int(input("Enter how long the virus would stay on its hos t in seconds: "))
    cycles_converter = cycles_var * 33.3
    disease.cycles_to_fate = float(cycles_converter)
    print("\nMortality rate -> How lethal the virus would be")
    mort_var = float(input("Enter the mortality rate of the virus in percentage: "))
    mort_converter = mort_var * 0.01
    disease.mortality_rate = mort_converter
    disease.start(randomize=True)
