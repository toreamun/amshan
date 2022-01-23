"""Mappings between OBIS codes and keys used in decoded data."""
from __future__ import annotations

FIELD_OBIS_LIST_VER_ID = "list_ver_id"
FIELD_METER_ID = "meter_id"
FIELD_METER_TYPE = "meter_type"
FIELD_METER_MANUFACTURER = "meter_manufacturer"
FIELD_METER_DATETIME = "meter_datetime"
FIELD_ACTIVE_POWER_IMPORT = "active_power_import"
FIELD_ACTIVE_POWER_IMPORT_L1 = "active_power_import_l1"
FIELD_ACTIVE_POWER_IMPORT_L2 = "active_power_import_l2"
FIELD_ACTIVE_POWER_IMPORT_L3 = "active_power_import_l3"
FIELD_ACTIVE_POWER_EXPORT = "active_power_export"
FIELD_ACTIVE_POWER_EXPORT_L1 = "active_power_export_l1"
FIELD_ACTIVE_POWER_EXPORT_L2 = "active_power_export_l2"
FIELD_ACTIVE_POWER_EXPORT_L3 = "active_power_export_l3"
FIELD_REACTIVE_POWER_IMPORT = "reactive_power_import"
FIELD_REACTIVE_POWER_IMPORT_L1 = "reactive_power_import_l1"
FIELD_REACTIVE_POWER_IMPORT_L2 = "reactive_power_import_l2"
FIELD_REACTIVE_POWER_IMPORT_L3 = "reactive_power_import_l3"
FIELD_REACTIVE_POWER_EXPORT = "reactive_power_export"
FIELD_REACTIVE_POWER_EXPORT_L1 = "reactive_power_export_l1"
FIELD_REACTIVE_POWER_EXPORT_L2 = "reactive_power_export_l2"
FIELD_REACTIVE_POWER_EXPORT_L3 = "reactive_power_export_l3"
FIELD_CURRENT_L1 = "current_l1"
FIELD_CURRENT_L2 = "current_l2"
FIELD_CURRENT_L3 = "current_l3"
FIELD_VOLTAGE_L1 = "voltage_l1"
FIELD_VOLTAGE_L2 = "voltage_l2"
FIELD_VOLTAGE_L3 = "voltage_l3"
FIELD_ACTIVE_POWER_IMPORT_TOTAL = "active_power_import_total"
FIELD_ACTIVE_POWER_EXPORT_TOTAL = "active_power_export_total"
FIELD_REACTIVE_POWER_IMPORT_TOTAL = "reactive_power_import_total"
FIELD_REACTIVE_POWER_EXPORT_TOTAL = "reactive_power_export_total"
FIELD_POWER_FACTOR = "power_factor"
FIELD_POWER_FACTOR_L1 = "power_factor_l1"
FIELD_POWER_FACTOR_L2 = "power_factor_l2"
FIELD_POWER_FACTOR_L3 = "power_factor_l3"

name_obis_map: dict[str, list[str]] = {
    FIELD_OBIS_LIST_VER_ID: ["0.2.129"],
    FIELD_METER_ID: ["96.1.0", "0.0.5"],
    FIELD_METER_TYPE: ["96.1.7", "96.1.1"],
    FIELD_METER_DATETIME: ["1.0.0"],
    FIELD_ACTIVE_POWER_IMPORT: ["1.7.0"],
    FIELD_ACTIVE_POWER_IMPORT_L1: ["21.7.0"],
    FIELD_ACTIVE_POWER_IMPORT_L2: ["41.7.0"],
    FIELD_ACTIVE_POWER_IMPORT_L3: ["61.7.0"],
    FIELD_ACTIVE_POWER_EXPORT: ["2.7.0"],
    FIELD_ACTIVE_POWER_EXPORT_L1: ["22.7.0"],
    FIELD_ACTIVE_POWER_EXPORT_L2: ["42.7.0"],
    FIELD_ACTIVE_POWER_EXPORT_L3: ["62.7.0"],
    FIELD_REACTIVE_POWER_IMPORT: ["3.7.0"],
    FIELD_REACTIVE_POWER_IMPORT_L1: ["23.7.0"],
    FIELD_REACTIVE_POWER_IMPORT_L2: ["43.7.0"],
    FIELD_REACTIVE_POWER_IMPORT_L3: ["63.7.0"],
    FIELD_REACTIVE_POWER_EXPORT: ["4.7.0"],
    FIELD_REACTIVE_POWER_EXPORT_L1: ["24.7.0"],
    FIELD_REACTIVE_POWER_EXPORT_L2: ["44.7.0"],
    FIELD_REACTIVE_POWER_EXPORT_L3: ["64.7.0"],
    FIELD_CURRENT_L1: ["31.7.0"],
    FIELD_CURRENT_L2: ["51.7.0"],
    FIELD_CURRENT_L3: ["71.7.0"],
    FIELD_VOLTAGE_L1: ["32.7.0"],
    FIELD_VOLTAGE_L2: ["52.7.0"],
    FIELD_VOLTAGE_L3: ["72.7.0"],
    FIELD_ACTIVE_POWER_IMPORT_TOTAL: ["1.8.0"],
    FIELD_ACTIVE_POWER_EXPORT_TOTAL: ["2.8.0"],
    FIELD_REACTIVE_POWER_IMPORT_TOTAL: ["3.8.0"],
    FIELD_REACTIVE_POWER_EXPORT_TOTAL: ["4.8.0"],
}

obis_name_map: dict[str, str] = {}
for name, obis_values in name_obis_map.items():
    for obis in obis_values:
        obis_name_map[obis] = name
