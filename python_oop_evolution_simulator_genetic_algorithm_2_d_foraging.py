#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Evolution Simulator — OOP + Genetic Algorithm (Python, single file)
------------------------------------------------------------------
A minimal but extensible evolution simulator for a 2D world where agents (creatures)
compete for food. After a fixed number of simulation steps, a GA selects and breeds
survivors into a new generation. Traits evolve over time (speed, sense radius,
metabolism), showing trade-offs between movement/foraging ability and energy cost.

✓ Pure Python standard library + optional matplotlib (for live visualization)
✓ Clear OOP structure: Genome, Creature, Food, Environment, EvolutionManager, Simulation
✓ Genetic operators: roulette selection, single-point crossover, gaussian mutation
✓ Reproducible runs (seed) and configurable parameters

Run (headless, no GUI):
    python evolution_sim.py --generations 10 --world 60 60 --pop 40 --steps 600

Run with visualization (requires matplotlib):
    python evolution_sim.py --viz --generations 20 --pop 60 --steps 600

Press Ctrl+C to stop the visualization.

Extension ideas (for your OOP final):
- Add predators and multiple species (inherit from Creature)
- Replace hand-coded policy with a small NN and evolve weights
- Replace GA with NEAT/ES or add local learning (RL) within a generation
- Implement sexual/asexual reproduction strategies as strategies (Strategy pattern)
- Add obstacles/terrain; change Food distribution model over time (Environment strategy)

