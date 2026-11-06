# Aurelux tree (IOTBT525) - findings v2 (2026-11-06)

## Device
- BLE name IOTBT525, MAC 08:65:F0:66:C5:25, service-data UUID 0x5A02
- Service data 14 bytes: 5b 07 0865f066c525 00c5 4e 08 01 2e
  - product ID 0x00C5 = 197, BLE ver 7, firmware 78, LED ver 8
- HA entity: light.living_room_living_room_christmas_tree (LEDnetWF BLE v2.0.1-beta20)

## What works in HA (tested live, user confirmed)
- Protocol override "v3": on/off, colour (E0 01 ... 3B colour), brightness  -> WORKS
- Protocol "segment": colour E1 03 and effects E1 01 -> ignored (tree went purple)
- Protocol "telink": colour E2 0B and effects E0 02 00 id speed bright -> ignored

## APK (com.Juele.Aurelux 1.0.0 build 3) - device DB (ObjectBox/LMDB, briturn_core zg_device_db, DB version 27)
- Product 197: category "hc3", icon enum://dengdai, transport TCP_WF/BLE
- Family: wifibleCarrierWaveSymphony
- Protocols: common, common1_0, common2_0, symphonyE1, symphonyE4
- Functions: firmware_data, timer_data, state_upload, state_upload_v2, function_setting,
  function_inquiry, set_time, control_data, switch_led_v2, switch_led_v3, bright_value_v2,
  timer_data_v2, colour_data_v2, colour_data_v3, switch_led, get_time, get_timer_list,
  get_timer_list_v2, wake_up, wake_up_inquire, fall_asleep, fall_asleep_inquire,
  music_data_hc3, set_wiring_preview, microphone_V2, custom_68code, symphony_scene_hc3,
  p3_random_colorful, symphony_scene_alexa
- NO scene_data_v3 -> explains why E0 02 effects fail.
- Mode command = symphony_scene_hc3 (not in any public template JSON; built in Dart code).

## Open item
- Byte format of symphony_scene_hc3 / p3_random_colorful + the mode-name list must be read
  from the compiled Dart code (libapp.so, Dart snapshot ee1eb666c76a5cb7746faf39d0b97547).
  Needs a Dart AOT decompiler (blutter) - blocked pending user permission.

## Files (cloud scratchpad, ephemeral)
- APK: (cloud scratchpad) apk/aurelux.apk (sha256 6de6307b...f999)
- DB dump tool: (cloud scratchpad) tools/fb.py ; entity dumps (cloud scratchpad) apk/ent_*.txt
- libapp strings: (cloud scratchpad) apk/libapp.strings.txt

## RESOLVED (2026-11-06): built-in scenes working in Home Assistant

Decompiled the app (Blutter, Dart 3.3.3) and recovered the scene command used
by the tree's "Symphony Carrier" control page
(app_common_command_lib/voice_control_ii/builder.dart ::buildCustomModeHEXCommand):

    E1 21 preview brightness type otherMode direction density speed rotate
          bg[hs_hi hs_lo v cct cctV]  count  count x [hs_hi hs_lo v cct cctV]

hs = (hue << 7) | saturation (same packing as the v3 colour command).
Sent with transport cmd_family 0x0B. Presets come from
voice_control_ii_cycle_default_data.dart (see app_presets_voice_control_ii.json).

Integration: fork https://github.com/fearonegh0st/lednetwf_ble (main, a19d1cc),
= LEDnetWF BLE v2.0.1-beta20 + lednetwf_ble-hc3-scenes.patch + hacs.json without
zip_release. Installed in HA via Marketplace custom repository.

Tested live on the tree (user confirmed):
- Effect list shows 39 named scenes
- "Fireworks Celebration": multi-colour animation  -> OK
- "Christmas 2": different holiday pattern          -> OK
- Effect speed 10 -> slower, 100 -> faster          -> OK
- Solid blue after scenes                           -> OK
- v3 colour now automatic for product 197 (no protocol override needed)
