import appdaemon.plugins.hass.hassapi as hass

class SetMaxBrightness(hass.Hass):
    async def initialize(self):
        self.listen_event(self.run, "SetMaxBrightness")

    async def dim(self, entity_id, data):
        self.turn_on(entity_id, **data)

    async def manDim(self, data):
        self.fire_event("MANUAL_DIM", **data)

    async def run(self, event, data, kwars):
        group = data.get("group")
        maxBrightness = data.get("maxBrightness")
        previousMaxBrightness = data.get("previousMaxBrightness")
        transition = data.get("transition") or 5
        self.log(data)


        # Setup direction (dimming down or brightening up)
        dimming = previousMaxBrightness > maxBrightness

        # Grab the entities
        entities = await self.get_state("group."+group, attribute="entity_id")
        self.log("ENTITIES: {}".format(entities))
        entitiesToChange = []
        entitiesToTurnOff = []
        lightsToManuallyDim = []

        for entityid in entities:
            entityState = await self.get_state(entityid)
            supported_features = await self.get_state(entityid, attribute="supported_features")
            curBrightness = await self.get_state(entityid, attribute="brightness")

            # if entity.domain != "light": continue

            try:
                if (supported_features & 1) == True: # check to see if entity can dim
                    if dimming:
                        if entityState == "on" and curBrightness > maxBrightness:
                            if (supported_features & 32) > 0: # If the light can't transition manually...
                                entitiesToChange.append(entityid)

                            else:
                                lightsToManuallyDim.append(entityid)

                        else:
                            if maxBrightness < 50:
                                entitiesToTurnOff.append(entityid)
                    else:
                        # brightening
                        if entityState == "on" and curBrightness < maxBrightness:
                            if (supported_features & 32) > 0: # If the light can't transition manually...
                                entitiesToChange.append(entityid)

                            else:
                                lightsToManuallyDim.append(entityid)

            except Exception as e:
                self.log(e)

        data = {"brightness":maxBrightness, "transition": transition}
        [await self.dim(x, data) for x in entitiesToChange]
        # hass.services.call_async("light", "turn_on", service_data = data)

        if len(lightsToManuallyDim) > 0:
            for light in lightsToManuallyDim:
                data = {"entity_id": light, "brightness":maxBrightness, "transition":transition}
                await self.manDim(data)
                # hass.bus.fire("MANUAL_DIM", event_data=data)

        if len(entitiesToTurnOff) > 0:
            data = {"entity_id", entitiesToTurnOff}
            hass.services.call("light", "turn_off", service_data = data)
