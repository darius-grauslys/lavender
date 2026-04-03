# System Overview: Collision Node Spatial Partitioning

## Purpose

The collision node system provides chunk-aligned spatial partitioning for
hitbox collision detection. Each loaded chunk (`Global_Space`) is associated
with a `Collision_Node` that tracks which hitboxes currently occupy that
chunk's spatial region. This allows the collision resolver to efficiently
narrow down collision candidates to only those hitboxes sharing the same
chunk.

## Architecture

### Data Hierarchy

