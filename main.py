import pygame
from ai import dumb_ai
import config
import racing_env.car as car_module
from utils import get_human_action
import json
import math
import os
from racing_env.start_line import find_start_line
from racing_env.lap_timer import LapTimer
from racing_env.telemetry import LapTelemetry
from hud import HUD
from scipy.ndimage import distance_transform_edt
from hmac_util import sign_lap

visual_mode = True
NUM_AI_CARS = 1
AI_COLORS = [
    (100, 160, 255),
    (255, 120, 120),
    (120, 255, 120),
]

pygame.init()
screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("rl-driver")
_rs = config.RENDER_SCALE
game_surface = pygame.Surface((config.WIDTH * _rs, config.HEIGHT * _rs))
clock = pygame.time.Clock()

# --- track state (globals reassigned by load_track) ---
world_w = world_h = 0
bg_color = (0, 0, 0)
scale_x = scale_y = 1.0
waypoints = []
signed_dist = None
track_img = None
lap_timer = None
car_spawn = None
start_angle = 0


def get_forward_normal(line_center, wps):
    nearest_idx = min(range(len(wps)), key=lambda i: line_center.distance_to(wps[i]))
    step = max(1, len(wps) // 20)
    prev_wp = wps[(nearest_idx - step) % len(wps)]
    next_wp = wps[(nearest_idx + step) % len(wps)]
    direction = next_wp - prev_wp
    if direction.length() > 0:
        direction = direction.normalize()
    return direction


def is_on_track(pos, margin=0):
    x, y = int(pos.x), int(pos.y)
    if not (0 <= x < world_w and 0 <= y < world_h):
        return False
    return signed_dist[x, y] > margin


def load_track(folder):
    global world_w, world_h, bg_color, scale_x, scale_y
    global waypoints, signed_dist, track_img, lap_timer, car_spawn, start_angle

    with open(f"{folder}/track.json") as f:
        data = json.load(f)

    world_w = data["world_w"]
    world_h = data["world_h"]

    _hex = data["background_color"].lstrip("#")
    bg_color = tuple(int(_hex[i:i + 2], 16) for i in (0, 2, 4))

    scale_x = world_w / data["painted_w"]
    scale_y = world_h / data["painted_h"]

    waypoints = [pygame.Vector2(p[0] * scale_x, p[1] * scale_y) for p in data["waypoints"]]

    mask = pygame.image.load(f"{folder}/track_mask.png").convert()
    mask = pygame.transform.scale(mask, (world_w, world_h))
    mask_arr = pygame.surfarray.array3d(mask)
    on_track = mask_arr[:, :, 0] == 0
    dist_in = distance_transform_edt(on_track)
    dist_out = distance_transform_edt(~on_track)
    signed_dist = dist_in - dist_out

    track_img = pygame.image.load(f"{folder}/bg.png").convert()
    track_img = pygame.transform.scale(track_img, (world_w * _rs, world_h * _rs))

    raw = find_start_line(f"{folder}/track_data.png")
    start_center = pygame.Vector2(raw.x * scale_x, raw.y * scale_y) if raw else None
    if start_center:
        forward_normal = get_forward_normal(start_center, waypoints)
        proximity = float(signed_dist[int(start_center.x), int(start_center.y)])
        lap_timer = LapTimer(start_center, forward_normal, proximity_threshold=proximity,
                             track_name=data.get("name", ""))
    else:
        lap_timer = None

    car_spawn = pygame.Vector2(data["spawn_x"] * scale_x, data["spawn_y"] * scale_y)
    start_angle = data["spawn_angle"]

    return data.get("name", folder)


def discover_tracks(root="tracks"):
    folders = []
    for entry in sorted(os.listdir(root)):
        path = os.path.join(root, entry)
        if os.path.isdir(path) and os.path.exists(os.path.join(path, "track.json")):
            folders.append(path)
    return folders


def screen_to_game(pos):
    sw, sh = screen.get_size()
    rs = config.RENDER_SCALE
    return (pos[0] * config.WIDTH * rs // sw, pos[1] * config.HEIGHT * rs // sh)


class Camera:
    def __init__(self):
        self.zoom = config.CAMERA_DEFAULTS["zoom"]
        self.follow = 1 if (world_w > config.WIDTH or world_h > config.HEIGHT) else 0


# --- initial load ---
TRACK_FOLDERS = discover_tracks()
current_track_idx = 1  # default to track2
load_track(TRACK_FOLDERS[current_track_idx])

hud = HUD()
hud.setup_switcher(TRACK_FOLDERS, current_track_idx)
telemetry = LapTelemetry()
prev_lap_count = 0
telemetry_accum = 0.0
TELEMETRY_INTERVAL = 1 / 60

camera = Camera()
cars = [car_module.Car(car_spawn.x, car_spawn.y, start_angle)]
for _i in range(NUM_AI_CARS):
    cars.append(car_module.Car(car_spawn.x, car_spawn.y, start_angle, team_color=AI_COLORS[_i % len(AI_COLORS)]))
car = cars[0]

running = True
paused = False
paused_mode = False
while running:
    if visual_mode:
        dt = clock.get_time() / 1000
    else:
        dt = 1 / 60

    clock.tick(config.FPS if visual_mode else 0)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if not visual_mode:
            continue

        if event.type == pygame.KEYDOWN:
            was_paused = paused

            if event.key == pygame.K_SPACE:
                paused_mode = not paused_mode

            if event.key == pygame.K_f:
                if camera.follow == 2:
                    camera.follow = 0
                else:
                    camera.follow += 1

            if event.key == pygame.K_r:
                for c in cars:
                    c.position = pygame.Vector2(car_spawn)
                    c.velocity = pygame.Vector2(0, 0)
                    c.angle = start_angle
                if lap_timer:
                    lap_timer.reset()
                paused_mode = False
                telemetry._current = []

            hud.handle_keydown(event.key, lap_timer=lap_timer)

            paused = paused_mode or hud.graph_open or hud.params_open or hud.switcher_open
            if lap_timer:
                if paused and not was_paused:
                    lap_timer.pause()
                elif not paused and was_paused:
                    lap_timer.unpause()

        if event.type == pygame.MOUSEBUTTONDOWN:
            was_paused = paused
            hud.handle_mousedown(screen_to_game(event.pos), car, camera)
            paused = paused_mode or hud.graph_open or hud.params_open or hud.switcher_open
            if lap_timer:
                if paused and not was_paused:
                    lap_timer.pause()
                elif not paused and was_paused:
                    lap_timer.unpause()
        if event.type == pygame.MOUSEMOTION:
            hud.handle_mousemotion(screen_to_game(event.pos))
        if event.type == pygame.MOUSEBUTTONUP:
            hud.handle_mouseup()
        if event.type == pygame.TEXTINPUT:
            hud.handle_textinput(event.text)
    # handle confirmed track switch
    if hud.switcher_confirmed:
        hud.switcher_confirmed = False
        current_track_idx = hud.switcher_idx
        load_track(TRACK_FOLDERS[current_track_idx])
        hud.setup_switcher(TRACK_FOLDERS, current_track_idx)
        cars = [car_module.Car(car_spawn.x, car_spawn.y, start_angle)]
        for _i in range(NUM_AI_CARS):
            cars.append(car_module.Car(car_spawn.x, car_spawn.y, start_angle, team_color=AI_COLORS[_i % len(AI_COLORS)]))
        car = cars[0]
        telemetry._current = []
        telemetry.laps = []
        prev_lap_count = 0
        telemetry_accum = 0.0
        camera.zoom = config.CAMERA_DEFAULTS["zoom"]
        camera.follow = 1 if (world_w > config.WIDTH or world_h > config.HEIGHT) else 0
        paused_mode = False
        paused = False

    game_surface.fill(bg_color)

    if visual_mode:
        keys = get_human_action(pygame.key.get_pressed())
    elif not visual_mode:
        keys = dumb_ai()

    blocked_by_line = False
    if not paused:
        for _ci, c in enumerate(cars):
            action = keys if _ci == 0 else dumb_ai()
            c.update(dt, action)
            if not is_on_track(c.position, c.track_margin):
                c.position -= c.velocity * dt
                c.velocity *= -c.bounce

        telemetry_accum += dt
        if lap_timer and lap_timer.state == "timing" and telemetry_accum >= TELEMETRY_INTERVAL:
            telemetry.record(car.velocity.length(), keys["up"], keys["brake"] or keys["down"])
        if telemetry_accum >= TELEMETRY_INTERVAL:
            telemetry_accum -= TELEMETRY_INTERVAL
        if lap_timer and len(lap_timer.laps) > prev_lap_count:
            is_official = all(
                getattr(car, k) == v for k, v in config.CAR_DEFAULTS.items()
            )
            lap_timer.signed_laps.append(
                sign_lap(lap_timer.track_name, lap_timer.laps[-1], official=is_official)
            )
            telemetry.finish_lap()
            prev_lap_count = len(lap_timer.laps)

        if lap_timer and lap_timer.state == "timing":
            if car.position.distance_to(lap_timer.center) < lap_timer.proximity * 2:
                backward_vel = car.velocity.dot(lap_timer.normal)
                if backward_vel > 0:
                    car.velocity -= lap_timer.normal * backward_vel
                    blocked_by_line = True

    # camera-aware track draw
    rs = config.RENDER_SCALE
    zoom = camera.zoom
    tw = int(world_w * zoom * rs)
    th = int(world_h * zoom * rs)

    scaled_track = pygame.transform.smoothscale(track_img, (tw, th))
    screen_width = config.WIDTH * rs
    screen_height = config.HEIGHT * rs
    if camera.follow > 0:
        blit_x = screen_width // 2 - int(car.position.x * zoom * rs)
        blit_y = screen_height // 2 - int(car.position.y * zoom * rs)
        rect = (blit_x, blit_y)
    else:
        blit_x = config.WIDTH * rs // 2 - tw // 2
        blit_y = config.HEIGHT * rs // 2 - th // 2
        rect = (blit_x, blit_y)
    if camera.follow == 2:
        screen_center = pygame.Vector2(screen_width // 2, screen_height // 2)
        track_center_world = pygame.Vector2(world_w // 2, world_h // 2)
        car_to_track_vector = (track_center_world - car.position) * zoom * rs
        rotated_vector = car_to_track_vector.rotate(car.angle)
        scaled_track = pygame.transform.rotozoom(scaled_track, -car.angle, 1)
        rect = scaled_track.get_rect(center=screen_center + rotated_vector)

    game_surface.blit(scaled_track, rect)

    if visual_mode:
        cars[0].draw(game_surface, camera, world_w, world_h)
        for c in cars[1:]:
            c.draw(game_surface, camera, world_w, world_h, cam_target=cars[0].position)

        if paused_mode:
            rs = config.RENDER_SCALE
            panel_w = config.WIDTH * rs
            panel_h = config.HEIGHT * rs
            surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            surf.fill((0, 0, 0, 200))
            game_surface.blit(surf, (0, 0))
            msg = hud.font.render("PAUSED", True, (255, 255, 255))
            game_surface.blit(msg, (panel_w // 2 - msg.get_width() // 2, panel_h - 42 * rs))

        if lap_timer:
            if not paused:
                lap_timer.update(car.position, car.velocity, dt)
            hud.draw(game_surface, car, lap_timer, telemetry, fps=clock.get_fps(), camera=camera, dt=dt)

        if blocked_by_line:
            rs = config.RENDER_SCALE
            panel_w = 500 * rs
            panel_h = 100 * rs
            cx = config.WIDTH * rs // 2
            cy = config.HEIGHT * rs // 2
            surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
            surf.fill((0, 0, 0, 220))
            game_surface.blit(surf, (cx - panel_w // 2, cy - panel_h // 2))
            msg = hud.font.render("can't go backwards past start line", True, (255, 0, 0))
            game_surface.blit(msg, (cx - msg.get_width() // 2, cy - msg.get_height() // 2))
    else:
        if lap_timer:
            lap_timer.update(car.position, car.velocity, dt)

    scaled = pygame.transform.smoothscale(game_surface, screen.get_size())
    screen.blit(scaled, (0, 0))
    pygame.display.flip()
pygame.quit()
