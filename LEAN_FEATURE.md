# Lean feature (Soldier of Fortune protocol 33)

## Semantics

| `usercmd_t.lean` | Meaning |
|------------------|---------|
| `0` | Not leaning |
| `-1` | Lean **right** (view shifts along player right, roll toward right in open space) |
| `+1` | Lean **left** |

The field is a signed 8-bit value on the logical command; only `-1`, `0`, and `+1` are used.

On the server, lean affects view offset, roll, target-identification trace, lean “head” hit volume, stance animations, and duck rules (cannot stand while leaning).

## Input resolution

The retail client evaluates lean **once per user command**, after movement buttons are applied. Later rules override earlier ones.

1. **+use strafe lean**: If `+use` is active this frame (pressed or held), strafe while holding use can set lean without `+leanleft` / `+leanright`:
   - `+moveright` (held or edge) → `-1` (right)
   - `+moveleft` (held or edge) → `+1` (left)
   - If both apply in this block, **left wins** (second check overwrites).
2. **Dedicated lean keys** (override use-strafe):
   - `+leanright` → `-1`
   - `+leanleft` → `+1` (wins if both lean keys are held)

Dedicated keys match `+leanleft` / `+leanright` chat/GPT bindings in this project.

## Network encoding

Lean is **not** delta-coded against the previous command. Every command in the move bitstream always includes:

1. **1 bit** — `1` if `lean ≠ 0`, else `0`
2. **If bit 1 was `1`**: **1 bit** direction — `1` = negative (`-1`, right), `0` = positive (`+1`, left)

Order in the stream (after pitch/yaw/roll, moves, and delta-coded buttons): **lean (absolute) → delta lightlevel → msec (8 bits, always) → delta fire times**.

Equivalent wire logic:

```c
write_bit(lean != 0);
if (lean)
    write_bit(lean < 0);
```

## Bugs that were in sof-gpt

1. **Wrong lean values** — Code used `lean = 1` for right and `lean = 2` for left. On the wire, direction is `lean < 0`. With `lean = 1` (positive), the client sent **left** when the player pressed lean right. Left “worked” only because `2` is still positive and encodes as left.
2. **Delta-coded lean** — Packets only wrote lean bits when `deltato.lean != deltafrom.lean`. The server expects the **current** lean state every command; holding lean while other fields are unchanged must still transmit `lean ≠ 0`.
3. **Missing input rules** — No `+use` + strafe lean, and `+leanleft` did not override `+leanright` when both were held (`elif` instead of retail priority).

## Correct implementation in this repo

- `Player.resolve_lean()` — same priority and values as the retail client.
- `deltaUsercmd()` in `src/sof/packets/raw.py` — always writes absolute lean bits.

## Verification

- In-game: `+use` with `+moveright` / `+moveleft`; both `+leanright` and `+leanleft` held (left should win).
- Capture move packets while holding lean steady with no other input changes; lean-active bits should remain set every frame.