Author: ChatGPT (OOP + DL/Evolution template)
License: MIT
"""
from __future__ import annotations

import argparse
import math
import random
import statistics
import sys
import time
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

# ==========================
# Utility & Configuration
# ==========================

Vec2 = Tuple[float, float]


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def dist(a: Vec2, b: Vec2) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


# ==========================
# Genome & Genetic Operators
# ==========================

@dataclass
class Genome:
    """Encodes heritable traits. Values are continuous within bounds.

    Traits:
        speed: max movement per step (costs energy via metabolism)
        sense: vision radius (costs a small sensing tax)
        metabolism: baseline energy cost per step
        greed: how aggressively to chase near food (0..1)
    """

    speed: float  # [0.5, 4.0]
    sense: float  # [5, 40]
    metabolism: float  # [0.02, 0.25]
    greed: float  # [0.0, 1.0]

    # Gene bounds for mutation/clamping
    BOUNDS = {
        "speed": (0.5, 4.0),
        "sense": (5.0, 40.0),
        "metabolism": (0.02, 0.25),
        "greed": (0.0, 1.0),
    }

    def clone(self) -> "Genome":
        return Genome(self.speed, self.sense, self.metabolism, self.greed)

    @staticmethod
    def random() -> "Genome":
        return Genome(
            speed=random.uniform(0.8, 3.2),
            sense=random.uniform(8, 25),
            metabolism=random.uniform(0.04, 0.16),
            greed=random.uniform(0.2, 0.9),
        )

    @staticmethod
    def crossover(a: "Genome", b: "Genome") -> "Genome":
        """Single-point crossover across the ordered list of genes."""
        genes_a = [a.speed, a.sense, a.metabolism, a.greed]
        genes_b = [b.speed, b.sense, b.metabolism, b.greed]
        point = random.randint(1, len(genes_a) - 1)
        child_genes = genes_a[:point] + genes_b[point:]
        return Genome(*child_genes)

    def mutate(self, rate: float = 0.2, sigma: float = 0.15) -> None:
        """Gaussian mutation with per-gene probability 'rate'."""
        for name in ["speed", "sense", "metabolism", "greed"]:
            if random.random() < rate:
                val = getattr(self, name)
                # proportional noise
                noise = random.gauss(0.0, sigma) * (val if val != 0 else 1.0)
                new_val = val + noise
                lo, hi = self.BOUNDS[name]
                setattr(self, name, clamp(new_val, lo, hi))


# ==========================
# World Entities
# ==========================

@dataclass
class Food:
    pos: Vec2
    energy: float = 1.0


@dataclass
class Creature:
    genome: Genome
    pos: Vec2
    energy: float = 5.0
    age: int = 0
    alive: bool = True
    id: int = field(default_factory=lambda: random.randint(1000, 999999))

    def step(self, env: "Environment") -> None:
        if not self.alive:
            return

        self.age += 1

        # Sense nearest food within radius
        target = self._nearest_food(env)

        # Movement: greedy chase if seen; else random walk
        if target is not None:
            tx, ty = target.pos
            dx, dy = tx - self.pos[0], ty - self.pos[1]
            d = math.hypot(dx, dy) + 1e-8
            # greed scales step toward the target
            step_len = self.genome.speed * (0.6 + 0.4 * self.genome.greed)
            move = (step_len * dx / d, step_len * dy / d)
        else:
            # correlated random walk
            theta = random.uniform(0, 2 * math.pi)
            step_len = self.genome.speed * random.uniform(0.4, 1.0)
            move = (step_len * math.cos(theta), step_len * math.sin(theta))

        # Update position with toroidal wrapping
        nx = (self.pos[0] + move[0]) % env.width
        ny = (self.pos[1] + move[1]) % env.height
        self.pos = (nx, ny)

        # Energy accounting
        # Movement cost ~ speed^2 (drag) + sensing tax + metabolism
        move_cost = 0.01 * (step_len ** 2)
        sense_cost = 0.001 * (self.genome.sense / 10.0)
        self.energy -= (self.genome.metabolism + move_cost + sense_cost)

        # Eat if on food (within small radius)
        if target is not None and dist(self.pos, target.pos) < 1.5:
            self.energy += target.energy
            env.remove_food(target)

        # Death check
        if self.energy <= 0:
            self.alive = False

    def fitness(self) -> float:
        # Survival time and surplus energy count; ensure non-negative
        return max(0.0, 0.6 * self.age + 2.0 * max(0.0, self.energy))

    def _nearest_food(self, env: "Environment") -> Optional[Food]:
        best = None
        best_d = self.genome.sense
        for f in env.foods:
            d = dist(self.pos, f.pos)
            if d <= best_d:
                best = f
                best_d = d
        return best


# ==========================
# Environment & Simulation
# ==========================

class Environment:
    def __init__(self, width: int, height: int, food_rate: int = 3, food_cap: int = 200):
        self.width = width
        self.height = height
        self.foods: List[Food] = []
        self.food_rate = food_rate  # foods spawned per step
        self.food_cap = food_cap

    def spawn_food(self) -> None:
        for _ in range(self.food_rate):
            if len(self.foods) >= self.food_cap:
                break
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            self.foods.append(Food((x, y), energy=random.uniform(0.8, 1.4)))

    def remove_food(self, f: Food) -> None:
        try:
            self.foods.remove(f)
        except ValueError:
            pass


class EvolutionManager:
    def __init__(self, mutation_rate: float = 0.2, mutation_sigma: float = 0.10):
        self.mutation_rate = mutation_rate
        self.mutation_sigma = mutation_sigma

    def next_generation(self, creatures: List[Creature], pop_size: int) -> List[Genome]:
        # Compute fitnesses
        fits = [c.fitness() for c in creatures]
        total_fit = sum(fits) + 1e-8
        if total_fit == 0:
            # all died early; reseed randomly
            return [Genome.random() for _ in range(pop_size)]

        # Roulette selection helper
        def select_parent() -> Genome:
            r = random.uniform(0, total_fit)
            acc = 0.0
            for c, f in zip(creatures, fits):
                acc += f
                if acc >= r:
                    return c.genome
            return creatures[-1].genome

        # Elitism: keep top-N genomes directly
        elite_n = max(1, pop_size // 10)
        elite = [c for c in sorted(creatures, key=lambda x: x.fitness(), reverse=True)][:elite_n]
        children: List[Genome] = [e.genome.clone() for e in elite]

        # Breed the rest
        while len(children) < pop_size:
            p1 = select_parent()
            p2 = select_parent()
            child = Genome.crossover(p1, p2)
            child.mutate(self.mutation_rate, self.mutation_sigma)
            children.append(child)

        return children[:pop_size]


class Simulation:
    def __init__(
        self,
        width: int = 80,
        height: int = 80,
        population: int = 50,
        steps_per_generation: int = 600,
        food_rate: int = 3,
        food_cap: int = 200,
        seed: int = 42,
    ):
        random.seed(seed)
        self.env = Environment(width, height, food_rate, food_cap)
        self.population = population
        self.steps_per_generation = steps_per_generation
        self.generation = 0
        self.creatures: List[Creature] = []
        self.evo = EvolutionManager()

        # Init population
        self.creatures = [
            Creature(
                genome=Genome.random(),
                pos=(random.uniform(0, width), random.uniform(0, height)),
                energy=random.uniform(4.0, 7.0),
            )
            for _ in range(population)
        ]

    def step(self) -> None:
        self.env.spawn_food()
        for c in self.creatures:
            c.step(self.env)

    def run_generation(self, verbose: bool = True) -> dict:
        for _ in range(self.steps_per_generation):
            self.step()

        # Stats
        fits = [c.fitness() for c in self.creatures]
        speeds = [c.genome.speed for c in self.creatures]
        senses = [c.genome.sense for c in self.creatures]
        metas = [c.genome.metabolism for c in self.creatures]
        greeds = [c.genome.greed for c in self.creatures]

        stats = {
            "gen": self.generation,
            "avg_fit": statistics.fmean(fits) if fits else 0.0,
            "max_fit": max(fits) if fits else 0.0,
            "avg_speed": statistics.fmean(speeds),
            "avg_sense": statistics.fmean(senses),
            "avg_meta": statistics.fmean(metas),
            "avg_greed": statistics.fmean(greeds),
            "survivors": sum(1 for c in self.creatures if c.alive),
            "food_left": len(self.env.foods),
        }
        if verbose:
            print(
                f"Gen {self.generation:3d} | fit avg/max: {stats['avg_fit']:.2f}/{stats['max_fit']:.2f} "
                f"| traits speed {stats['avg_speed']:.2f}, sense {stats['avg_sense']:.1f}, meta {stats['avg_meta']:.3f}, greed {stats['avg_greed']:.2f} "
                f"| survivors {stats['survivors']}")

        # Breed next generation
        next_genomes = self.evo.next_generation(self.creatures, self.population)
        # Reset world (optional: keep some food for continuity)
        self.env.foods.clear()

        # Create new creatures
        self.creatures = [
            Creature(genome=g.clone(), pos=(random.uniform(0, self.env.width), random.uniform(0, self.env.height)), energy=random.uniform(4.0, 7.0))
            for g in next_genomes
        ]
        self.generation += 1
        return stats

    # ============ Visualization ============
    def run_with_viz(self, generations: int = 20, fps: int = 60) -> None:
        try:
            import matplotlib.pyplot as plt
        except Exception:
            print("matplotlib not available; falling back to headless run.")
            self.run(generations)
            return

        plt.ion()
        fig, ax = plt.subplots(figsize=(6, 6))
        ax.set_xlim(0, self.env.width)
        ax.set_ylim(0, self.env.height)
        scat_creatures = ax.scatter([], [], s=25, marker='o', alpha=0.9, label='Creatures')
        scat_food = ax.scatter([], [], s=10, marker='x', alpha=0.6, label='Food')
        title = ax.set_title("Evolution Simulator")
        ax.legend(loc='upper right')

        steps = 0
        gen_steps = self.steps_per_generation
        gen_remaining = gen_steps
        target_dt = 1.0 / fps

        while self.generation < generations:
            t0 = time.time()
            self.step()
            steps += 1
            gen_remaining -= 1

            # Update plot every few frames for speed
            if steps % 2 == 0:
                cx = [c.pos[0] for c in self.creatures if c.alive]
                cy = [c.pos[1] for c in self.creatures if c.alive]
                fx = [f.pos[0] for f in self.env.foods]
                fy = [f.pos[1] for f in self.env.foods]
                scat_creatures.set_offsets(list(zip(cx, cy)))
                scat_food.set_offsets(list(zip(fx, fy)))
                title.set_text(f"Gen {self.generation} | creatures {len(self.creatures)} | food {len(self.env.foods)}")
                plt.pause(0.001)

            if gen_remaining <= 0:
                stats = self.run_generation(verbose=True)
                gen_remaining = gen_steps

            # crude frame cap
            dt = time.time() - t0
            if dt < target_dt:
                time.sleep(target_dt - dt)

        plt.ioff()
        plt.show(block=False)

    # ============ Headless run ============
    def run(self, generations: int = 20) -> None:
        for _ in range(generations):
            self.run_generation(verbose=True)


# ==========================
# CLI
# ==========================

def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="OOP Evolution Simulator (2D Foraging + GA)")
    p.add_argument("--world", nargs=2, type=int, default=[80, 80], help="world width height")
    p.add_argument("--pop", type=int, default=50, help="population size")
    p.add_argument("--steps", type=int, default=600, help="steps per generation")
    p.add_argument("--generations", type=int, default=20, help="number of generations")
    p.add_argument("--food-rate", type=int, default=3, help="food spawned per step")
    p.add_argument("--food-cap", type=int, default=200, help="max food items in world")
    p.add_argument("--seed", type=int, default=42, help="random seed")
    p.add_argument("--viz", action="store_true", help="enable matplotlib visualization")
    return p.parse_args(argv)


def main(argv: List[str]) -> None:
    args = parse_args(argv)
    sim = Simulation(
        width=args.world[0],
        height=args.world[1],
        population=args.pop,
        steps_per_generation=args.steps,
        food_rate=args.food_rate,
        food_cap=args.food_cap,
        seed=args.seed,
    )
    if args.viz:
        sim.run_with_viz(generations=args.generations)
    else:
        sim.run(generations=args.generations)


if __name__ == "__main__":
    main(sys.argv[1:])
