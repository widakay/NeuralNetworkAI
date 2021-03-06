import pygame, sys, time, math

import network
from Map import Map
from Creature import Creature
from operator import itemgetter, attrgetter, methodcaller
import random

from pygame.locals import *

class App:
	def __init__(self):
		self._running = True
		self.surf = None
		self.frameCount = 1
		self.startTime = time.time()
		self.runhistory = []
		self.runs = 0

		self.size = self.width, self.height = -1, -1
		self.speed = 10

		self.map = Map(32, 32)
		self.map.generate()

		self.keys = {}

		for i in range(300):
			self.keys[i] = False
		self.creature = Creature()

	def on_init(self):
		pygame.init()
		displayModes = pygame.display.list_modes()
		print "Display modes:", displayModes
		x = displayModes[0][0]
		y = displayModes[0][1]

		if x > 1440:
			x = 1440
		if y > 900:
			y = 900

		mode = (x,y)
		print "Using mode:", mode
		self.size = self.width, self.height = mode

		self.surf = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF | pygame.FULLSCREEN)
		pygame.mouse.set_visible(False)


		self.creature.place(self.map)

		self._running = True

	def on_event(self, event):
		if event.type == pygame.QUIT:
			self._running = False
	def on_loop(self):

		if self.creature._living == False:
			self.reset()


		if self.keys[pygame.K_LEFT]:
			self.speed += 1

		if self.keys[pygame.K_UP]:
			pass

		if self.keys[pygame.K_RIGHT]:
			self.speed -= 1

		if self.keys[pygame.K_DOWN]:
			pass
		if self.speed < 1:
			self.speed = 1

		mouse_pos = pygame.mouse.get_pos()

		self.map.viewPos[0] += mouse_pos[0]-self.width/2
		self.map.viewPos[1] += mouse_pos[1]-self.height/2

		pygame.mouse.set_pos([self.width/2, self.height/2])

		if self.frameCount % self.speed == 0:
			self.simUntilDeath()
	def simUntilDeath(self):
		while self.creature._living == True:
			self.creature.sim(self.map)


	def reset(self):
		self.runs += 1
		self.runhistory.append([self.creature, self.map])
		if self.runs > 4:
			self.runhistory.sort(key=lambda x: x[0].ticks, reverse=True)
			print "-----------------------------"

			#for run in self.runhistory:

			print "ticks:", self.creature.ticks
			for neuronRow in self.creature.network.network:
				for neuron in neuronRow:
					print neuron.weights
			print "-----------------------------"

			self.map.generate()
			self.creature = Creature()

			for layerNum in range(len(self.creature.network.network)):
				for neuronNum in range(len(self.creature.network.network[layerNum])):
					randomNum = random.randint(-4,min(32,len(self.runhistory)/2))
					if randomNum < 0:
						self.creature.network.network[layerNum][neuronNum].weights = [random.random(), random.random(), random.random()]
					else:
						self.creature.network.network[layerNum][neuronNum] = self.runhistory[randomNum][0].network.network[layerNum][neuronNum]
			self.creature.place(self.map)

		else:
			self.map.generate()
			self.creature = Creature()
			self.creature.place(self.map)

	def on_render(self):
		self.surf.fill((0, 0, 0))

		self.map.draw(self.surf)
		self.creature.draw(self.surf, self.map)

		self.frameCount += 1

	def on_cleanup(self):
		pygame.quit()
	def setScale(self, scale):
		if scale < 1:
			return
		self.map.viewPos = [
		(self.map.viewPos[0] - self.width/2)*(scale/self.map.scale)+self.width/2,
		(self.map.viewPos[1] - self.height/2)*(scale/self.map.scale)+self.height/2
		]
		self.map.scale = scale

	def main(self):
		if self.on_init() == False:
			self._running = False

		while self._running:
			for event in pygame.event.get():
				if self.keys[pygame.K_ESCAPE]:
					self._running = False
				self.on_event(event)
				if event.type == pygame.KEYDOWN:
					self.keys[event.key] = True
				if event.type == pygame.KEYUP:
					self.keys[event.key] = False
				if event.type == pygame.QUIT:
					self._running = False
				if event.type == MOUSEBUTTONDOWN:
					if event.button == 4:
						self.setScale(self.map.scale * 1.03)
					if event.button == 5:
						self.setScale(self.map.scale * 0.97)
				if event.type == MOUSEBUTTONUP:
					if event.button == 1:
						self.reset()


			self.on_loop()
			self.on_render()
			pygame.display.flip()
		self.on_cleanup()



def run():
	app = App()
	app.main()

if __name__ == "__main__" :
	run()
