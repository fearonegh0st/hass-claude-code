# Handoff: add the Christmas tree to the Grand Parlor 3D model

For: Claude running on Batman-GamingDesktop (has Blender 5.1.2 and the PC's files).
From: the cloud session that built the tree, 2026-11-06. Owner: Jeremy "Gh0sT" Parson.

## Goal

Merge a ready-made low-poly Christmas tree into the Grand Parlor room model used by the
Home Assistant 3D dashboard cards, saved as a **new version** (`living_room_v4.glb`).
Then tell Jeremy it's done so the dashboard cards can be pointed at v4.

## Rules that apply (from Jeremy's standing preferences)

- **Never overwrite originals.** Do not touch `living_room_v3.glb`. Save `living_room_v4.glb`.
  Also keep a copy of v3 untouched (it already is; just don't save over it).
- Check with numbers, not screenshot loops. **One or two screenshots max.**
- Show the change in Blender before finishing (original vs new is fine as a quick view).
- At the start of the Blender session, check the open file isn't a temp autosave.
- Tell Jeremy exactly where files were saved, with full paths.
- Ask before deleting anything. Do not restart Home Assistant.
- This is a 3D-floorplan asset, **not a print**: units are **metres** to match the room GLB.
  The 1 BU = 1 mm print rule and the manifold check do not apply here.

## Files

Tree source (GitHub, public repo `fearonegh0st/hass-claude-code`,
branch `claude/aurelux-tree-home-assistant-q6snhc`, folder `aurelux-tree/blender/`):

- `xmas_tree_v1.py`: parametric Blender script that builds the tree (run this).
- `xmas_tree_v1.glb`: the tree on its own (reference only).
- `xmas_tree_v1_preview.png`: what it should look like.

Raw download URL for the script:
`https://raw.githubusercontent.com/fearonegh0st/hass-claude-code/claude/aurelux-tree-home-assistant-q6snhc/aurelux-tree/blender/xmas_tree_v1.py`

Room model (on Home Assistant, Samba share):
`\\homeassistant\config\www\manor3d\room3d\rooms_v1\living_room_v3.glb`
(served to the dashboard as `/local/manor3d/room3d/rooms_v1/living_room_v3.glb`).
If the share isn't mapped, Jeremy can map `\\homeassistant\config` (Samba add-on) or copy the
file over; ask him rather than guessing a path.

## Tree spec (already built by the script)

- Object name **`furn.xmas_tree`** (the dashboard card finds it by this exact node name).
- 1.24 m wide x 2.15 m tall (~7 ft); stand, trunk, 4 needle tiers, 25 red/gold/blue ornaments,
  emissive Bat-yellow star. 368 verts, ~50 KB. Custom property
  `ha_entity = light.living_room_living_room_christmas_tree`.
- Position: **south-east corner** of the parlor. Default Blender location `(7.6, -9.0, 0.0)`.

Coordinate notes (glTF is Y-up, Blender is Z-up; Blender `(x, y, z)` = card `(x, -z, y)`):

- Room centre in card coords is about x=4.11, z=7.35. The parlor spans roughly x 0.4 -> 8.0,
  z 5.2 (north / TV wall) -> 9.3 (south).
- West wall lamps are at card x=0.42, so **west = low x, east = high x; north = low z,
  south = high z**.
- SE corner in card coords ~ (7.6, 0, 9.0) -> Blender (7.6, -9.0, 0).

## Steps

1. Open Blender 5.1.2. Confirm you're not in a temp autosave. Start from an empty scene
   (File > New > General, delete the default cube/camera/light).
2. File > Import > glTF 2.0 > `living_room_v3.glb`.
3. Measure the room bounds with numbers: print the min/max X and Y (and the floor Z) of the
   imported floor/wall objects, so you can confirm where the SE corner really is.
4. Scripting workspace > Open `xmas_tree_v1.py` > Run Script. It prints the tree's size and
   location. If the corner from step 3 differs, edit `TREE_LOCATION` at the top and re-run
   (the script replaces its own previous tree). Keep ~0.15 m clearance from both walls
   (tree radius is 0.62 m, so centre ~0.8 m in from each wall), and make sure it doesn't
   intersect furniture in that corner (check bounding boxes numerically).
5. One screenshot from roughly the dashboard camera: position (4.11, 7.615, 12.396) looking at
   (4.11, 0.5, 7.347) in card/glTF coords, i.e. Blender camera at (4.11, -12.396, 7.615)
   aimed at (4.11, -7.347, 0.5). Show Jeremy.
6. File > Export > glTF 2.0: **glTF Binary (.glb)**, save as
   `\\homeassistant\config\www\manor3d\room3d\rooms_v1\living_room_v4.glb`.
   Include: all objects (not "Selected only"), Custom Properties ON, Apply Modifiers ON.
   Keep node names unchanged (the card also uses `furn.wall_flat_tv.001`,
   `furn.nest_hub_living_screen`, `furn.rosie_robot`, `furn.rosie_dock`,
   `furn.parlor_lamp_nw`, `furn.parlor_lamp_sw`).
7. Sanity check the export: re-import `living_room_v4.glb` into a fresh scene, confirm a node
   named exactly `furn.xmas_tree` exists and all the node names above still exist. Report the
   file size vs v3.
8. Report back to Jeremy: full path of v4, tree position used, any furniture moved/avoided,
   and the one screenshot.

## What happens after (for Jeremy / the Home Assistant session, not the PC session)

The dashboard edit is done from a session with the Home Assistant connection. Back up first
(each floorplan already has a hidden "Grand Parlor (backup 1106)" view). Then, in the Grand
Parlor `custom:manor-room3d-card` (dashboards `manor-lab` first, then `manor-floorplan` and
`manor-floorplan-phone`):

- change `model` to `/local/manor3d/room3d/rooms_v1/living_room_v4.glb?v=1`
- in `objects`, replace the temporary marker
  `{"pos": [7.6, 1.2, 9], "kind": "lamp", "entity": "light.living_room_living_room_christmas_tree", "label": "XMAS TREE"}`
  (currently only on `manor-lab`) with
  `{"node": "furn.xmas_tree", "kind": "lamp", "entity": "light.living_room_living_room_christmas_tree", "label": "XMAS TREE", "pos": [7.6, 1.2, 9.0]}`
  (keep `pos` matching the final tree location, in card coords, at about star/mid height).

## Context (already done, don't redo)

- The tree (Aurelux, BLE `IOTBT525`) is controlled in Home Assistant by a patched
  LEDnetWF BLE integration from `github.com/fearonegh0st/lednetwf_ble` (entity
  `light.living_room_living_room_christmas_tree`): colour, brightness, 39 app scenes, 5 palettes.
- Dashboard controls exist on Phone app > Living Room and both manor floorplans' Grand Parlor.
- Full write-up: `aurelux-tree/FINDINGS.md` in the same repo/branch.
