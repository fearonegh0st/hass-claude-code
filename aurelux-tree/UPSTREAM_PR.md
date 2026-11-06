# Upstream pull request: 8none1/lednetwf_ble

Open: https://github.com/8none1/lednetwf_ble/compare/main...fearonegh0st:lednetwf_ble:aurelux-hc3-scenes?expand=1

Title:
Add hc3 built-in scenes (0xE1 0x21) for product 197 (Aurelux Christmas tree)

Body (paste everything below the line):

---

## Summary

Adds support for the built-in scenes of product **197 (0x00C5)**, an hc3 "carrier wave symphony" controller sold as the **Aurelux** smart Christmas tree (BLE name `IOTBT525`, service data under UUID `0x5A02`, firmware 78).

On v2.0.1-beta20 this device:
- follows the v3 colour command (`0xE0 0x01`) but auto-detects as *segment*, so colour only works with the protocol override set to v3;
- ignores every effect command the integration sends (`0xE1 0x01` segment scenes, `0xE0 0x02` Telink / `scene_data_v3`).

The vendor device database (briturn_core `zg_device_db`, v27) lists product 197 as family `wifibleCarrierWaveSymphony`, category `hc3`, with `colour_data_v3` / `switch_led_v3` and **no** `scene_data_v3`; its scene function is `symphony_scene_hc3`.

## The scene command

Recovered from the vendor app's compiled Dart code (`app_common_command_lib/voice_control_ii/builder.dart::buildCustomModeHEXCommand`, used by the "Symphony Carrier" control page):

```
E1 21 preview brightness type otherMode direction density speed rotate
      bg[hs_hi hs_lo v cct cctV]
      count  count x [hs_hi hs_lo v cct cctV]
```

- `hs` = `(hue << 7) | saturation`, the same packing as `pack_hue_saturation` / the 0x3B and v3 colour commands
- brightness, density, speed, v, cct, cctV: 0-100; at most 8 colours; no checksum
- sent with `cmd_family 0x0B`

Scene definitions (animation type, speed, density, direction, colour list) come from the app's built-in preset table (`voice_control_ii_cycle_default_data.dart`), with the Chinese preset names translated to English. 39 unique presets.

## Changes

- `hc3_scenes.py` (new): scene table plus `build_hc3_scene_payload()`
- `device.py`: for products in `HC3_SCENE_PRODUCT_IDS` (197), `effect_list` returns the scene names, `has_effects` is True, and `set_effect` sends `0xE1 0x21`. The effect speed number re-sends the scene through the existing `set_effect_speed` path.
- `const.py`: add 197 to `IOTBT_V3_PRODUCT_IDS`, so colour works without the manual override
- `manifest.json`: version bump (feel free to drop or replace it)

## Testing

Tested on a real Aurelux tree (product 197) on HA 2026.11:
- the effect list shows the 39 scenes
- "Fireworks Celebration" and "Christmas 2" each play a distinct multi-colour animation
- effect speed 10 is visibly slower, 100 visibly faster
- solid RGB colour works after running a scene, with no protocol override

Not covered: reading the active scene back from the device (the entity tracks the scene HA last sent), and the music / `p3_random_colorful` functions.
