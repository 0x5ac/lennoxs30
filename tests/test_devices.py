"""Test devices."""
# pylint: disable=too-many-lines
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=invalid-name
# pylint: disable=protected-access
# pylint: disable=line-too-long

import logging

from unittest.mock import patch

import pytest
from homeassistant.helpers import device_registry as dr
from lennoxs30api.s30api_async import LENNOX_NONE_STR, lennox_zone
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.lennoxs30 import (
    DOMAIN,
    Manager,
)
from custom_components.lennoxs30.const import (
    LENNOX_MFG,
    VENTILATION_EQUIPMENT_ID,
)
from custom_components.lennoxs30.device import (
    S30AuxiliaryUnit,
    S30ControllerDevice,
    S30IndoorUnit,
    S30OutdoorUnit,
    S30VentilationUnit,
)


# The id the mocked registry hands back for the controller; children must link to it via via_device_id.
CONTROLLER_DEVICE_ID = "controller-device-id"


@pytest.mark.asyncio()
async def test_create_devices_multiple_times(hass, manager_2_systems: Manager):
    manager = manager_2_systems
    device_registry = dr.async_get(hass)
    with patch.object(device_registry, "async_get_or_create"):
        await manager.create_devices()

        assert len(manager.system_equip_device_map[manager.api.system_list[0].sysId]) == 3
        assert len(manager.system_equip_device_map[manager.api.system_list[1].sysId]) == 4
        assert len(manager.system_equip_device_map) == 2

        await manager.create_devices()
        assert len(manager.system_equip_device_map[manager.api.system_list[0].sysId]) == 3
        assert len(manager.system_equip_device_map[manager.api.system_list[1].sysId]) == 4
        assert len(manager.system_equip_device_map) == 2


@pytest.mark.asyncio()
async def test_create_devices(hass, manager_2_systems: Manager):
    manager = manager_2_systems
    device_registry = dr.async_get(hass)
    system = manager.api.system_list[0]
    with patch.object(device_registry, "async_get_or_create") as mock_create_device:
        mock_create_device.return_value.id = CONTROLLER_DEVICE_ID
        await manager.create_devices()

        assert len(manager.system_equip_device_map[manager.api.system_list[0].sysId]) == 3
        assert len(manager.system_equip_device_map[manager.api.system_list[1].sysId]) == 4
        assert len(manager.system_equip_device_map) == 2

        call = mock_create_device.mock_calls[0]
        identifiers = call.kwargs["identifiers"]
        assert call.kwargs["manufacturer"] == LENNOX_MFG
        assert call.kwargs["suggested_area"] == "basement"
        assert call.kwargs["name"] == manager.api.system_list[0].name
        assert call.kwargs["model"] == manager.api.system_list[0].productType
        assert call.kwargs["sw_version"] == manager.api.system_list[0].softwareVersion
        elem = None
        for elem in identifiers:
            break
        assert elem[0] == DOMAIN
        assert elem[1] == manager.api.system_list[0].unique_id
        device = manager.system_equip_device_map[system.sysId][0]
        assert isinstance(device, S30ControllerDevice)
        assert device.unique_name == system.unique_id
        assert device.device_id == CONTROLLER_DEVICE_ID

        call = mock_create_device.mock_calls[1]
        identifiers = call.kwargs["identifiers"]
        assert call.kwargs["manufacturer"] == LENNOX_MFG
        assert call.kwargs["suggested_area"] == "outside"
        assert call.kwargs["name"] == manager.api.system_list[0].name + " Heat Pump"
        assert call.kwargs["model"] == "XP20-036-230B04"
        assert call.kwargs["hw_version"] == "5821D09999"
        assert "sw_version" not in call.kwargs
        assert call.kwargs["via_device_id"] == CONTROLLER_DEVICE_ID
        for elem in identifiers:
            break
        assert elem[0] == DOMAIN
        assert elem[1] == manager.api.system_list[0].unique_id + "_ou"
        device = manager.system_equip_device_map[system.sysId][1]
        assert isinstance(device, S30OutdoorUnit)
        assert device.unique_name == system.unique_id + "_ou"

        call = mock_create_device.mock_calls[2]
        identifiers = call.kwargs["identifiers"]
        assert call.kwargs["manufacturer"] == LENNOX_MFG
        assert call.kwargs["suggested_area"] == "basement"
        assert call.kwargs["name"] == manager.api.system_list[0].name + " Air Handler"
        assert call.kwargs["model"] == "CBA38MV-036-230-02"
        assert call.kwargs["hw_version"] == "1621B25999"
        assert "sw_version" not in call.kwargs
        assert call.kwargs["via_device_id"] == CONTROLLER_DEVICE_ID
        for elem in identifiers:
            break
        assert elem[0] == DOMAIN
        assert elem[1] == manager.api.system_list[0].unique_id + "_iu"
        device = manager.system_equip_device_map[system.sysId][2]
        assert isinstance(device, S30IndoorUnit)
        assert device.unique_name == system.unique_id + "_iu"

        call = mock_create_device.mock_calls[3]
        zone: lennox_zone = manager.api.system_list[0].zone_list[0]
        identifiers = call.kwargs["identifiers"]
        assert call.kwargs["manufacturer"] == LENNOX_MFG
        assert call.kwargs["name"] == manager.api.system_list[0].name + "_" + zone.name
        assert call.kwargs["model"] == "thermostat"
        assert "sw_version" not in call.kwargs
        assert call.kwargs["via_device_id"] == CONTROLLER_DEVICE_ID

        for elem in identifiers:
            break
        assert elem[0] == DOMAIN
        assert elem[1] == zone.unique_id


