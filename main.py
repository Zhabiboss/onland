import pygame
import sys
import random
from tkinter import * 
import os
import math

map_width = 1056 // 32
map_height = 704 // 32
font = None

class LootTable:
    def __init__(self, drop_chances):
        """
        drop_chances: A dictionary where keys are item IDs and values are the drop probabilities (0.01 to 1).
        """
        self.drop_chances = drop_chances

    def generate_drop(self):
        """
        Returns a list of item IDs based on the defined probabilities.
        """
        return [item_id for item_id, chance in self.drop_chances.items() if random.random() < chance]

class Map:
    def __init__(self, app):
        self.app = app
        self.grid = [[[0] for i in range(map_width)] for j in range(map_height)]

        self.player_pos = ...

        self.object_table = {
            0: "water", 1: "grass", 2: "stone", 3: "bush",
            4: "iron_ore", 5: "coal_ore", 6: "table", 7: "furnace",
            8: "chest"
        }

        self.texture_table = {
            0: "Resources/water.png", 1: "Resources/grass.png", 2: "Resources/stone.png", 3: "Resources/bush.png",
            4: "Resources/iron_ore.png", 5: 0, 6: 0, 7: 0, 8: 0, 10: 0, 11: 0, 12: 0, 13: 0
        }

        self.item_table = {
            10: "stick", 11: "iron_ingot", 12: "coal", 13: "sword"
        }

        self.loot_table = {
            0: None, 1: LootTable({1: 1}), 2: LootTable({2: 1}), 3: LootTable({10: 0.9}), 4: LootTable({4: 1}),
            5: LootTable({5: 1}), 6: LootTable({6: 1}), 7: LootTable({7: 1}), 8: LootTable({8: 1}) 
        }

    def draw(self):
        for jdx, j in enumerate(self.grid):
            for idx, i in enumerate(j):
                try:
                    if self.texture_table[i[-1]] == 0:
                        pygame.draw.rect(self.app.screen, (255, 0, 255), (idx * 32, jdx * 32, 32, 32))
                        tsurf = pygame.Surface((32, 32), pygame.SRCALPHA)
                        tsurf.fill((0, 0, 0, len(i) * 4))
                        self.app.screen.blit(tsurf, (idx * 32, jdx * 32))
                    else:
                        self.app.screen.blit(pygame.transform.scale(pygame.image.load(self.texture_table[i[-1]]), (32, 32)), (idx * 32, jdx * 32))
                        tsurf = pygame.Surface((32, 32), pygame.SRCALPHA)
                        tsurf.fill((0, 0, 0, len(i) * 4))
                        self.app.screen.blit(tsurf, (idx * 32, jdx * 32))
                except:
                    continue

    def place(self, id: int, coord: tuple[int, int]):
        if id > len(self.object_table) - 1:
            return
        try:
            self.grid[coord[1]][coord[0]].append(id)
        except:
            return
        
    def remove(self, coord: tuple[int, int]):
        try:
            cell = self.grid[coord[1]][coord[0]]
            object_id = cell[-1]
            cell.remove(object_id)
        except:
            return
        
class Particle:
    def __init__(self, app, x, y, color, velocity):
        self.app = app
        self.x, self.y = x, y
        self.color = color
        self.vx, self.vy = velocity
        self.gx, self.gy = 0, 3

    def update(self):
        self.vx += self.gx
        self.vy += self.gy
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.95
        self.vy *= 0.95

        if self.y > self.app.height:
            self.app.particles.remove(self)

    def draw(self):
        pygame.draw.circle(self.app.screen, self.color, (self.x, self.y), 2)

