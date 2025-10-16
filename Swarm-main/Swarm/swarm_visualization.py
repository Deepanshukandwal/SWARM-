import matplotlib.pyplot as plt
import matplotlib.animation as animation
import matplotlib.patheffects as path_effects
from matplotlib.patches import RegularPolygon, Circle
from matplotlib.lines import Line2D
from swarm_core import friendly_drones, enemy_drones, DETECTION_RANGE, FIRING_RANGE, ARENA_SIZE
import numpy as np
import random

def run_animation():
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(0, ARENA_SIZE)
    ax.set_ylim(0, ARENA_SIZE)
    ax.set_facecolor("#08121F")
    ax.set_xticks(np.arange(0, ARENA_SIZE + 1, 50))
    ax.set_yticks(np.arange(0, ARENA_SIZE + 1, 50))
    ax.grid(True, color="#00E5FF", linestyle='-', linewidth=0.5, alpha=0.25)
    for line in ax.get_xgridlines() + ax.get_ygridlines():
        line.set_path_effects([path_effects.Stroke(linewidth=1.5, foreground="#00FFFF", alpha=0.3),
                               path_effects.Normal()])
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    for spine in ax.spines.values():
        spine.set_edgecolor("#00E5FF")
        spine.set_linewidth(1.2)
        spine.set_alpha(0.5)

    base_positions = [(100, 40), (250, 40), (400, 40)]
    base_glows = []
    for (x, y) in base_positions:
        glow = Circle((x, y), radius=35, color="#00E5FF", alpha=0.07, zorder=1)
        ax.add_patch(glow)
        base_glows.append(glow)
        hex_base = RegularPolygon((x, y), 6, radius=25, orientation=np.pi/6,
                                  facecolor="#5C5C5C", edgecolor="#00FFFF", lw=1.2, zorder=2)
        ax.add_patch(hex_base)
        center_glow = Circle((x, y), radius=9, color="#00FFFF", alpha=0.3, zorder=3)
        ax.add_patch(center_glow)
        ax.text(x, y - 28, "BASE", color="#00FFFF", ha="center", va="center",
                fontsize=9, fontweight="bold", zorder=4)

    friendly_scatter = ax.scatter([], [], c="lime", s=80, edgecolors="black", zorder=4)
    enemy_scatter = ax.scatter([], [], c="red", s=80, edgecolors="black", alpha=0.9, zorder=4)

    # ✅ Custom legend matching your image
    legend_handles = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='lime', markeredgecolor='black',
               markersize=10, markeredgewidth=1.2, linestyle=''),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markeredgecolor='black',
               markersize=10, markeredgewidth=1.2, linestyle='')
    ]
    legend_labels = ["Friendly Drones", "Enemy Drones"]
    legend = ax.legend(handles=legend_handles, labels=legend_labels,
                       loc="upper right", facecolor="#0B1622", edgecolor="#00FFFF",
                       labelcolor="#00FFFF", fontsize=9, frameon=True,
                       handlelength=1.2, handletextpad=0.6)
    for text in legend.get_texts():
        text.set_fontweight('bold')
    legend.get_frame().set_alpha(0.9)

    detection_circles = []
    explosions = []
    targets_lines = []
    kills = 0

    def update(frame):
        nonlocal kills
        xs_friend, ys_friend, xs_enemy, ys_enemy = [], [], [], []
        pulse = 0.1 + 0.05 * np.sin(frame / 5)
        for glow in base_glows:
            glow.set_alpha(pulse)
        for c in detection_circles:
            c.remove()
        detection_circles.clear()
        for line in targets_lines:
            line.remove()
        targets_lines.clear()
        for e in explosions[:]:
            new_alpha = max(0, e.get_alpha() - 0.05)
            e.set_alpha(new_alpha)
            e.set_radius(e.get_radius() * 1.05)
            if new_alpha <= 0:
                e.remove()
                explosions.remove(e)

        live_enemies = [e for e in enemy_drones if e.alive]
        for drone in friendly_drones:
            target = None
            for enemy in live_enemies:
                dist = np.hypot(enemy.x - drone.x, enemy.y - drone.y)
                if dist <= DETECTION_RANGE:
                    target = enemy
                    break
            drone.move(target)
            aura = Circle((drone.x, drone.y), DETECTION_RANGE / 2, color="#00E5FF", alpha=0.08, zorder=1)
            ax.add_patch(aura)
            detection_circles.append(aura)
            if target:
                line, = ax.plot([drone.x, target.x], [drone.y, target.y],
                                color="#00FFFF", linewidth=1, alpha=0.6, zorder=2)
                targets_lines.append(line)
            if target and np.hypot(target.x - drone.x, target.y - drone.y) <= FIRING_RANGE[1]:
                target.alive = False
                target.explosion_timer = 10
                kills += 1
                exp = Circle((target.x, target.y), 10, color="orange", alpha=0.9)
                ax.add_patch(exp)
                explosions.append(exp)
            xs_friend.append(drone.x)
            ys_friend.append(drone.y)

        for enemy in enemy_drones:
            if enemy.alive:
                enemy.move()
                xs_enemy.append(enemy.x)
                ys_enemy.append(enemy.y)
            elif enemy.explosion_timer > 0:
                enemy.explosion_timer -= 1
                exp = Circle((enemy.x, enemy.y), 10 + random.uniform(-2, 5),
                             color=random.choice(["orange", "yellow", "red"]),
                             alpha=enemy.explosion_timer / 10)
                ax.add_patch(exp)
                explosions.append(exp)

        friendly_scatter.set_offsets(np.c_[xs_friend, ys_friend])
        enemy_scatter.set_offsets(np.c_[xs_enemy, ys_enemy])
        ax.set_title(f"Radar Visualization | Frame: {frame} | Kills: {kills}",
                     color="#00FFFF", fontsize=12)
        return friendly_scatter, enemy_scatter, *detection_circles, *explosions, *targets_lines

    ani = animation.FuncAnimation(fig, update, frames=500, interval=100, blit=False, repeat=False)
    plt.show()
