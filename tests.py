MAP_WIDTH = 80
MAP_HEIGHT = 45

class Tile(object):
	''' Map tiles, and their properties '''
	def __init__(self, blocked, block_sight = None):
		self.blocked = blocked

		# By default, if a tile is blocked, it also blocks sight
		if block_sight is None: block_sight = blocked
		self.block_sight = block_sight

def make_map():
	global map
	# Fill map with 'unblocked' tiles
	map = [[ Tile(False) 
		for y in range(MAP_HEIGHT) ] 
			for x in range(MAP_WIDTH) ]	# List comprehensions to make two-dimensional arrays!

	map[30][22].blocked = True
	map[30][22].block_sight = True
	map[50][22].blocked = True
	map[50][22].block_sight = True

	return map

make_map()

print map