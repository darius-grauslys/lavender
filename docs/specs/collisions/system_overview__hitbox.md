# System Overview: Hitbox Management

## Purpose

The hitbox management system provides a type-erased, pooled allocation scheme
for collision primitives. It allows multiple hitbox manager types (e.g. AABB,
future AAABBB) to coexist under a single `Hitbox_Context`, each with its own
pool of hitboxes, while exposing a uniform opaque access interface for
cross-type operations.

## Architecture

### Data Hierarchy