@pytest.mark.asyncio()
async def test_create_devices_no_outdoor(hass, manager: Manager):
    device_registry = dr.async_get(hass)
    system = manager.api.system_list[0]
    with patch.object(device_registry, "async_get_or_create") as mock_create_device:
        mock_create_device.return_value.id = CONTROLLER_DEVICE_ID
        system.outdoorUnitType = LENNOX_NONE_STR
        system.equipment.pop(1)
        await manager.create_devices()

        assert len(manager.system_equip_device_map[system.sysId]) == 2

        call = mock_create_device.mock_calls[0]
        identifiers = call.kwargs["identifiers"]
        assert call.kwargs["manufacturer"] == LENNOX_MFG
        assert call.kwargs["suggested_area"] == "basement"
        assert call.kwargs["name"] == manager.api.system_list[0].name
        assert call.kwargs["model"] == manager.api.system_list[0].productType
        assert call.kwargs["sw_version"] == manager.api.system_list[0].softwareVersion
        elem = None
        for elem in identifiers:
            break
        assert elem[0] == DOMAIN
        assert elem[1] == manager.api.system_list[0].unique_id
        device = manager.system_equip_device_map[system.sysId][0]
        assert isinstance(device, S30ControllerDevice)
        assert device.unique_name == system.unique_id

        call = mock_create_device.mock_calls[1]
        identifiers = call.kwargs["identifiers"]
        assert call.kwargs["manufacturer"] == LENNOX_MFG
        assert call.kwargs["suggested_area"] == "basement"
        assert call.kwargs["name"] == manager.api.system_list[0].name + " Air Handler"
        assert call.kwargs["model"] == "CBA38MV-036-230-02"
        assert call.kwargs["hw_version"] == "1621B25999"
        assert "sw_version" not in call.kwargs
        assert call.kwargs["via_device_id"] == CONTROLLER_DEVICE_ID

        for elem in identifiers:
            break
        assert elem[0] == DOMAIN
        assert elem[1] == manager.api.system_list[0].unique_id + "_iu"
        device = manager.system_equip_device_map[system.sysId][2]
        assert isinstance(device, S30IndoorUnit)
        assert device.unique_name == system.unique_id + "_iu"

        call = mock_create_device.mock_calls[2]
        zone: lennox_zone = manager.api.system_list[0].zone_list[0]
        identifiers = call.kwargs["identifiers"]
        assert call.kwargs["manufacturer"] == LENNOX_MFG
        assert call.kwargs["name"] == manager.api.system_list[0].name + "_" + zone.name
        assert call.kwargs["model"] == "thermostat"
        assert "sw_version" not in call.kwargs
        assert call.kwargs["via_device_id"] == CONTROLLER_DEVICE_ID

        for elem in identifiers:
            break
        assert elem[0] == DOMAIN
        assert elem[1] == zone.unique_id


