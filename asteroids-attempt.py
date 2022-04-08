#python3

import numpy as np
from matplotlib import pyplot as plt
import keyboard
from matplotlib.animation import FuncAnimation


class game():
    def __init__(self, player, asteroids_count=5, asteroid_speed=.02, size=(1, 1), asteroid_size=(.1, .2),
                 boss_gate_size=.1, acceleration=.1, rotation_speed=1, circle_detail=20, safe_radius=.2, fps=30):
        self.player = player
        self.pos = np.array([size[0] / 2, size[1] / 2])
        self.vel = np.array([0., 0.])
        self.ang = 0
        self.fps = fps
        self.size = size
        self.asteroids_pos = np.random.random((asteroids_count, 2)) @ [[size[0], 0], [0, size[1]]]
        self.asteroids_vel = np.random.normal(0, asteroid_speed / np.sqrt(2), (asteroids_count, 2))
        self.asteroids_count = asteroids_count
        self.asteroid_sizes = asteroid_size[0] + (asteroid_size[1] - asteroid_size[0]) * np.random.uniform(
            size=asteroids_count)
        self.acceleration = acceleration
        self.rotation_speed = rotation_speed
        self.circle_detail = circle_detail
        self.t = 0
        self.gameover = False

        for i in range(self.asteroids_count):
            x_pos = self.asteroids_pos[i][0]
            y_pos = self.asteroids_pos[i][1]
            while (self.pos[0] - x_pos) ** 2 + (self.pos[1] - y_pos) ** 2 < (safe_radius + self.asteroid_sizes[i]) ** 2:
                self.asteroids_pos[i] = np.random.random(2) * [size[0], size[1]]
                x_pos = self.asteroids_pos[i][0]
                y_pos = self.asteroids_pos[i][1]

    def getAsteroidPos(self, t=None):
        if t is None:
            return self.asteroids_pos
        else:
            return self.asteroids_pos + self.asteroids_vel * (t - self.t)

    def getAsteroidVel(self):
        return self.asteroids_pos

    def getAstroidSizes(self):
        return self.asteroid_sizes

    def update(self):
        if self.gameover:
            return
        self.pos = self.pos + 1 / self.fps * self.vel
        if self.player.get_forwards():
            self.vel = self.vel + self.acceleration * np.array([np.cos(self.ang), np.sin(self.ang)]) / self.fps

        if self.player.get_right():
            self.ang -= self.rotation_speed / self.fps

        if self.player.get_left():
            self.ang += self.rotation_speed / self.fps

        if self.pos[0] > 1:
            self.pos[0] -= 1
        if self.pos[0] < 0:
            self.pos[0] += 1
        if self.pos[1] > 1:
            self.pos[1] -= 1
        if self.pos[1] < 0:
            self.pos[1] += 1

        self.t += 1 / self.fps

        self.asteroids_pos = self.asteroids_pos + self.asteroids_vel / self.fps
        for i in range(self.asteroids_count):
            if self.asteroids_pos[i][0] > 1:
                self.asteroids_pos[i][0] -= 1
            if self.asteroids_pos[i][0] < 0:
                self.asteroids_pos[i][0] += 1
            if self.asteroids_pos[i][1] > 1:
                self.asteroids_pos[i][1] -= 1
            if self.asteroids_pos[i][1] < 0:
                self.asteroids_pos[i][1] += 1
        if self.testCollision():
            self.gameover = True

    def testCollision(self):
        for i in range(self.asteroids_count):
            for x_repeat in -1, 0, 1:
                for y_repeat in -1, 0, 1:
                    x_pos = self.asteroids_pos[i][0] + x_repeat
                    y_pos = self.asteroids_pos[i][1] + y_repeat
                    if (self.pos[0] - x_pos) ** 2 + (self.pos[1] - y_pos) ** 2 < self.asteroid_sizes[i] ** 2:
                        return True
        return False

    def initframe(self, ax):
        self.asteroid_plots = dict()

        circle_linspace = np.linspace(0, 2 * np.pi, self.circle_detail)
        x_circle = np.cos(circle_linspace)
        y_circle = np.sin(circle_linspace)
        for i in range(self.asteroids_count):
            for x_repeat in -1, 0, 1:
                for y_repeat in -1, 0, 1:
                    x_pos = self.asteroids_pos[i][0] + x_repeat
                    y_pos = self.asteroids_pos[i][1] + y_repeat
                    self.asteroid_plots[i, x_repeat, y_repeat] = \
                    ax.plot(x_pos + self.asteroid_sizes[i] * x_circle, y_pos + self.asteroid_sizes[i] * y_circle, "b")[
                        0]
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        self.ship_plot = ax.plot(*self.pos, "ko")[0]
        self.line_plot = \
        ax.plot([self.pos[0], self.pos[0] + 2 * np.cos(self.ang)], [self.pos[1], self.pos[1] + 2 * np.sin(self.ang)],
                "r")[0]

    def updateframe(self, ax):
        ax.set_title("Time is %.2f" % self.t)
        circle_linspace = np.linspace(0, 2 * np.pi, self.circle_detail)
        x_circle = np.cos(circle_linspace)
        y_circle = np.sin(circle_linspace)
        for i in range(self.asteroids_count):
            for x_repeat in -1, 0, 1:
                for y_repeat in -1, 0, 1:
                    x_pos = self.asteroids_pos[i][0] + x_repeat
                    y_pos = self.asteroids_pos[i][1] + y_repeat
                    self.asteroid_plots[i, x_repeat, y_repeat].set_data(
                        [x_pos + self.asteroid_sizes[i] * x_circle, y_pos + self.asteroid_sizes[i] * y_circle])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        self.ship_plot.set_data(*self.pos)
        self.line_plot.set_data([self.pos[0], self.pos[0] + 2 * np.cos(self.ang)],
                                [self.pos[1], self.pos[1] + 2 * np.sin(self.ang)])


