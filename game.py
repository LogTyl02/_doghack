import libtcodpy as libtcod

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20



#
# Classes
#

class Actor(object):
	''' This is anything that can be drawn to the screen: 
		Player, monsters, items, stairs '''
	def __init__(self, x, y, char, color):
		self.x     = x
		self.y     = y
		self.char  = char
		self.color = color

	def move(self, dx, dy):
		if not map[self.x + dx][self.y + dy].blocked:  # This makes blocked map pieces impassible.
			self.x += dx
			self.y += dy

	def draw(self):
		libtcod.console_set_default_foreground(con, self.color)
		libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

	def clear(self):
		libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)


##			  ##
#	The Map	   #	
##			  ##

MAP_WIDTH = 80
MAP_HEIGHT = 45

color_dark_wall = libtcod.Color(165, 180, 175)	# Kind of a grayish green, clay color
color_dark_ground = libtcod.Color(120, 100, 65) # Dark Brown, dirty 

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

#####


# Needs to be moved into a class
def handle_keys():
	global playerx, playery

	key = libtcod.console_wait_for_keypress(True)		# Waits for user input before continuing
	if key.vk == libtcod.KEY_ENTER and key.lalt:
		libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
	elif key.vk == libtcod.KEY_ESCAPE:
		return True

	if libtcod.console_is_key_pressed(libtcod.KEY_UP) or libtcod.console_is_key_pressed(libtcod.KEY_KP8):
		player.move(0, -1)

	elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN) or libtcod.console_is_key_pressed(libtcod.KEY_KP2):
		player.move(0, 1)

	elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT) or libtcod.console_is_key_pressed(libtcod.KEY_KP4):
		player.move(-1, 0)

	elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT) or libtcod.console_is_key_pressed(libtcod.KEY_KP6):
		player.move(1, 0)

	elif libtcod.console_is_key_pressed(libtcod.KEY_KP7):
		player.move(-1, -1)

	elif libtcod.console_is_key_pressed(libtcod.KEY_KP9):
		player.move(1, -1)

	elif libtcod.console_is_key_pressed(libtcod.KEY_KP1):
		player.move(-1, +1)

	elif libtcod.console_is_key_pressed(libtcod.KEY_KP3):
		player.move(1, 1)

def render_all():

	for actor in actors:
		actor.draw()

	for y in range(MAP_HEIGHT):
		for x in range(MAP_WIDTH):
			wall = map[x][y].block_sight
			if wall:
				#libtcod.console_set_char_background(con, x, y, color_dark_wall, libtcod.BKGND_SET)
				libtcod.console_put_char_ex(con, x, y, '#', color_dark_wall, libtcod.gray)
			else:
				libtcod.console_set_char_background(con, x, y, color_dark_ground, libtcod.BKGND_SET)

	libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)



libtcod.console_set_custom_font('dejavu16x16_gs_tc.png', libtcod.FONT_TYPE_GRAYSCALE | libtcod.FONT_LAYOUT_TCOD)

libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'doghack alpha', False)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)	# Making a non-root console for buffer-drawing effects, etc.

libtcod.sys_set_fps(LIMIT_FPS)

#
# Init Character and Stuff
#

# Our hero!
player = Actor(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, '@', libtcod.white)

# Some miscreant
npc = Actor(SCREEN_WIDTH/2 - 5, SCREEN_HEIGHT/2, '@', libtcod.yellow)

# A scary demon! I hope it's not Demogorgon...
demon = Actor(SCREEN_WIDTH/2 - 10, SCREEN_HEIGHT/2 - 5, '&', libtcod.magenta)

actors = [npc, demon, player]



make_map()

#
# Main Loop
#

while not libtcod.console_is_window_closed():
	libtcod.console_set_default_foreground(con, libtcod.white)

	render_all()
	libtcod.console_flush()

	for actor in actors:
		actor.clear()
	exit = handle_keys()
	if exit:
		break