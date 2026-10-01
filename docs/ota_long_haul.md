# Use OTA Long Haul with Crosstalk

OTA Long Haul lets Crosstalk hand one short text message to a separate radio
program when normal Reticulum delivery is unavailable. The radio program lives
in the companion
[`reticulum-hf-bridge`](https://github.com/buildwithparallel/reticulum-hf-bridge)
repository.

The shortest useful explanation is:

- **Crosstalk is the messenger and control panel.** It owns conversations,
  contacts, the **Send over HF** switch, radio settings, Start/Stop controls,
  and status displays.
- **`reticulum-hf-bridge` is the radio implementation.** It contains the
  workers Crosstalk starts, the HF frame and modem, Hermes-Lite 2 control,
  RTL-SDR reception, and command-line test tools.
- **Hermes-Lite 2 transmits. RTL-SDR receives.** The current bridge does not
  receive through the Hermes. A complete radio hop needs both roles somewhere.
- **The HF part is public plaintext.** Reticulum encryption ends before the
  transmitter and a new encrypted LXMF message begins after reception.

```text
origin Crosstalk
    | encrypted LXMF to the local bridge
    v
Hermes Crosstalk + txbridge worker
    | public plaintext HF
    v
RTL-SDR + ingress worker
    | new encrypted LXMF message
    v
destination Crosstalk / Columba / other LXMF client
```

## Choose the role for this computer

| Choose in Bridge Extensions | Hardware | What this computer does | Can transmit? |
| --- | --- | --- | --- |
| **Hermes-Lite 2** | Hermes-Lite 2 on wired Ethernet and an appropriate antenna/filter | Receives an LXMF message from a Crosstalk island, converts it to the public HF frame, and keys one finite transmission | Yes, but only after explicit arming |
| **RTL-SDR** | RTL-SDR on USB and a receive antenna | Listens for the public HF frame, validates it, and creates a new LXMF message for the far network | No |

You may install both roles, but they are separate processes and hardware. Do
not run the RTL role and another SDR application against the same dongle.

## Install the radio software

Crosstalk packages do not contain the radio repository. Install it separately
on every computer that directly operates a Hermes or RTL-SDR:

```bash
git clone https://github.com/buildwithparallel/reticulum-hf-bridge.git
cd reticulum-hf-bridge
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-radio.txt
PYTHONPATH=src .venv/bin/python -m hfbridge.rnssetup
```

The last command creates the separate Reticulum configuration directories used
by the radio workers. The receive and transmit sections below show the two
interface blocks to review before starting either role.

For an RTL-SDR, install a system `librtlsdr` or use the repository's
`scripts/fetch-third-party.sh` build. The bridge README contains the current
platform and command-line details.

In Crosstalk, open **Bridge Extensions → OTA Long Haul**, choose the radio,
and set **Radio software folder** to the cloned repository root. It is the
directory containing both `src/hfbridge/` and `requirements-radio.txt`.

Examples:

```text
/home/alex/reticulum-hf-bridge
/Users/alex/Code/reticulum-hf-bridge
C:\Users\Alex\Code\reticulum-hf-bridge
```

Do not select `Crosstalk.app`, Crosstalk's installation directory, the Python
executable, or `src/hfbridge/`. The screen should change to **Software looks
ready** after saving a valid path. Crosstalk prefers the bridge repository's
`.venv` Python when it exists.

## Receive with an RTL-SDR

Use this on the far side of the HF hop.

1. Plug in the RTL-SDR and stop any other application using it.
2. Open **Bridge Extensions → OTA Long Haul → RTL-SDR**.
3. Enter the bridge repository root as **Radio software folder** and save it.
4. Pick a tuner gain. Start lower when the transmitter is nearby and raise it
   for weaker distant signals.
5. Make sure the ingress worker's Reticulum configuration can reach the
   destination's LXMF network, as described below.
6. Select **Start**. The page should say **Listening here**.

The counters mean:

- **Messages heard:** a valid HF frame passed FEC and CRC.
- **Forwarded:** ingress handed a reconstructed message to LXMF.
- **Could not decode:** a captured burst did not produce a valid frame.
- **Could not forward:** radio reception worked, but the far Reticulum path
  was unavailable.

The RTL worker is its own RNS process. Crosstalk's ordinary interfaces are not
automatically copied into it. Before relying on forwarding, configure
`rns-instances/ingress/config` inside the bridge repository with an interface
that can reach the destination network. A direct public-node example is:

```ini
[reticulum]
  enable_transport = No
  share_instance = No
  instance_name = hf-ingress
  shared_instance_port = 37505
  instance_control_port = 37506

[interfaces]
  [[Far Network]]
    type = TCPClientInterface
    interface_enabled = True
    target_host = YOUR_RNS_NODE
    target_port = YOUR_RNS_PORT
```

Use a node you operate or intentionally trust. The destination must be
reachable from that same interface. Start the RTL worker after editing the
file. **Forwarded** does not prove the recipient displayed the message; only
the destination application can confirm that.

## Transmit with a Hermes-Lite 2

Use this on the licensed transmitting side. Keep **Allow this computer to
transmit** off while setting up; the worker can run in dry-run mode without
opening a radio socket.

1. Connect the Hermes-Lite 2 and this computer to the same wired Ethernet
   network. Connect the correct antenna and filtering for the chosen band.
2. In the HF-station Crosstalk, add a **TCP Server** interface listening on
   `127.0.0.1:3742`. Keep this station island separate from the destination's
   normal Reticulum network.
3. Configure `rns-instances/txbridge/config` in the bridge repository as a TCP
   client to that station island:

   ```ini
   [reticulum]
     enable_transport = No
     share_instance = No
     instance_name = hf-txbridge
     shared_instance_port = 37503
     instance_control_port = 37504

   [interfaces]
     [[HF Station]]
       type = TCPClientInterface
       interface_enabled = True
       target_host = 127.0.0.1
       target_port = 3742
   ```

4. Open **Bridge Extensions → OTA Long Haul → Hermes-Lite 2**.
5. Set **Radio software folder** to the bridge repository root.
6. Enter the transmitting station's real callsign.
7. Select **Find radio**. Choose the discovered Hermes address. If no radio
   answers, fix the Ethernet route before continuing; the repository path is a
   separate setting.
8. Leave the working frequency at its documented default unless the control
   operator has selected another clear, permitted frequency. Begin with the
   lowest practical power for a bench test.
9. Select **Start** with transmit disabled. The status should read **Running
   here, transmit off**. Messages received in this state increment **Held** and
   do not key the radio.
10. After the operator has verified the station, enable **Allow this computer
    to transmit**, then Stop and Start so the armed setting takes effect.

The Hermes counters mean:

- **Messages received:** the bridge received a candidate LXMF message.
- **On the air:** the worker completed a radio transmission.
- **Held:** the bridge received the message while transmit was disabled.
- **Rejected:** the text, destination, or optional allow list rejected it.
- **Could not transmit:** radio setup or the UDP transmission failed.

If **Only let listed people use this station** is enabled, enter each permitted
sender's 32-character **LXMF delivery address**, not an identity hash. Stop and
Start after changing the list.

## Send a message through the Hermes station

The origin is an ordinary Crosstalk instance on the transmitting island:

1. Give it only a **TCP Client** connection to the HF station's TCP server.
   Do not also give it a normal path to the intended destination, or Reticulum
   can bypass the radio.
2. Wait for the `hf-txbridge` announce.
3. Start or open a conversation using the recipient's **LXMF delivery
   address**.
4. Enable **Send over HF**, enter one short readable text message, and send.

Crosstalk sends the local LXMF hop to `hf-txbridge`; the recipient's delivery
address rides in the bridge title. A local delivered status only confirms the
message reached the transmitting bridge. There is no HF acknowledgement.

On reception, the far application sees the ingress identity as the sender and
`hfvia:<CALLSIGN>` as the title. The original Reticulum identity does not cross
the public radio hop.

## What Start does

Crosstalk launches a child process from the selected repository:

- Hermes starts `python -m hfbridge.txbridge`.
- RTL-SDR starts `python -m hfbridge.ingress`.
- Stop terminates that child process.
- Crosstalk parses the worker's status lines for the counters shown on screen.

The worker deliberately has its own Reticulum configuration and identity under
`rns-instances/`. That separation prevents an encrypted Reticulum packet from
being mistaken for the public HF format, but it also means the two config files
above are part of station setup.

## Common problems

### “Software not found yet”

The selected folder is not the bridge repository root. Choose the directory
that contains `src/hfbridge/txbridge.py`.

### “No route to host” under the Hermes address

The saved IP is not reachable from this computer. Use **Find radio**, verify
wired Ethernet, and update the address. This error is unrelated to the radio
software folder.

### RTL hears a message but cannot forward it

The HF hop worked. Check `rns-instances/ingress/config`, the public-node
session, destination announcements, and whether the destination is reachable
from ingress's own RNS instance.

### The conversation never offers Send over HF

Confirm the origin can hear the `hf-txbridge` announce and does not already
have a normal path to the recipient.

### Hermes says Held instead of On the air

Transmit was off when the worker started. Enabling the toggle is saved, but it
applies on the next Start.

## Read next

- [`reticulum-hf-bridge` README](https://github.com/buildwithparallel/reticulum-hf-bridge): radio implementation and current project status.
- [End-to-end topology](https://github.com/buildwithparallel/reticulum-hf-bridge/blob/main/docs/end-to-end.md): tested multi-process layout and CLI equivalents.
- [Raspberry Pi 5 + Tailscale field test](https://github.com/buildwithparallel/reticulum-hf-bridge/blob/main/docs/pi5-tailscale-field-test.md): private phone control, RTL receiver reports, and optional GPS range data.
- [10 m HF codec](./hf_codec.md): public on-air format for implementers and monitors.

This software does not decide whether a transmission is lawful or appropriate.
The station's control operator must verify current rules, privileges, band use,
equipment, filtering, and message content before enabling transmit.
