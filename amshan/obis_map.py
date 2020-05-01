"""Mappings between OBIS codes and keys used in decoded data."""
from typing import Dict, List

NEK_HAN_FIELD_OBIS_LIST_VER_ID = "list_ver_id"
NEK_HAN_FIELD_METER_ID = "meter_id"
NEK_HAN_FIELD_METER_TYPE = "meter_type"
NEK_HAN_FIELD_METER_MANUFACTURER = "meter_manufacturer"
NEK_HAN_FIELD_METER_DATETIME = "meter_datetime"
NEK_HAN_FIELD_ACTIVE_POWER_IMPORT = "active_power_import"
NEK_HAN_FIELD_ACTIVE_POWER_EXPORT = "active_power_export"
NEK_HAN_FIELD_REACTIVE_POWER_IMPORT = "reactive_power_import"
NEK_HAN_FIELD_REACTIVE_POWER_EXPORT = "reactive_power_export"
NEK_HAN_FIELD_CURRENT_L1 = "current_l1"
NEK_HAN_FIELD_CURRENT_L2 = "current_l2"
NEK_HAN_FIELD_CURRENT_L3 = "current_l3"
NEK_HAN_FIELD_VOLTAGE_L1 = "voltage_l1"
NEK_HAN_FIELD_VOLTAGE_L2 = "voltage_l2"
NEK_HAN_FIELD_VOLTAGE_L3 = "voltage_l3"
NEK_HAN_FIELD_ACTIVE_POWER_IMPORT_HOUR = "active_power_import_hour"
NEK_HAN_FIELD_ACTIVE_POWER_EXPORT_HOUR = "active_power_export_hour"
NEK_HAN_FIELD_REACTIVE_POWER_IMPORT_HOUR = "reactive_power_import_hour"
NEK_HAN_FIELD_REACTIVE_POWER_EXPORT_HOUR = "reactive_power_export_hour"

name_obis_map: Dict[str, List[str]] = {
    NEK_HAN_FIELD_OBIS_LIST_VER_ID: ["1.1.0.2.129.255"],
    NEK_HAN_FIELD_METER_ID: ["0.0.96.1.0.255", "1.1.0.0.5.255"],
    NEK_HAN_FIELD_METER_TYPE: ["0.0.96.1.7.255", "1.1.96.1.1.255"],
    NEK_HAN_FIELD_ACTIVE_POWER_IMPORT: ["1.0.1.7.0.255", "1.1.1.7.0.255"],
    NEK_HAN_FIELD_ACTIVE_POWER_EXPORT: ["1.0.2.7.0.255", "1.1.2.7.0.255"],
    NEK_HAN_FIELD_REACTIVE_POWER_IMPORT: ["1.0.3.7.0.255", "1.1.3.7.0.255"],
    NEK_HAN_FIELD_REACTIVE_POWER_EXPORT: ["1.0.4.7.0.255", "1.1.4.7.0.255"],
    NEK_HAN_FIELD_CURRENT_L1: ["1.0.31.7.0.255", "1.1.31.7.0.255"],
    NEK_HAN_FIELD_CURRENT_L2: ["1.0.51.7.0.255", "1.1.51.7.0.255"],
    NEK_HAN_FIELD_CURRENT_L3: ["1.0.71.7.0.255", "1.1.71.7.0.255"],
    NEK_HAN_FIELD_VOLTAGE_L1: ["1.0.32.7.0.255", "1.1.32.7.0.255"],
    NEK_HAN_FIELD_VOLTAGE_L2: ["1.0.52.7.0.255", "1.1.52.7.0.255"],
    NEK_HAN_FIELD_VOLTAGE_L3: ["1.0.72.7.0.255", "1.1.72.7.0.255"],
    NEK_HAN_FIELD_METER_DATETIME: ["0.0.1.0.0.255", "0.1.1.0.0.255"],
    NEK_HAN_FIELD_ACTIVE_POWER_IMPORT_HOUR: ["1.0.1.8.0.255", "1.1.1.8.0.255"],
    NEK_HAN_FIELD_ACTIVE_POWER_EXPORT_HOUR: ["1.0.2.8.0.255", "1.1.2.8.0.255"],
    NEK_HAN_FIELD_REACTIVE_POWER_IMPORT_HOUR: ["1.0.3.8.0.255", "1.1.3.8.0.255"],
    NEK_HAN_FIELD_REACTIVE_POWER_EXPORT_HOUR: ["1.0.4.8.0.255", "1.1.4.8.0.255"],
}

obis_name_map: Dict[str, str] = {}
for name, obis_values in name_obis_map.items():
    for obis in obis_values:
        obis_name_map[obis] = name
