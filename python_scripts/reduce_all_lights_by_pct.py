transition = data.get("transition")
pct = data.get("pct")
color_temp = data.get("color_temp")

devices = []
for device in hass.states.all():
    if device.domain == 'light' and device.entity_id != 'light.undercabinet_lights' and device.state == 'on':
        try:
            logger.error(device.attributes['brightness'])
            if device.attributes['supported_features'] & 1: #light.SUPPORT_BRIGHTNESS


                brightness = int(int(device.attributes['brightness']) * (pct/100))
                if brightness==0:
                    brightness = 1
                service_data = {"entity_id":device.entity_id, 
                                "brightness":brightness}


                if transition: 
                    service_data["transition"] = transition
                if color_temp and device.entity_id != 'light.nursery_dresser': # Leave the nursery dresser at whatever color.
                    service_data["color_temp"] = color_temp

                if not device.attributes['supported_features'] & 32: #light.SUPPORT_TRANSITION
                    hass.bus.fire("MANUAL_DIM",service_data)
                else:
                    hass.services.call("light", "turn_on", service_data, False)
        except Exception as e:
            logger.error("Problem halfing the brightness of {}".format(device.entity_id))
            logger.error(e)
