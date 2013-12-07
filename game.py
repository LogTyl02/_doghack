import libtcodpy as libtcod
import math
import textwrap
 
#actual size of the window
SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
 
#size of the map
MAP_WIDTH = 80
MAP_HEIGHT = 43
 
#parameters for dungeon generator
ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
 
# Monster constants
MAX_ROOM_MONSTERS = 2

# Items
MAX_ROOM_ITEMS = 2

INVENTORY_WIDTH = 50
 
FOV_ALGO = 0  #default FOV algorithm
FOV_LIGHT_WALLS = True  #light walls or not
TORCH_RADIUS = 10
 
# Sizes and values relevant for the GUI
BAR_WIDTH = 21
PANEL_HEIGHT = 8
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT

MSG_X = BAR_WIDTH + 2
MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
MSG_HEIGHT = PANEL_HEIGHT - 1

LIMIT_FPS = 20  #20 frames-per-second maximum
 
 
color_dark_wall = libtcod.darkest_sepia
color_light_wall = libtcod.sepia
color_dark_ground = libtcod.darkest_gray
color_light_ground = libtcod.darker_gray

class Item:
	def pick_up(self):
		if len(inventory) >= 26:
			message('Your inventory is full. Maybe you should pawn some of your stuff.', libtcod.cyan)
		else:
			inventory.append(self.owner)
			objects.remove(self.owner)
			message('You picked up a ' + str(self.owner.name) + '.', libtcod.light_green)

class Fighter:
	# Combat-related properties and methods
	def __init__(self, hp, defense, power, death_function=None):
		self.death_function = death_function
		self.max_hp = hp
		self.hp = hp
		self.defense = defense
		self.power = power

	def take_damage(self, damage):
		if damage > 0:
			self.hp -= damage

		if self.hp <= 0:
			function = self.death_function
			if function is not None:
				function(self.owner)

	def attack(self, target):
		damage = self.power - target.fighter.defense

		if damage > 0:
			message('The ' + str(self.owner.name.capitalize()) + ' attacks ' + str(target.name) + ' for ' + str(damage) + ' hit points! ', libtcod.white)
			target.fighter.take_damage(damage)
		else:
			message('The ' + str(self.owner.name.capitalize()) + ' attacks ' + str(target.name) + ' but it has no effect! ', libtcod.white)

class BasicMonster:
	# Ai for a basic monster
	def take_turn(self):
		monster = self.owner
		if libtcod.map_is_in_fov(fov_map, monster.x, monster.y):
			# Move towards player if far away
			if monster.distance_to(player) >= 2:
				monster.move_towards(player.x, player.y)
			# Close enough, attack!
			elif player.fighter.hp > 0:
				monster.fighter.attack(player)

class Tile:
    #a tile of the map and its properties
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked
 
        #all tiles start unexplored
        self.explored = False
 
        #by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight
 
class Rect:
    #a rectangle on the map. used to characterize a room.
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h
 
    def center(self):
        center_x = (self.x1 + self.x2) / 2
        center_y = (self.y1 + self.y2) / 2
        return (center_x, center_y)
 
    def intersect(self, other):
        #returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)
 
