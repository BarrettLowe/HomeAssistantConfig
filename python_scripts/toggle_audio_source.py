logger.debug("Started toggle_audio_source")
source = data.get('source')
speakers = data.get('speakers')

currentSource = hass.states.get(speakers).attributes['source']

if currentSource == "Nothing":
    newSource = source
else:
    newSource = "Nothing"

service_data = {}
service_data['entity_id'] = speakers
service_data['source'] = newSource

if speakers == "media_player.kitchen":
    if hass.states.get(speakers) == 'unavailable':
        hass.services.call("rest_command","snapclient_toggle_kitchen")
        while (hass.states.get(speakers) == 'unavailable'):
            time.sleep(0.5)

hass.services.call('media_player','select_source', service_data)