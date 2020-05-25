# Simple light notification.

max_brightness = data.get("max_brightness") or 255
entity_id = data.get("entity_id")

oldAttrs = {'entity_id': entity_id}
notifyAttrs = {'entity_id': entity_id}

state = hass.states.get(entity_id)
if not state.domain == 'light':
    raise Exception("Entity is not a light")

attrs = state.attributes
prevState = state.state

# Copy attributes for restoring the light
for a in ['brightness','rgb_color','color_temp']:
    try:
        oldAttrs[a] = attrs[a]
    except KeyError:
        pass

logger.debug(attrs)
logger.debug(state.state)

notifyState = None
notifyBrightness = None
notifyColor = None
notifyTransition = None

if state.state == 'off': 
    notifyState = 'on'
    notifyBrightness = max_brightness
else: 
    if attrs['supported_features'] & 1: #light.SUPPORT_BRIGHTNESS
        notifyState = 'on'
        # light is currently on and supports different brightnesses
        if attrs['supported_features'] & 16: # light.SUPPORT_COLOR
            curColor = attrs['rgb_color']
            logger.debug(curColor)
            if (curColor[2] > (curColor[1] + curColor[0])/2):
                notifyColor = (curColor[2],curColor[1],curColor[0])
            else:
                notifyColor = (100,100,255)
        elif attrs['brightness'] > 255/2: 
            notifyBrightness = 30
        else:
            notifyBrightness = 255

        if attrs['supported_features'] & 32: # light.SUPPORT_TRANSITION
            notifyTransition = 1
    else:
        # light does not support different brightnesses
        notifyState = 'off'
        
if notifyBrightness:
    notifyAttrs['brightness'] = notifyBrightness
if notifyColor:
    notifyAttrs['rgb_color'] = notifyColor
if notifyTransition:
    notifyAttrs['transition'] = notifyTransition
    oldAttrs['transition'] = notifyTransition

hass.services.call('light','turn_'+notifyState, notifyAttrs)

time.sleep(1.0)

hass.services.call('light','turn_'+prevState, oldAttrs)