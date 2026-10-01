import unittest
from types import SimpleNamespace

from src.backend.rnode_ble import (
    RNODE_UART_SERVICE_UUID,
    advertised_names,
    matches_rnode_device,
    scan_rnode_ble_devices,
)


CORE_BLUETOOTH_UUID = "06B073E2-E6F5-522B-E6A7-F68CCD0359B1"


def device(name="RNode 8561", address=CORE_BLUETOOTH_UUID):
    return SimpleNamespace(name=name, address=address)


def advertisement(local_name="RNode 8561", services=None, rssi=-53):
    return SimpleNamespace(
        local_name=local_name,
        service_uuids=services if services is not None else [RNODE_UART_SERVICE_UUID.upper()],
        rssi=rssi,
    )


class FakeScanner:
    results = {}

    @classmethod
    async def discover(cls, timeout, return_adv):
        cls.timeout = timeout
        cls.return_adv = return_adv
        return cls.results


class RNodeBleMatchingTest(unittest.TestCase):
    def test_names_include_local_and_system_names(self):
        self.assertEqual(
            advertised_names(
                device(name="Meshtastic_ed54"),
                advertisement(local_name="RNode 8561"),
            ),
            ["RNode 8561", "Meshtastic_ed54"],
        )

    def test_generic_target_accepts_advertised_rnode_name(self):
        self.assertTrue(
            matches_rnode_device(
                device(name="Meshtastic_ed54"),
                advertisement(local_name="RNode 8561"),
                None,
            )
        )

    def test_core_bluetooth_uuid_is_a_valid_specific_target(self):
        self.assertTrue(
            matches_rnode_device(
                device(),
                advertisement(),
                CORE_BLUETOOTH_UUID.lower(),
            )
        )

    def test_specific_target_can_match_either_name(self):
        self.assertTrue(
            matches_rnode_device(
                device(name="Meshtastic_ed54"),
                advertisement(local_name="RNode 8561"),
                "Meshtastic_ed54",
            )
        )

    def test_unrelated_uart_device_needs_specific_selection(self):
        candidate = device(name="Sensor")
        advert = advertisement(local_name="Telemetry")
        self.assertFalse(matches_rnode_device(candidate, advert, None))
        self.assertTrue(matches_rnode_device(candidate, advert, CORE_BLUETOOTH_UUID))

    def test_device_without_rnode_uart_service_is_rejected(self):
        self.assertFalse(
            matches_rnode_device(
                device(),
                advertisement(services=["0000180f-0000-1000-8000-00805f9b34fb"]),
                CORE_BLUETOOTH_UUID,
            )
        )


class RNodeBleScanTest(unittest.IsolatedAsyncioTestCase):
    async def test_scan_returns_uuid_names_and_signal(self):
        FakeScanner.results = {
            CORE_BLUETOOTH_UUID: (
                device(name="Meshtastic_ed54"),
                advertisement(local_name="RNode 8561", rssi=-53),
            ),
            "ignored": (
                device(name="Headphones", address="ignored"),
                advertisement(
                    local_name="Headphones",
                    services=["0000180f-0000-1000-8000-00805f9b34fb"],
                ),
            ),
        }

        results = await scan_rnode_ble_devices(timeout=3.5, scanner_class=FakeScanner)

        self.assertEqual(FakeScanner.timeout, 3.5)
        self.assertTrue(FakeScanner.return_adv)
        self.assertEqual(results, [{
            "identifier": CORE_BLUETOOTH_UUID,
            "name": "RNode 8561",
            "advertised_name": "RNode 8561",
            "system_name": "Meshtastic_ed54",
            "rssi": -53,
        }])


if __name__ == "__main__":
    unittest.main()
