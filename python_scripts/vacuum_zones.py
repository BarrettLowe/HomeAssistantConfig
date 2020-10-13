# This is just a simple python script to help with sending the vacuum to 
# different zones. Call this script with as many zones as desired.


def scr():
    zones = data.get("zones")
    try:
        if (hass.states.get("vacuum.roborock") == "unavailable"):
            hass.services.call("notify","barrett", {
                "message":"The vacuum is not available and cannot run!",
                "title":"Vacuum ERROR"
            })
            return
        service_data = {'entity_id':"vacuum.roborock"}
        service_data["command"] = 'zoned_cleanup'
        service_data["params"] = {'zone_ids': zones}

        logger.debug("service_data:")
        logger.debug(service_data)

        hass.services.call("vacuum","send_command", service_data, False)
        hass.services.call("automation","turn_on", {"entity_id":"automation.vacuum_to_trashcan"})
        hass.services.call("vacuum","set_fan_speed", {"entity_id": "vacuum.roborock", "fan_speed":60})
    except Exception as e:
        logger.error(e)

scr()