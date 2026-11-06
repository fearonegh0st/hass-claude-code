"""Parametric Christmas tree for the Grand Parlor 3D model (Blender 5.1).

Builds a low-poly tree (trunk, stand, 4 tiers, star, ornaments) as one
object named "furn.xmas_tree" and places it in the south-east corner of the
Grand Parlor. Meant to be run inside the scene that holds
living_room_v3.glb, then exported as living_room_v4.glb.

Units: this model is in METRES (it matches the room GLB, where the parlor
is about 8.2 x 4.3 m). This is a 3D-floorplan asset, not a print, so the
usual 1 BU = 1 mm print convention does not apply here.

Position: glTF is Y-up, Blender is Z-up. The dashboard's card coordinates
(x, y, z) map to Blender (x, -z, y). The SE corner in card coordinates is
about (7.6, 0, 9.0), so the default location below is Blender (7.6, -9.0, 0).
Adjust TREE_LOCATION if it lands in furniture.

How to run:
  1. Blender 5.1: File > Import > glTF 2.0 > living_room_v3.glb
     (from \\homeassistant\\config\\www\\manor3d\\room3d\\rooms_v1\\)
  2. Scripting workspace > Open this file > Run Script.
  3. Check the tree in the SE corner. Change the parameters below and run
     again if needed; the script replaces its own previous tree.
  4. File > Export > glTF 2.0 as living_room_v4.glb (do NOT overwrite v3),
     same folder. Format: glTF Binary; include: Selected Objects off,
     Custom Properties on.
  5. Tell Claude: the dashboard card then gets model .../living_room_v4.glb
     and an object {"node": "furn.xmas_tree", "kind": "lamp", ...}.
"""

import math

import bpy
import bmesh

# ---------------- parameters (metres) ----------------
TREE_NAME = "furn.xmas_tree"
TREE_LOCATION = (7.6, -9.0, 0.0)  # Blender coords (x, y, z), floor at z=0
TREE_HEIGHT = 2.10                # stand to star tip, ~7 ft
BASE_RADIUS = 0.62                # widest tier radius
TIERS = 4
TIER_OVERLAP = 0.35               # fraction each tier overlaps the one below
TRUNK_RADIUS = 0.06
TRUNK_HEIGHT = 0.22
STAND_RADIUS = 0.28
STAND_HEIGHT = 0.10
STAR_SIZE = 0.12
ORNAMENTS_PER_TIER = 7
ORNAMENT_RADIUS = 0.035
SEGMENTS = 12                     # low poly keeps the dashboard GLB light
# ------------------------------------------------------


