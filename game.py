import libtcodpy as libtcod

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20

playerx = SCREEN_WIDTH/2
playery = SCREEN_HEIGHT/2

class Actor(object):
	''' This is anything that can be drawn to the screen: 
		Player, monsters, items, stairs '''
	def __init__(self, x, y, char, color):
		self.x     = x
		self.y     = y
		self.char  = char
		self.color = color

	def move(self, dx, dy):
		self.x += dx
		self.y += dy

	def draw(self):
		libtcod.console_set_default_foreground(con, self.color)
		libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

	def clear(self):
		libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

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

#
# Main Loop
#

while not libtcod.console_is_window_closed():
	libtcod.console_set_default_foreground(con, libtcod.white)

	for actor in actors:
		actor.draw()

	libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)		# Blitting the non-root console's content to the root console for actual display.
	libtcod.console_flush()

	for actor in actors:
		actor.clear()
	exit = handle_keys()
	if exit:
		break