class Object:
    #this is a generic object: the player, a monster, an item, the stairs...
    #it's always represented by a character on screen.
    def __init__(self, x, y, char, color, name, blocks = False, fighter = None, ai = None, item=None):
    	self.item = item
    	if self.item:
    		self.item.owner = self

    	self.fighter = fighter
    	if self.fighter: # Let the fighter component knows who owns it
    		self.fighter.owner = self

    	self.ai = ai
    	if self.ai: # Let the AI compenent know who owns it
    		self.ai.owner = self

    	self.name = name
    	self.blocks = blocks
        self.x = x
        self.y = y
        self.char = char
        self.color = color
 
    def move(self, dx, dy):
        #move by the given amount, if the destination is not blocked
        if not is_blocked(self.x + dx, self.y + dy):
            self.x += dx
            self.y += dy
 
    def move_towards(self, target_x, target_y):
    	# Vector from this object to the target, and distance
    	dx = target_x - self.x
    	dy = target_y - self.y
    	distance = math.sqrt( (dx ** 2) + (dy ** 2) )

    	# Normalize it to length 1 (preserving direction), then round it and
    	#	convert it to integer so the movement is restricted to the map grid
    	dx = int(round(dx / distance))
    	dy = int(round(dy / distance))
    	self.move(dx, dy)

    def distance_to(self, other):
    	# Return the distance to another object
    	dx = other.x - self.x
    	dy = other.y - self.y
    	return math.sqrt(dx ** 2 + dy ** 2)

    def draw(self):
        #only show if it's visible to the player
        if libtcod.map_is_in_fov(fov_map, self.x, self.y):
            #set the color and then draw the character that represents this object at its position
            libtcod.console_set_default_foreground(con, self.color)
            libtcod.console_put_char(con, self.x, self.y, self.char, libtcod.BKGND_NONE)

    def send_to_back(self):
    	# make this object be drawn first, so all others appear above it if they're in the same tile
    	global objects
    	objects.remove(self)
    	objects.insert(0, self)
 
    def clear(self):
        #erase the character that represents this object
        libtcod.console_put_char(con, self.x, self.y, ' ', libtcod.BKGND_NONE)

def place_objects(room):
	# Choose random number of monsters
	num_monsters = libtcod.random_get_int(0, 0, MAX_ROOM_MONSTERS)

	for i in range(num_monsters):
		# Choose random spot for this monsters
		x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
		y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

		if not is_blocked(x, y):
			if libtcod.random_get_int(0, 0, 100) < 80: 		# 80 % chance of getting an orc
				# create an orc
				fighter_component = Fighter(hp=10, defense=0, power=3, death_function = monster_death)
				ai_compenent = BasicMonster()
				monster = Object(x, y, 'o', libtcod.red, 'Orc', blocks=True, fighter=fighter_component, ai=ai_compenent)
			else:
				# create a troll (christ, that seems excessive)
				fighter_component = Fighter(hp=16, defense=1, power=4, death_function = monster_death)
				ai_compenent = BasicMonster()
				monster = Object(x, y, 'T', libtcod.red, 'Troll', blocks=True, fighter=fighter_component, ai=ai_compenent)

			objects.append(monster)

	# Time for items
	num_items = libtcod.random_get_int(0, 0, MAX_ROOM_ITEMS)

	for i in range(num_items):
		#Choose a random spot for this item
		x = libtcod.random_get_int(0, room.x1+1, room.x2-1)
		y = libtcod.random_get_int(0, room.y1+1, room.y2-1)

		# only place it if the tile isn't blocked
		if not is_blocked(x, y):
			#create a healing potion
			item_component = Item()
			item = Object(x, y, '!', name='healing potion', color=libtcod.white, item=item_component)

			objects.append(item)
			item.send_to_back()

def create_room(room):
    global map
    #go through the tiles in the rectangle and make them passable
    for x in range(room.x1 + 1, room.x2):
        for y in range(room.y1 + 1, room.y2):
            map[x][y].blocked = False
            map[x][y].block_sight = False
 