def _material(name, rgb, emission=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.6
    if emission > 0:
        bsdf.inputs["Emission Color"].default_value = (*rgb, 1.0)
        bsdf.inputs["Emission Strength"].default_value = emission
    return mat


def _assign(bm, faces, mat_index):
    for f in faces:
        f.material_index = mat_index


def build_tree():
    # Replace an earlier run.
    old = bpy.data.objects.get(TREE_NAME)
    if old is not None:
        bpy.data.objects.remove(old, do_unlink=True)
    old_mesh = bpy.data.meshes.get(TREE_NAME)
    if old_mesh is not None and old_mesh.users == 0:
        bpy.data.meshes.remove(old_mesh)

    mats = [
        _material("xmas_needles", (0.05, 0.28, 0.10)),
        _material("xmas_trunk", (0.25, 0.14, 0.06)),
        _material("xmas_stand", (0.08, 0.08, 0.09)),
        _material("xmas_star", (1.0, 0.84, 0.0), emission=4.0),       # Bat yellow
        _material("xmas_orn_red", (0.85, 0.05, 0.05), emission=1.5),
        _material("xmas_orn_gold", (1.0, 0.65, 0.1), emission=1.5),
        _material("xmas_orn_blue", (0.1, 0.35, 1.0), emission=1.5),
    ]

    bm = bmesh.new()

    # Stand and trunk.
    r = bmesh.ops.create_cone(bm, cap_ends=True, segments=SEGMENTS,
                              radius1=STAND_RADIUS, radius2=STAND_RADIUS * 0.85,
                              depth=STAND_HEIGHT)
    bmesh.ops.translate(bm, verts=r["verts"], vec=(0, 0, STAND_HEIGHT / 2))
    _assign(bm, {f for v in r["verts"] for f in v.link_faces}, 2)

    r = bmesh.ops.create_cone(bm, cap_ends=True, segments=8,
                              radius1=TRUNK_RADIUS, radius2=TRUNK_RADIUS,
                              depth=TRUNK_HEIGHT)
    bmesh.ops.translate(bm, verts=r["verts"],
                        vec=(0, 0, STAND_HEIGHT + TRUNK_HEIGHT / 2))
    _assign(bm, {f for v in r["verts"] for f in v.link_faces}, 1)

    # Needle tiers: stacked cones, each narrower, overlapping.
    foliage_bottom = STAND_HEIGHT + TRUNK_HEIGHT * 0.8
    foliage_height = TREE_HEIGHT - foliage_bottom - STAR_SIZE
    tier_h = foliage_height / (TIERS - (TIERS - 1) * TIER_OVERLAP)
    tier_info = []
    for i in range(TIERS):
        z0 = foliage_bottom + i * tier_h * (1 - TIER_OVERLAP)
        rad = BASE_RADIUS * (1 - i / (TIERS + 0.6))
        r = bmesh.ops.create_cone(bm, cap_ends=True, segments=SEGMENTS,
                                  radius1=rad, radius2=0.0, depth=tier_h)
        bmesh.ops.translate(bm, verts=r["verts"], vec=(0, 0, z0 + tier_h / 2))
        _assign(bm, {f for v in r["verts"] for f in v.link_faces}, 0)
        tier_info.append((z0, rad))

    # Ornaments around the lower edge of each tier.
    orn_mats = [4, 5, 6]
    k = 0
    for i, (z0, rad) in enumerate(tier_info):
        n = max(3, ORNAMENTS_PER_TIER - i)
        for j in range(n):
            a = 2 * math.pi * (j + 0.5 * (i % 2)) / n
            pos = (math.cos(a) * rad * 0.92, math.sin(a) * rad * 0.92, z0 + 0.06)
            r = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=ORNAMENT_RADIUS)
            bmesh.ops.translate(bm, verts=r["verts"], vec=pos)
            _assign(bm, {f for v in r["verts"] for f in v.link_faces}, orn_mats[k % 3])
            k += 1

    # Star: a flat five-point star facing south (toward the room camera).
    star_z = TREE_HEIGHT - STAR_SIZE * 0.6
    verts = []
    for p in range(10):
        ang = math.pi / 2 + p * math.pi / 5
        rr = STAR_SIZE * (1.0 if p % 2 == 0 else 0.42)
        verts.append(bm.verts.new((math.cos(ang) * rr, 0.0, star_z + math.sin(ang) * rr)))
    center_f = bm.verts.new((0.0, -0.02, star_z))
    center_b = bm.verts.new((0.0, 0.02, star_z))
    for p in range(10):
        a, b = verts[p], verts[(p + 1) % 10]
        for c in (center_f, center_b):
            f = bm.faces.new((a, b, c) if c is center_f else (b, a, c))
            f.material_index = 3

    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)

    mesh = bpy.data.meshes.new(TREE_NAME)
    bm.to_mesh(mesh)
    bm.free()
    for m in mats:
        mesh.materials.append(m)

    obj = bpy.data.objects.new(TREE_NAME, mesh)
    obj.location = TREE_LOCATION
    obj["ha_entity"] = "light.living_room_living_room_christmas_tree"
    bpy.context.scene.collection.objects.link(obj)

    # Report size so it can be checked against the room with numbers.
    dims = obj.dimensions
    print(f"{TREE_NAME}: {dims.x:.2f} x {dims.y:.2f} x {dims.z:.2f} m at {tuple(obj.location)}")
    return obj


if __name__ == "__main__":
    build_tree()