@pytest.mark.asyncio()
async def test_create_devices_no_indoor(hass, manager: Manager):
    device_registry = dr.async_get(hass)
    system = manager.api.system_list[0]
    with patch.object(device_registry, "async_get_or_create") as mock_create_device:
        mock_create_device.return_value.id = CONTROLLER_DEVICE_ID
        manager.api.system_list[0].indoorUnitType = LENNOX_NONE_STR
        system.equipment.pop(2)

        await manager.create_devices()

        assert len(manager.system_equip_device_map[system.sysId]) == 2

        call = mock_create_device.mock_calls[0]
        identifiers = call.kwargs["identifiers"]
        assert call.kwargs["manufacturer"] == LENNOX_MFG
        assert call.kwargs["suggested_area"] == "basement"
        assert call.kwargs["name"] == manager.api.system_list[0].name
        assert call.kwargs["model"] == manager.api.system_list[0].productType
        assert call.kwargs["sw_version"] == manager.api.system_list[0].softwareVersion
        elem = None
        for elem in identifiers:
            break
        assert elem[0] == DOMAIN
        assert elem[1] == manager.api.system_list[0].unique_id
        device = manager.system_equip_device_map[system.sysId][0]
        assert isinstance(device, S30ControllerDevice)
        assert device.unique_name == system.unique_id

        call = mock_create_device.mock_calls[1]
        identifiers = call.kwargs["identifiers"]
        assert call.kwargs["manufacturer"] == LENNOX_MFG
        assert call.kwargs["suggested_area"] == "outside"
        assert call.kwargs["name"] == manager.api.system_list[0].name + " Heat Pump"
        assert call.kwargs["model"] == "XP20-036-230B04"
        assert call.kwargs["hw_version"] == "5821D09999"
        assert "sw_version" not in call.kwargs
        assert call.kwargs["via_device_id"] == CONTROLLER_DEVICE_ID
        for elem in identifiers:
            break
        assert elem[0] == DOMAIN
        assert elem[1] == manager.api.system_list[0].unique_id + "_ou"
        device = manager.system_equip_device_map[system.sysId][1]
        assert isinstance(device, S30OutdoorUnit)
        assert device.unique_name == system.unique_id + "_ou"

        call = mock_create_device.mock_calls[2]
        zone: lennox_zone = manager.api.system_list[0].zone_list[0]
        identifiers = call.kwargs["identifiers"]
        assert call.kwargs["manufacturer"] == LENNOX_MFG
        assert call.kwargs["name"] == manager.api.system_list[0].name + "_" + zone.name
        assert call.kwargs["model"] == "thermostat"
        assert "sw_version" not in call.kwargs
        assert call.kwargs["via_device_id"] == CONTROLLER_DEVICE_ID

        for elem in identifiers:
            break
        assert elem[0] == DOMAIN
        assert elem[1] == zone.unique_id


