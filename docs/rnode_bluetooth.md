# RNode over Bluetooth (BLE)

Crosstalk can connect to an [RNode](https://github.com/markqvist/RNode_Firmware), including the Heltec LoRa 32 V3, without a USB cable. Messages travel from Crosstalk over Bluetooth to the RNode, then over LoRa to other Reticulum nodes.

## Connect an RNode

1. Disconnect the RNode's USB cable if it stops Bluetooth advertising.
2. Turn on Bluetooth at the RNode and put it in pairing mode.
3. Open **Interfaces → Add Interface** in Crosstalk.
4. Choose **RNode (LoRa Radio)** and set **Connection** to **Bluetooth (BLE)**.
5. Press **Scan for RNodes**.
6. Select the radio that appears and save the interface.
7. Enter the PIN shown on the RNode if the operating system asks for it.

Crosstalk saves the selected radio as a `ble://` target. On macOS that target is a CoreBluetooth UUID; on Windows or Linux it may be a Bluetooth address. You do not need to know either value before scanning.

## Heltec V3 pairing mode

The Heltec V3 uses the **PRG** button:

1. If the display is asleep, tap **PRG** once to wake it.
2. Use a short press to turn Bluetooth on. Confirm the Bluetooth icon appears.
3. Hold **PRG** for about six seconds, then release it before ten seconds.
4. Scan while the pairing PIN is visible.

Releasing after five seconds enters Bluetooth pairing. Holding for more than ten seconds starts the RNode WiFi console/AP instead. If that happens, press **RST** once and try again.

## Radio settings

Choose a regional preset as a starting point, or enter the exact frequency, bandwidth, spreading factor, coding rate, and transmit power used by your mesh. Every peer must use compatible LoRa settings. Presets are starting points, not legal advice or universal radio defaults.

## Troubleshooting

- Use USB or BLE, not both, while pairing and testing.
- Keep the pairing PIN visible until Crosstalk connects.
- If scanning finds nothing, re-enter pairing mode and scan again.
- On macOS, scan inside Crosstalk. The RNode may never appear in System Settings.
- If the interface stays disconnected, open **Diagnostics → Log Viewer** and search for `BLE` or `RNode`.
- Official desktop packages include the required `bleak` Bluetooth library.

USB serial and WiFi (`tcp://host`) remain available from the same RNode form.