class ai_controller():
    def __init__(self):
        self.g = None
        self.p = None
        self.x = None

        # self.get_forwards()
        # self.get_right()
        # self.get_left()

    def connect(self, g):
        self.g = g
        self.x = np.array([*g.pos, *g.vel, g.ang])
        self.p = np.zeros_like(self.x)

        self.get_forwards()
        self.get_right()
        self.get_left()

    def obstacle(x, y, W1=1, r=(1, 1), c=(0, 0)):
        '''
        Define an area that will represent an obstacle

        Parameters:
            x (float): x position in space
            y (float): y position in space
            W1 (float): weight of cost
            r (tuple): radius in x and y direction
            c (tuple): center of the ellipse
        '''

        ellipse = ((x - c[0]) ** 2 / r[0] + (y - c[1]) ** 2 / r[1]) ** 20 + 1

        return W1 / ellipse

    def obstacle_dx(x, y, W1=1, r=(1, 1,), c=(0, 0)):
        '''
        x derivative of the obstacle

        Parameters:
            x (float): x position in space
            y (float): y position in space
            W (float): weight of cost
            r (tuple): radius in x and y direction
            c (tuple): center of the ellipse
        '''

        circle = (x - c[0]) ** 2 / r[0] + (y - c[1]) ** 2 / r[1]
        numer = -40 * W1 * (x - c[0]) * (circle) ** 19
        denom = r[0] * ((circle) ** 20 + 1) ** 2

        return numer / denom

    def obstacle_dy(x, y, W1=1, r=(1, 1,), c=(0, 0)):
        '''
        y derivative of the obstacle

        Parameters:
            x (float): x position in space
            y (float): y position in space
            W1 (float): weight of cost
            r (tuple): radius in x and y direction
            c (tuple): center of the ellipse
        '''

        circle = (x - c[0]) ** 2 / r[0] + (y - c[1]) ** 2 / r[1]
        numer = -40 * W1 * (y - c[1]) * (circle) ** 19
        denom = r[1] * ((circle) ** 20 + 1) ** 2

        return numer / denom



    def update(self):
        pass

    def get_forwards(self):
        return self.p[4] > 0

    def get_right(self):
        return self.p[2] * np.cos(self.x[4]) + self.p[3] * np.cos(self.x[4]) > 0

    def get_left(self):
        return self.p[2] * np.cos(self.x[4]) + self.p[3] * np.cos(self.x[4]) < 0



if __name__ == "__main__":
    fig = plt.figure()
    ax = plt.subplot()
    g = game(ai_controller(), fps=30)
    g.initframe(ax)


    def update(i):
        g.update()
        g.updateframe(ax)


    update(1)

    anim = FuncAnimation(fig, update, frames=[0], interval=1 / g.fps, repeat=True)
    plt.show()
