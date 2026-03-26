import pygame
import json

pygame.init()
pygame.display.set_mode((1, 1))  # dummy window

surface = pygame.image.load("assets/track_data.png").convert()

waypoints = []
for y in range(surface.get_height()):
    for x in range(surface.get_width()):
        if surface.get_at((x, y))[:3] == (255, 255, 255):
            waypoints.append([x, y])

with open("track.json", "r") as f:
    track_data = json.load(f)
track_data["waypoints"] = waypoints
track_data["painted_w"] = surface.get_width()
track_data["painted_h"] = surface.get_height()
with open("track.json", "w") as f:
    json.dump(track_data, f, indent=2)

print(f"Extracted {len(waypoints)} waypoints -> track.json")
pygame.quit()