class Hotbar:
    def __init__(self, app):
        self.app = app
        self.items = [(8, 999), None, None, None, None, None, None, None]
        self.selection = 1
        self.current_item = self.items[self.selection - 1]
        self.texture_table = self.app.map.texture_table
    
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_1]: self.selection = 1
        if keys[pygame.K_2]: self.selection = 2
        if keys[pygame.K_3]: self.selection = 3
        if keys[pygame.K_4]: self.selection = 4
        if keys[pygame.K_5]: self.selection = 5
        if keys[pygame.K_6]: self.selection = 6
        if keys[pygame.K_7]: self.selection = 7
        if keys[pygame.K_8]: self.selection = 8
        self.current_item = self.items[self.selection - 1]
    
    def draw(self):
        pygame.draw.rect(self.app.screen, (100, 60, 50), (0, 0, self.app.width, 52))
        pygame.draw.rect(self.app.screen, (255, 255, 255), (10 + (self.selection - 1) * 52 - 3, 7, 38, 38))
        for i in range(len(self.items)):
            try:
                if self.texture_table[self.items[i][0]] == 0:
                    pygame.draw.rect(self.app.screen, (255, 0, 255), (10 + i * 52, 10, 32, 32))
                    amount = self.items[i][1]
                    text = font.render(str(amount), True, (255, 255, 255))
                    self.app.screen.blit(text, ((10 + i * 52) + 16 - text.get_width() // 2, 21 - text.get_width() // 2))
                else:
                    self.app.screen.blit(pygame.transform.scale(pygame.image.load(self.texture_table[self.items[i][0]]), (32, 32)), (10 + i * 52, 10))
                    amount = self.items[i][1]
                    text = font.render(str(amount), True, (255, 255, 255))
                    self.app.screen.blit(text, ((10 + i * 52) + 16 - text.get_width() // 2, 21 - text.get_width() // 2))
            except:
                if self.items[i] == None:
                    pygame.draw.rect(self.app.screen, (50, 30, 25), (10 + i * 52, 10, 32, 32))
                    continue
                pygame.draw.rect(self.app.screen, (255, 0, 255), (10 + i * 52, 10, 32, 32))

class Player:
    def __init__(self, app):
        self.app = app
        self.x, self.y = self.app.player_pos
        self.respawn_x, self.respawn_y = self.app.respawn_pos  # Set from the Application
        self.speed = 2
        try:
            self.u1 = pygame.transform.scale(pygame.image.load("Resources/player_up_1.png"), (32, 32))
            self.u2 = pygame.transform.scale(pygame.image.load("Resources/player_up_2.png"), (32, 32))
            self.d1 = pygame.transform.scale(pygame.image.load("Resources/player_down_1.png"), (32, 32))
            self.d2 = pygame.transform.scale(pygame.image.load("Resources/player_down_2.png"), (32, 32))
            self.l1 = pygame.transform.scale(pygame.image.load("Resources/player_left_1.png"), (32, 32))
            self.l2 = pygame.transform.scale(pygame.image.load("Resources/player_left_2.png"), (32, 32))
            self.r1 = pygame.transform.scale(pygame.image.load("Resources/player_right_1.png"), (32, 32))
            self.r2 = pygame.transform.scale(pygame.image.load("Resources/player_right_2.png"), (32, 32))
        except:
            self.u1 = pygame.Surface((32, 32), pygame.SRCALPHA)
            self.u1.fill((255, 0, 255))
            self.u2 = pygame.Surface((32, 32), pygame.SRCALPHA)
            self.u2.fill((255, 0, 255))
            self.d1 = pygame.Surface((32, 32), pygame.SRCALPHA)
            self.d1.fill((255, 0, 255))
            self.d1 = pygame.Surface((32, 32), pygame.SRCALPHA)
            self.d1.fill((255, 0, 255))
            self.l1 = pygame.Surface((32, 32), pygame.SRCALPHA)
            self.l1.fill((255, 0, 255))
            self.l2 = pygame.Surface((32, 32), pygame.SRCALPHA)
            self.l2.fill((255, 0, 255))
            self.r1 = pygame.Surface((32, 32), pygame.SRCALPHA)
            self.r1.fill((255, 0, 255))
            self.r2 = pygame.Surface((32, 32), pygame.SRCALPHA)
            self.r2.fill((255, 0, 255))
        self.u = [self.u1, self.u2]
        self.d = [self.d1, self.d2]
        self.l = [self.l1, self.l2]
        self.r = [self.r1, self.r2]
        self.drs = [self.u, self.d, self.l, self.r]
        self.dr = 2
        self.tc = 1
    
    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.y -= self.speed * self.app.dt
            if self.tc == 1: self.tc = 2
            else: self.tc = 1
            self.dr = 1
        if keys[pygame.K_s]:
            self.y += self.speed * self.app.dt
            if self.tc == 1: self.tc = 2
            else: self.tc = 1
            self.dr = 2
        if keys[pygame.K_a]:
            self.x -= self.speed * self.app.dt
            if self.tc == 1: self.tc = 2
            else: self.tc = 1
            self.dr = 3
        if keys[pygame.K_d]:
            self.x += self.speed * self.app.dt
            if self.tc == 1: self.tc = 2
            else: self.tc = 1
            self.dr = 4

        if self.app.map.grid[int(self.y)][int(self.x)][-1] == 0:
            self.death_animation()
            self.x, self.y = self.app.respawn_pos

    def death_animation(self):
        for i in range(10):
            self.app.particles.append(Particle(self.app, self.x * 32, self.y * 32, (255, 0, 0), (random.randint(-5, 5), random.randint(-15, -10))))

    def draw(self):
        self.app.screen.blit(self.drs[self.dr - 1][self.tc - 1], (self.x * 32, self.y * 32))

class Container:
    def __init__(self, items: list[tuple[int, int]], coords: tuple[int, int]):
        self.items = items
        self.coords = coords

class Gameplay:
    def __init__(self, save):
        self.res = self.width, self.height = 1056, 704
        self.screen = pygame.display.set_mode(self.res)
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.dt = 1 / self.fps

        self.sounds = {
            "vine_boom": pygame.mixer.Sound("Resources/vine-boom.mp3")
        }

        self.map = Map(self)
        self.particles: list[Particle] = []

        # Initialize player and respawn positions
        self.player_pos = (0, 0)
        self.respawn_pos = (0, 0)

        self.hotbar = Hotbar(self)

        self.readSave(save)

        self.player = Player(self)
        self.player.x, self.player.y = self.player_pos

        self.containers: list[Container] = []

        self.save = save
        self.crafting = False

        pygame.display.set_caption("ONLAND")

    def readSave(self, name: str):
        with open(f"Saves/{name}.ols", "r") as file:
            lines = [line.strip() for line in file.readlines() if line.strip()]

        # Check if there are enough lines to include a map and player positions
        if len(lines) < 2:
            print("Save file is not in the correct format or is incomplete.")
            sys.exit()

        # Load the map grid
        for line in lines[:-2]:  # Exclude the last line which has player data
            cells = line.split(" ")
            x, y = int(cells[0]), int(cells[1])
            # Clear the cell before appending new objects
            self.map.grid[y][x] = []
            # Append all objects from the save file to the cell
            for obj_id in cells[2:]:
                self.map.grid[y][x].append(int(obj_id))

        # Extract player and respawn positions from the last line
        player_data = lines[-2].split(" ")
        if len(player_data) != 4:
            print("The last line in the save file does not contain exactly four integers for player and respawn positions.")
            sys.exit()

        self.player_pos = (int(player_data[0]), int(player_data[1]))
        self.respawn_pos = (int(player_data[2]), int(player_data[3]))
        hotbar_data = lines[-1]
        hotbar_items = hotbar_data.split(' ')
        #self.hotbar.items = [(int(hotbar_items[i]), int(hotbar_items[i + 1])) for i in range(0, len(hotbar_items), 2)]
        self.hotbar.items = []
        for i in range(0, len(hotbar_items), 2):
            if (int(hotbar_items[i]), int(hotbar_items[i + 1])) == (0, 0):
                self.hotbar.items.append(None)
            else:
                self.hotbar.items.append((int(hotbar_items[i]), int(hotbar_items[i + 1])))

        if len(self.hotbar.items) < 8:
            a = 8 - len(self.hotbar.items)
            for i in range(a):
                self.hotbar.items.append(None)

    def writeSave(self, name: str):
        with open(f"Saves/{name}.ols", "w") as file:
            for y, row in enumerate(self.map.grid):
                for x, cell in enumerate(row):
                    if cell != [0]:  # Check that the cell is not just water
                        # Write the cell's content, skipping the first element if it's 0
                        content = "0 " + " ".join(str(id) for id in cell if id != 0)
                        if content:  # Only write if there's something other than water
                            file.write(f"{x} {y} {content}\n")
            file.write(f"{int(self.player.x)} {int(self.player.y)} ")
            file.write(f"{int(self.player.respawn_x)} {int(self.player.respawn_y)}\n")
            hotbar_data = ""
            for item in self.hotbar.items:
                if item == None:
                    if hotbar_data == "":
                        hotbar_data += "0 0"
                    else:
                        hotbar_data += " 0 0"
                else:
                    if hotbar_data == "":
                        hotbar_data += f"{item[0]} {item[1]}"
                    else:
                        hotbar_data += f" {item[0]} {item[1]}"

            file.write(hotbar_data)
            file.close()

    def update(self):
        self.dt = 1 / self.clock.get_fps() if self.clock.get_fps() != 0 else 1 / self.fps
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.writeSave(self.save)
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if pygame.mouse.get_pressed()[0]:
                    mx, my = pygame.mouse.get_pos()
                    try:
                        slot = self.hotbar.items[self.hotbar.selection - 1]
                        if slot[0] not in self.map.item_table:
                            if pygame.key.get_pressed()[pygame.K_LSHIFT]:
                                for container in self.containers:
                                    if container.coords == (int(mx // 32), int(my // 32)):
                                        container.items.append(slot)
                                        self.hotbar.items[self.hotbar.selection - 1] = None
                            else:
                                self.map.place(slot[0], (int(mx // 32), int(my // 32)))
                                self.hotbar.items[self.hotbar.selection - 1] = list(self.hotbar.items[self.hotbar.selection - 1])
                                self.hotbar.items[self.hotbar.selection - 1][1] -= 1
                                self.hotbar.items[self.hotbar.selection - 1] = tuple(self.hotbar.items[self.hotbar.selection - 1])
                                if slot[0] == 8:
                                    self.containers.append(Container([], (int(mx // 32), int(my // 32))))
                                if self.hotbar.items[self.hotbar.selection - 1][1] == 0:
                                    self.hotbar.items[self.hotbar.selection - 1] = None
                        else:
                            for container in self.containers:
                                if container.coords == (int(mx // 32), int(my // 32)):
                                    container.items.append(slot)
                                    self.hotbar.items[self.hotbar.selection - 1] = None
                    except: pass
                if pygame.mouse.get_pressed()[2]:
                    mx, my = pygame.mouse.get_pos()
                    cell = self.map.grid[int(my // 32)][int(mx // 32)]
                    if cell and cell[-1] != 0:  # Make sure there is something to remove
                        id = cell[-1]  # Get the top item's ID before removal
                        self.map.remove((int(mx // 32), int(my // 32)))  # Now remove the item
                        if id == 8:
                            for container in self.containers:
                                if container.coords == (int(mx // 32), int(my // 32)):
                                    for item in container.items:
                                        placed = False
                                        # Check if the item is already in the hotbar
                                        for i, slot in enumerate(self.hotbar.items):
                                            if slot and slot[0] == item[0]:
                                                self.hotbar.items[i] = (item[0], slot[1] + item[1])  # Update the tuple in the list
                                                placed = True
                                                break
                                        # If the item is not in the hotbar, find an empty slot
                                        if not placed:
                                            for i, slot in enumerate(self.hotbar.items):
                                                if not slot:  # Empty slot found
                                                    self.hotbar.items[i] = (item[0], item[1])
                                                    break
                        if id != 0:  # Don't pick up water
                            # Generate drop items based on loot table
                            if id in self.map.loot_table:
                                drop_items = self.map.loot_table[id].generate_drop()
                                for id in drop_items:
                                    placed = False
                                    # Check if the item is already in the hotbar
                                    for i, slot in enumerate(self.hotbar.items):
                                        if slot and slot[0] == id:
                                            self.hotbar.items[i] = (id, slot[1] + 1)  # Update the tuple in the list
                                            placed = True
                                            break
                                    # If the item is not in the hotbar, find an empty slot
                                    if not placed:
                                        for i, slot in enumerate(self.hotbar.items):
                                            if not slot:  # Empty slot found
                                                self.hotbar.items[i] = (id, 1)
                                                break

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c: self.crafting = not self.crafting
                if event.key == pygame.K_e:
                    self.screen.fill("yellow")
                    for i in range(360):
                        self.particles.append(Particle(self, self.player.x * 32, self.player.y * 32, random.choice([(255, 0, 0), "yellow"]), (random.randint(6, 12) * math.cos(i), random.randint(12, 24) * math.sin(i))))
                    self.player.x, self.player.y = self.respawn_pos
                    pygame.mixer.Channel(1).play(self.sounds["vine_boom"])

        self.player.update()

        for p in self.particles:
            p.update()

        self.hotbar.update()
        
        pygame.display.update()
        self.clock.tick(self.fps)

    def draw(self):
        self.screen.fill((190, 190, 255))
        self.map.draw()
        self.player.draw()

        for p in self.particles:
            p.draw()

        self.hotbar.draw()

    def run(self):
        while True:
            self.draw()
            self.update()

root = Tk()
root["bg"] = "white"
root.title("Saves:")
root.geometry("750x550")
root.resizable(width = True, height = True)

selected_save = None
play = False
labelS = Label(root, text = "Selected: ")
labelS.grid(column = 0, row = 0)
for file in os.listdir("./Saves/"):
    if file.endswith(".ols"):
        name = file[:-4]
        def select(name):
            global selected_save
            selected_save = name
            labelS.config(text = f"Selected: {name}, press Play to open save")

        saveBtn = Button(root, text = name, command = (lambda: select(name)))
        saveBtn.grid(column = 0, row = os.listdir("./Saves/").index(file) + 1)

def play_():
    global play
    play = True
    root.destroy()
playBtn = Button(root, text = "Play", command = play_)
playBtn.grid(column = 0, row = 5)

root.mainloop()

if play:
    pygame.init()
    font = pygame.font.Font("freesansbold.ttf", 16)
    gp = Gameplay(selected_save)
    gp.run()