@pytest.mark.asyncio()
async def test_create_devices_furn_ac_zoning(hass, manager_system_04_furn_ac_zoning_ble: Manager):
    manager: Manager = manager_system_04_furn_ac_zoning_ble
    device_registry = dr.async_get(hass)
    system = manager.api.system_list[0]
    with patch.object(device_registry, "async_get_or_create") as mock_create_device:
        mock_create_device.return_value.id = CONTROLLER_DEVICE_ID
        await manager.create_devices()
        assert mock_create_device.call_count == 11
        assert len(manager.system_equip_device_map[system.sysId]) == 5

        call = mock_create_device.mock_calls[0]
        identifiers = call.kwargs["identifiers"]
        assert call.kwargs["manufacturer"] == LENNOX_MFG
        assert call.kwargs["suggested_area"] == "basement"
        assert call.kwargs["name"] == manager.api.system_list[0].name
        assert call.kwargs["model"] == manager.api.system_list[0].productType
        assert call.kwargs["sw_version"] == manager.api.system_list[0].softwareVersion
        elem = None
        for elem in identifiers:
            break
        assert elem[0] == DOMAIN
        assert elem[1] == manager.api.system_list[0].unique_id

        call = mock_create_device.mock_calls[1]
        identifiers = call.kwargs["identifiers"]
        assert call.kwargs["manufacturer"] == LENNOX_MFG
        assert call.kwargs["suggested_area"] == "outside"
        assert call.kwargs["name"] == manager.api.system_list[0].name + " Air Conditioner"
        assert call.kwargs["model"] == "EL18XCVS036-230A01"
        assert call.kwargs["hw_version"] == "5821E06000"
        assert "sw_version" not in call.kwargs
        assert call.kwargs["via_device_id"] == CONTROLLER_DEVICE_ID

        for elem in identifiers:
            break
        assert elem[0] == DOMAIN
        assert elem[1] == manager.api.system_list[0].unique_id + "_ou"
        device = manager.system_equip_device_map[system.sysId][1]
        assert isinstance(device, S30OutdoorUnit)
        assert device.unique_name == system.unique_id + "_ou"

        call = mock_create_device.mock_calls[2]
        identifiers = call.kwargs["identifiers"]
        assert call.kwargs["manufacturer"] == LENNOX_MFG
        assert call.kwargs["suggested_area"] == "basement"
        assert call.kwargs["name"] == manager.api.system_list[0].name + " Furnace"
        assert call.kwargs["model"] == "SLP99UH110XV60C-01"
        assert call.kwargs["hw_version"] == "5920H11000"
        assert "sw_version" not in call.kwargs
        assert call.kwargs["via_device_id"] == CONTROLLER_DEVICE_ID

        for elem in identifiers:
            break
        assert elem[0] == DOMAIN
        assert elem[1] == manager.api.system_list[0].unique_id + "_iu"
        device = manager.system_equip_device_map[system.sysId][2]
        assert isinstance(device, S30IndoorUnit)
        assert device.unique_name == system.unique_id + "_iu"

        call = mock_create_device.mock_calls[3]
        identifiers = call.kwargs["identifiers"]
        assert call.kwargs["manufacturer"] == LENNOX_MFG
        assert call.kwargs["suggested_area"] == "basement"
        assert call.kwargs["name"] == manager.api.system_list[0].name + " Zoning Controller (zone 1 to 4)"
        assert call.kwargs["model"] == "103916-03"
        assert call.kwargs["hw_version"] == "BT21B13000"
        assert "sw_version" not in call.kwargs
        assert call.kwargs["via_device_id"] == CONTROLLER_DEVICE_ID

        for elem in identifiers:
            break
        assert elem[0] == DOMAIN
        assert elem[1] == manager.api.system_list[0].unique_id + "_BT21B13000"
        device = manager.system_equip_device_map[system.sysId][3]
        assert isinstance(device, S30AuxiliaryUnit)
        assert device.unique_name == system.unique_id + "_BT21B13000"

        call = mock_create_device.mock_calls[4]
        identifiers = call.kwargs["identifiers"]
        assert call.kwargs["manufacturer"] == LENNOX_MFG
        assert call.kwargs["name"] == manager.api.system_list[0].name + " Ventilator"
        assert call.kwargs["model"] == "2_stage_hrv"
        assert "sw_version" not in call.kwargs
        assert call.kwargs["via_device_id"] == CONTROLLER_DEVICE_ID
        device = manager.system_equip_device_map[system.sysId][VENTILATION_EQUIPMENT_ID]
        assert isinstance(device, S30VentilationUnit)

        call = mock_create_device.mock_calls[5]
        zone: lennox_zone = manager.api.system_list[0].zone_list[0]
        identifiers = call.kwargs["identifiers"]
        assert call.kwargs["manufacturer"] == LENNOX_MFG
        assert call.kwargs["name"] == manager.api.system_list[0].name + "_" + zone.name
        assert call.kwargs["model"] == "thermostat"
        assert "sw_version" not in call.kwargs
        assert call.kwargs["via_device_id"] == CONTROLLER_DEVICE_ID

        for elem in identifiers:
            break
        assert elem[0] == DOMAIN
        assert elem[1] == zone.unique_id

        call = mock_create_device.mock_calls[6]
        zone: lennox_zone = manager.api.system_list[0].zone_list[1]
        identifiers = call.kwargs["identifiers"]
        assert call.kwargs["manufacturer"] == LENNOX_MFG
        assert call.kwargs["name"] == manager.api.system_list[0].name + "_" + zone.name
        assert call.kwargs["model"] == "thermostat"
        assert "sw_version" not in call.kwargs
        assert call.kwargs["via_device_id"] == CONTROLLER_DEVICE_ID

        for elem in identifiers:
            break
        assert elem[0] == DOMAIN
        assert elem[1] == zone.unique_id

        call = mock_create_device.mock_calls[7]
        zone: lennox_zone = manager.api.system_list[0].zone_list[2]
        identifiers = call.kwargs["identifiers"]
        assert call.kwargs["manufacturer"] == LENNOX_MFG
        assert call.kwargs["name"] == manager.api.system_list[0].name + "_" + zone.name
        assert call.kwargs["model"] == "thermostat"
        assert "sw_version" not in call.kwargs
        assert call.kwargs["via_device_id"] == CONTROLLER_DEVICE_ID

        for elem in identifiers:
            break
        assert elem[0] == DOMAIN
        assert elem[1] == zone.unique_id

        index = 8
        for ble_device in system.ble_devices.values():
            if ble_device.deviceType == "tstat":
                continue
            call = mock_create_device.mock_calls[index]
            identifiers = call.kwargs["identifiers"]
            assert call.kwargs["manufacturer"] == LENNOX_MFG
            assert call.kwargs["name"] == system.name + " " + ble_device.deviceName
            assert call.kwargs["model"] == ble_device.controlModelNumber
            assert call.kwargs["sw_version"] == ble_device.controlSoftwareVersion
            assert call.kwargs["hw_version"] == ble_device.controlHardwareVersion
            assert call.kwargs["via_device_id"] == CONTROLLER_DEVICE_ID

            for elem in identifiers:
                break
            assert elem[0] == DOMAIN
            assert elem[1] == f"{system.unique_id}_ble_{ble_device.ble_id}"
            index += 1


