import libtcodpy as libtcod

class Fighter:
	# Combat-related properties and methods
	def __init__(self, hp, defense, power, death_function=None):
		self.max_hp = hp
		self.hp = hp
		self.defense = defense
		self.power = power
		self.death_function = death_function
		
	def take_damage(self, damage):
		# Apply damage
		if damage > 0:
			self.hp -= damage
		
		if self.hp <= 0:
			function = self.death_function
			if function is not None:
				function(self.owner)
			
	def attack(self, target):
		damage = self.power - target.fighter.defense
		
		if damage > 0:
			# Make the target take damage
			print self.owner.name.capitalize() + " attacks " + target.name + " for " + str(damage) + " hit points."
			target.fighter.take_damage(damage)
		else:
			print self.owner.name.capitalize() + " attacks " + target.name + " but it has no effect!"
		

class BasicMonster:
	# AI for a monster
	def take_turn(self):
		monster = self.owner
		player = monster.get_player()
		
		if libtcod.map_is_in_fov(monster.get_fov_map(), monster.x, monster.y):
		
			if monster.distance_to(player) >= 2:
				monster.move_towards(player.x, player.y)
			
			elif player.fighter.hp > 0:
				monster.fighter.attack(player)