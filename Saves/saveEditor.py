import pygame
import sys
import random
import os

map_width = 1056 // 32
map_height = 704 // 32

class MapEditor:
    def __init__(self):
        self.grid = [[[0] for _ in range(map_width)] for _ in range(map_height)]
        self.selected_id = 1  # The object ID selected for placement
        self.respawn_point = None  # Initialize the respawn point

        self.texture_table = {
            0: "Resources/water.png",
            1: "Resources/grass.png",
            2: "Resources/stone.png",
            3: "Resources/bush.png",
            4: "Resources/iron_ore.png",
            5: 0,
            6: 0,
            7: 0,
            9: None
        }

        self.object_table = {
            0: "water",
            1: "grass",
            2: "stone",
            3: "bush",
            4: "iron_ore",
            5: "coal_ore",
            6: "table",
            7: "furnace",
        }

    def draw(self, screen):
        for jdx, row in enumerate(self.grid):
            for idx, cell in enumerate(row):
                object_id = cell[-1]
                object_texture = self.texture_table.get(object_id)
                if object_texture:
                    texture = pygame.transform.scale(pygame.image.load(object_texture), (32, 32))
                    screen.blit(texture, (idx * 32, jdx * 32))
                elif object_id == 9:  # Draw respawn point as a distinct color
                    pygame.draw.rect(screen, (0, 255, 0), (idx * 32, jdx * 32, 32, 32))
                    tsurf = pygame.Surface((32, 32), pygame.SRCALPHA)
                    tsurf.fill((0, 0, 0, len(cell) * 4))
                    screen.blit(tsurf, (idx * 32, jdx * 32))
                else:
                    pygame.draw.rect(screen, (255, 0, 255), (idx * 32, jdx * 32, 32, 32))
                    tsurf = pygame.Surface((32, 32), pygame.SRCALPHA)
                    tsurf.fill((0, 0, 0, len(cell) * 4))
                    screen.blit(tsurf, (idx * 32, jdx * 32))

    def place(self, object_id, coord):
        if object_id == 9:
            # Clear the previous respawn point
            if self.respawn_point:
                x, y = self.respawn_point
                self.grid[y][x] = [self.grid[y][x][0]]  # Keep the bottommost layer (e.g., grass)
            self.respawn_point = coord
        x, y = coord
        self.grid[y][x].append(object_id)

    def remove(self, coord):
        x, y = coord
        if len(self.grid[y][x]) > 1:
            self.grid[y][x].pop()

def save_map_to_file(map_data, respawn_point, filename):
    with open(filename, "w") as file:
        for y, row in enumerate(map_data):
            for x, cell in enumerate(row):
                if cell != [0]:
                    content = " ".join(str(id) for id in cell if id != 0 and id != 9)
                    if content:  # Only write if there's something other than water
                        file.write(f"{x} {y} {content}\n")
        # Add player position and respawn point at the end
        player_pos = respawn_point if respawn_point else (0, 0)
        file.write(f"{player_pos[0]} {player_pos[1]} {player_pos[0]} {player_pos[1]}")

def main():
    pygame.init()
    screen = pygame.display.set_mode((1056, 704))
    clock = pygame.time.Clock()
    map_editor = MapEditor()
    running = True
    font = pygame.font.Font(None, 32)  # Initialize font

    while running:
        screen.fill((0, 0, 0))
        map_editor.draw(screen)
        
        # Display the selected object ID
        selected_id_surf = font.render(f"Selected ID: {map_editor.selected_id}", True, (255, 255, 255))
        screen.blit(selected_id_surf, (10, 10))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                # Inside the main loop, where the 's' key event is handled
                if event.key == pygame.K_s:  # Save the map
                    filename = f"save_{random.randint(1000, 9999)}.ols"
                    save_map_to_file(map_editor.grid, map_editor.respawn_point, os.path.join('Saves', filename))
                    print(f"Map saved as {filename}")

                # Change the selected ID with number keys
                if pygame.K_1 <= event.key <= pygame.K_9:
                    map_editor.selected_id = event.key - pygame.K_1 + 1

            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                coord = mx // 32, my // 32
                if event.button == 1:  # Left mouse button
                    map_editor.place(map_editor.selected_id, coord)
                elif event.button == 3:  # Right mouse button
                    map_editor.remove(coord)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

    pygame.quit()

if __name__ == "__main__":
    main()