@pytest.mark.asyncio()
async def test_create_device_no_equipment(hass, manager_system_04_furn_ac_zoning: Manager):
    """Test to make sure we don't crash if no equipment is received"""
    manager = manager_system_04_furn_ac_zoning
    device_registry = dr.async_get(hass)
    system = manager.api.system_list[0]
    # Wipe out the equipment list.
    system.equipment = {}
    system.ventilationUnitType = None
    with patch.object(device_registry, "async_get_or_create") as mock_create_device:
        mock_create_device.return_value.id = CONTROLLER_DEVICE_ID
        await manager.create_devices()

        # The controller is always mapped as equipment 0 even when no equipment list was received,
        # which is the normal case on cloud connections.
        assert len(manager.system_equip_device_map[manager.api.system_list[0].sysId]) == 1
        controller = manager.system_equip_device_map[manager.api.system_list[0].sysId][0]
        assert isinstance(controller, S30ControllerDevice)
        assert controller.unique_name == manager.api.system_list[0].unique_id
        assert len(manager.system_equip_device_map) == 1

        call = mock_create_device.mock_calls[0]
        identifiers = call.kwargs["identifiers"]
        assert call.kwargs["manufacturer"] == LENNOX_MFG
        assert call.kwargs["suggested_area"] == "basement"
        assert call.kwargs["name"] == manager.api.system_list[0].name
        assert call.kwargs["model"] == manager.api.system_list[0].productType
        assert call.kwargs["sw_version"] == manager.api.system_list[0].softwareVersion
        elem = None
        for elem in identifiers:
            break
        assert elem[0] == DOMAIN
        assert elem[1] == manager.api.system_list[0].unique_id

        call = mock_create_device.mock_calls[1]
        identifiers = call.kwargs["identifiers"]
        assert call.kwargs["manufacturer"] == LENNOX_MFG
        assert call.kwargs["suggested_area"] == "outside"
        assert call.kwargs["name"] == manager.api.system_list[0].name + " " + system.outdoorUnitType
        assert call.kwargs["model"] == "air conditioner"
        assert call.kwargs["hw_version"] is None
        assert "sw_version" not in call.kwargs
        assert call.kwargs["via_device_id"] == CONTROLLER_DEVICE_ID
        for elem in identifiers:
            break
        assert elem[0] == DOMAIN
        assert elem[1] == manager.api.system_list[0].unique_id + "_ou"

        call = mock_create_device.mock_calls[2]
        identifiers = call.kwargs["identifiers"]
        assert call.kwargs["manufacturer"] == LENNOX_MFG
        assert call.kwargs["suggested_area"] == "basement"
        assert call.kwargs["name"] == manager.api.system_list[0].name + " " + system.indoorUnitType
        assert call.kwargs["model"] == "furnace"
        assert call.kwargs["hw_version"] is None
        assert "sw_version" not in call.kwargs
        assert call.kwargs["via_device_id"] == CONTROLLER_DEVICE_ID
        for elem in identifiers:
            break
        assert elem[0] == DOMAIN
        assert elem[1] == manager.api.system_list[0].unique_id + "_iu"


