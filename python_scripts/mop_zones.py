# This is just a simple python script to help with sending the vacuum to 
# different zones. Call this script with as many zones as desired.

zones = data.get("zones")

try:
    service_data = {'entity_id':"vacuum.roborock"}
    service_data["command"] = 'zoned_cleanup'
    service_data["params"] = {'zone_ids': zones}

    logger.debug("service_data:")
    logger.debug(service_data)

    hass.services.call("vacuum","send_command", service_data, False)
    hass.services.call("automation","turn_on", {"entity_id":"automation.vacuum_to_trashcan"})
    hass.services.call("vacuum","set_fan_speed", {"entity_id": "vacuum.roborock", "fan_speed":105})
except Exception as e:
    logger.error(e)