def create_h_tunnel(x1, x2, y):
    global map
    #horizontal tunnel. min() and max() are used in case x1>x2
    for x in range(min(x1, x2), max(x1, x2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False
 
def create_v_tunnel(y1, y2, x):
    global map
    #vertical tunnel
    for y in range(min(y1, y2), max(y1, y2) + 1):
        map[x][y].blocked = False
        map[x][y].block_sight = False
 
def make_map():
    global map, player
 
    #fill map with "blocked" tiles
    map = [[ Tile(True)
        for y in range(MAP_HEIGHT) ]
            for x in range(MAP_WIDTH) ]
 
    rooms = []
    num_rooms = 0
 
    for r in range(MAX_ROOMS):
        #random width and height
        w = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        h = libtcod.random_get_int(0, ROOM_MIN_SIZE, ROOM_MAX_SIZE)
        #random position without going out of the boundaries of the map
        x = libtcod.random_get_int(0, 0, MAP_WIDTH - w - 1)
        y = libtcod.random_get_int(0, 0, MAP_HEIGHT - h - 1)
 
        #"Rect" class makes rectangles easier to work with
        new_room = Rect(x, y, w, h)
 
        #run through the other rooms and see if they intersect with this one
        failed = False
        for other_room in rooms:
            if new_room.intersect(other_room):
                failed = True
                break
 
        if not failed:
            #this means there are no intersections, so this room is valid
 
            #"paint" it to the map's tiles
            create_room(new_room)

            # Add some life to the party
            place_objects(new_room) # Only monsters right now
 
            #center coordinates of new room, will be useful later
            (new_x, new_y) = new_room.center()
 
            if num_rooms == 0:
                #this is the first room, where the player starts at
                player.x = new_x
                player.y = new_y
            else:
                #all rooms after the first:
                #connect it to the previous room with a tunnel
 
                #center coordinates of previous room
                (prev_x, prev_y) = rooms[num_rooms-1].center()
 
                #draw a coin (random number that is either 0 or 1)
                if libtcod.random_get_int(0, 0, 1) == 1:
                    #first move horizontally, then vertically
                    create_h_tunnel(prev_x, new_x, prev_y)
                    create_v_tunnel(prev_y, new_y, new_x)
                else:
                    #first move vertically, then horizontally
                    create_v_tunnel(prev_y, new_y, prev_x)
                    create_h_tunnel(prev_x, new_x, new_y)
 
            #finally, append the new room to the list
            rooms.append(new_room)
            num_rooms += 1
 
 
def render_all():
    global fov_map, color_dark_wall, color_light_wall
    global color_dark_ground, color_light_ground
    global fov_recompute
 
    if fov_recompute:
        #recompute FOV if needed (the player moved or something)
        fov_recompute = False
        libtcod.map_compute_fov(fov_map, player.x, player.y, TORCH_RADIUS, FOV_LIGHT_WALLS, FOV_ALGO)
 
        #go through all tiles, and set their background color according to the FOV
        for y in range(MAP_HEIGHT):
            for x in range(MAP_WIDTH):
                visible = libtcod.map_is_in_fov(fov_map, x, y)
                wall = map[x][y].block_sight
                if not visible:
                    #if it's not visible right now, the player can only see it if it's explored
                    if map[x][y].explored:
                        if wall:
                            libtcod.console_put_char_ex(con, x, y, 177, libtcod.darkest_gray, color_light_wall)
                        else:
                            libtcod.console_put_char_ex(con, x, y, '.', libtcod.darker_gray, color_light_ground)
                else:
                    #it's visible
                    if wall:
                        libtcod.console_put_char_ex(con, x, y, 176, libtcod.gray, color_light_wall)
                    else:
                        libtcod.console_put_char_ex(con, x, y, '.', libtcod.lighter_gray, color_light_ground)
                    #since it's visible, explore it
                    map[x][y].explored = True
 
    #draw all objects in the list
    for object in objects:
    	if object != player:
        	object.draw()
    player.draw()
 	
    #blit the contents of "con" to the root console
    libtcod.console_blit(con, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0, 0)


    # Prepare to render the GUI Panel
    libtcod.console_set_default_background(panel, libtcod.black)
    libtcod.console_clear(panel)

    # print the game messages

    y = 1
    for (line, color) in game_msgs:
    	libtcod.console_set_default_foreground(panel, color)
    	libtcod.console_print_ex(panel, MSG_X, y, libtcod.BKGND_NONE, libtcod.LEFT, line)
    	y += 1


    # Show the player's stats
    render_bar(1, 1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp,
    	libtcod.red, libtcod.darker_red)

    # Blit the contents of the panel to the root console
    libtcod.console_blit(panel, 0, 0, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0, PANEL_Y)

    
 
def is_blocked(x, y):
	# First test the map tile
	if map[x][y].blocked:
		return True
	# Now check for any blocking objects
	for object in objects:
		if object.blocks and object.x == x and object.y == y:
			return True

	return False

def player_move_or_attack(dx, dy):
	global fov_recompute

	# The coordinates to which the player is moving or attacking
	x = player.x + dx
	y = player.y + dy

	# Try to find an attackable object there
	target = None
	for object in objects:
		if object.fighter and object.x == x and object.y == y:
			target = object
			break

	if target is not None:
		player.fighter.attack(target)
	else:
		player.move(dx, dy)
		fov_recompute = True

def handle_keys():
    global fov_recompute

    global playerx, playery

    key = libtcod.console_wait_for_keypress(True)       # Waits for user input before continuing
    if key.vk == libtcod.KEY_ENTER and key.lalt:
        libtcod.console_set_fullscreen(not libtcod.console_is_fullscreen())
    elif key.vk == libtcod.KEY_ESCAPE:
        return 'exit'


    if game_state == 'playing':
	    if libtcod.console_is_key_pressed(libtcod.KEY_UP) or libtcod.console_is_key_pressed(libtcod.KEY_KP8):
	        player_move_or_attack(0, -1)

	    elif libtcod.console_is_key_pressed(libtcod.KEY_DOWN) or libtcod.console_is_key_pressed(libtcod.KEY_KP2):
	        player_move_or_attack(0, 1)

	    elif libtcod.console_is_key_pressed(libtcod.KEY_LEFT) or libtcod.console_is_key_pressed(libtcod.KEY_KP4):
	        player_move_or_attack(-1, 0)

	    elif libtcod.console_is_key_pressed(libtcod.KEY_RIGHT) or libtcod.console_is_key_pressed(libtcod.KEY_KP6):
	        player_move_or_attack(1, 0)

	    elif libtcod.console_is_key_pressed(libtcod.KEY_KP7):
	        player_move_or_attack(-1, -1)

	    elif libtcod.console_is_key_pressed(libtcod.KEY_KP9):
	        player_move_or_attack(1, -1)

	    elif libtcod.console_is_key_pressed(libtcod.KEY_KP1):
	        player_move_or_attack(-1, +1)

	    elif libtcod.console_is_key_pressed(libtcod.KEY_KP3):
	        player_move_or_attack(1, 1)

	    else:
	    	# Test for other keys
	    	key_char = chr(key.c)
	    	# Snagging items

	    	if key_char == 'g' or key_char == ',':
	    		#pick up item
	    		for object in objects: #look for an item in the player's tile
	    			if object.x == player.x and object.y == player.y and object.item:
	    				object.item.pick_up()
	    				break

	    	# Inventory
	    	if key_char == 'i':
	    		#show the inventory
	    		inventory_menu('You do know how to use your inventory, right?\n')

		    	return 'didnt-take-turn'
 
def player_death(player):
 	# The game ends
	global game_state
 	message('YOU DIED!', libtcod.dark_red)
 	game_state = 'dead'

 	# Transform the player into a corpse!
 	player.char = '%'
 	player.color = libtcod.dark_red

def monster_death(monster):
 	# Transform it into a corpse! It doesn't block or do anything
 	message('The ' + str(monster.name.capitalize()) + ' crumples to the floor in a bloody heap!', libtcod.yellow)
 	monster.char = '%'
 	monster.color = libtcod.dark_red
 	monster.blocks = False
 	monster.fighter = None
 	monster.ai = None
 	monster.name = 'remains of', monster.name
 	monster.send_to_back()




def menu(header, options, width):
	if len(options) > 26: raise ValueError('Cannot have a menu with more than 26 options.')

	#calculate the total height for the header after auto-wrap, and one line per option
	header_height = libtcod.console_get_height_rect(con, 0, 0, width, SCREEN_HEIGHT, header)
	height = len(options) + header_height

	#print an off-screen console that represents the menu's window
	window = libtcod.console_new(width, height)

	#print the header, with auto-wrap
	libtcod.console_set_default_foreground(window, libtcod.white)
	libtcod.console_print_rect_ex(window, 0, 0, width, height, libtcod.BKGND_NONE, libtcod.LEFT, header)

	#print all the options

	y = header_height
	letter_index = ord('a')
	for option_text in options:
		text = '(' + chr(letter_index) + ') ' + option_text
		libtcod.console_print_ex(window, 0, y, libtcod.BKGND_NONE, libtcod.LEFT, text)
		y += 1
		letter_index += 1

	# Blit the contents of 'window' to the root console
	x = SCREEN_WIDTH / 2 - width / 2
	y = SCREEN_HEIGHT / 2 - height / 2
	libtcod.console_blit(window, 0, 0, width, height, 0, x, y, 1.0, 0.7)

	#present the root console to the player and wait for a key-press
	libtcod.console_flush()
	key = libtcod.console_wait_for_keypress(True)  #Bugged, try the waitForEvent API

def inventory_menu(header):
	if len(inventory) == 0:
		options = ['Inventory is empty.']
	else:
		options = [item.name for item in inventory]

	index = menu(header, options, INVENTORY_WIDTH)



def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
	# Render a bar (HP, experience, etc). First calculate the width of the bar
	bar_width = int(float(value) / maximum * total_width)

	# Render the background first
	libtcod.console_set_default_background(panel, back_color)
	libtcod.console_rect(panel, x, y, total_width, 1, False, libtcod.BKGND_SCREEN)

	# Now render the bar on top
	libtcod.console_set_default_background(panel, bar_color)
	if bar_width > 0:
		libtcod.console_rect(panel, x, y, bar_width, 1, False, libtcod.BKGND_SCREEN)

	# Finally, some centered text with the values
	libtcod.console_set_default_foreground(panel, libtcod.white)
	libtcod.console_print_ex(panel, x + total_width / 2, y, libtcod.BKGND_NONE, libtcod.CENTER,
		name + ': ' + str(value) + '/' + str(maximum))

def message(new_msg, color = libtcod.white):
	# Split the message if necessary, among multiple lines
	new_msg_lines = textwrap.wrap(new_msg, MSG_WIDTH)

	for line in new_msg_lines:
		#if the buffer is full, remove the first line to make room for the new one
		if len(game_msgs) == MSG_HEIGHT:
			del game_msgs[0]

		# add the new line as a tuple, with the text and color
		game_msgs.append( (line, color) )


#############################################
# Initialization & Main Loop
#############################################

libtcod.console_set_custom_font('terminal16x16_gs_ro.png', libtcod.FONT_TYPE_GREYSCALE | libtcod.FONT_LAYOUT_ASCII_INROW, nb_char_horiz=16, nb_char_vertic=16)
libtcod.console_init_root(SCREEN_WIDTH, SCREEN_HEIGHT, 'doghack alpha', False)
libtcod.sys_set_fps(LIMIT_FPS)

panel = libtcod.console_new(MAP_WIDTH, MAP_HEIGHT)
con = libtcod.console_new(SCREEN_WIDTH, SCREEN_HEIGHT)
 
#create object representing the player
fighter_component = Fighter(hp=30, defense=2, power=3, death_function = player_death)
player = Object(SCREEN_WIDTH/2, SCREEN_HEIGHT/2, '@', libtcod.white, 'Player', fighter=fighter_component)
 
#create an NPC
# npc = Object(SCREEN_WIDTH/2 - 5, SCREEN_HEIGHT/2, '@', libtcod.yellow, 'NPC', True)
 
#the list of objects with those two
objects = [player]

# Inventory

inventory = []

# Game message
game_msgs = []

#generate map (at this point it's not drawn to the screen)
make_map()
 
#create the FOV map, according to the generated map
fov_map = libtcod.map_new(MAP_WIDTH, MAP_HEIGHT)
for y in range(MAP_HEIGHT):
    for x in range(MAP_WIDTH):
        libtcod.map_set_properties(fov_map, x, y, not map[x][y].block_sight, not map[x][y].blocked)
 
 
fov_recompute = True
game_state = 'playing'
player_action = None

# A warm, welcoming message!
message('Welcome stranger! Prepare to perish in the Tombs of the Ancient Dog Kings', libtcod.red)
 
while not libtcod.console_is_window_closed():
 
    #render the screen
    render_all()
 
    libtcod.console_flush()
 
    #erase all objects at their old locations, before they move
    for object in objects:
        object.clear()
 
    #handle keys and exit game if needed
    player_action = handle_keys()
    if player_action == 'exit':
        break

    # Let the monsters take their turn
    if game_state == 'playing' and player_action != 'didnt-take-turn':
    	for object in objects:
    		if object.ai:
    			object.ai.take_turn()