@pytest.mark.asyncio()
async def test_create_devices_zone_name_missing(hass, manager: Manager, caplog):
    """Create devices should continue with a fallback zone name when zone.name is missing."""
    device_registry = dr.async_get(hass)
    system = manager.api.system_list[0]
    zone: lennox_zone = system.zone_list[0]
    zone.name = None

    with patch.object(device_registry, "async_get_or_create") as mock_create_device:
        mock_create_device.return_value.id = CONTROLLER_DEVICE_ID
        with caplog.at_level(logging.WARNING):
            caplog.clear()
            await manager.create_devices()

    zone_call = None
    for call in mock_create_device.mock_calls:
        if call.kwargs.get("model") == "thermostat":
            zone_call = call
            break

    assert zone_call is not None
    assert zone_call.kwargs["name"] == f"{system.name}_Zone_{zone.id}"
    assert "create_devices active zone missing name" in caplog.text


@pytest.mark.asyncio()
async def test_S30VentilationUnit_device_model(hass, manager_2_systems: Manager):
    manager = manager_2_systems
    system = manager.api.system_list[1]
    s30 = S30ControllerDevice(hass, manager.config_entry, system)
    system.ventilationUnitType = "ventilation"
    vent = S30VentilationUnit(hass, manager.config_entry, system, s30)
    assert vent.device_model == "Fresh Air Damper"

    system.ventilationUnitType = "1_stage_hrv"
    vent = S30VentilationUnit(hass, manager.config_entry, system, s30)
    assert vent.device_model == "1_stage_hrv"


@pytest.mark.asyncio()
async def test_create_devices_links_children_by_registry_id(hass, manager: Manager):
    """Against the real registry, every child device must carry the controller's registry id as via_device_id."""
    # The registry only creates devices for a config entry hass knows about.
    entry = MockConfigEntry(
        domain=DOMAIN,
        entry_id=manager.config_entry.entry_id,
        unique_id=manager.config_entry.unique_id,
        data=dict(manager.config_entry.data),
    )
    entry.add_to_hass(hass)
    device_registry = dr.async_get(hass)
    # conftest stubs async_get_or_create for every test; this one needs the real registry.
    real_async_get_or_create = dr.DeviceRegistry.async_get_or_create.__get__(device_registry)
    with patch.object(device_registry, "async_get_or_create", real_async_get_or_create):
        await manager.create_devices()
    system = manager.api.system_list[0]

    def registered(unique_name: str) -> dr.DeviceEntry:
        found = device_registry.async_get_devices(identifiers={(DOMAIN, unique_name)}, config_entry_id=manager.config_entry.entry_id)
        assert len(found) == 1, unique_name
        return found[0]

    controller = registered(system.unique_id)
    assert manager.system_equip_device_map[system.sysId][0].device_id == controller.id
    assert controller.via_device_id is None
    for suffix in ("_ou", "_iu"):
        assert registered(system.unique_id + suffix).via_device_id == controller.id
    for zone in system.zone_list:
        if zone.is_zone_active():
            assert registered(zone.unique_id).via_device_id == controller.id
