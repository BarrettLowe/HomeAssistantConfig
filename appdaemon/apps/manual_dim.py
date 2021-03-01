import appdaemon.plugins.hass.hassapi as hass
import math, time
from datetime import datetime

#
# Hellow World App
#
# Args:
#

class ManualDimmer(hass.Hass):

  def initialize(self):
    self.listen_event(self.transitionLight, 'MANUAL_DIM')
    # self.listen_event(self.volumeFade, 'MANUAL_FADE')
    
  def transitionLight(self, event, data, kwargs):
    entity = None
    transition = None
    brightness = None
    try:
        entity = data['entity_id']
        brightness = data['brightness']
    except Exception as e:
        self.log("Error receiving data for manual dim: {}".format(e))
        return

    try:
        transition = data['transition']
    except Exception as e:
        transition = 1

    canDim = self.get_state(entity,attribute='supported_features') & 1
    if (not canDim):
        self.log("Error: entity {} cannot dim".format(entity))

    self.log("INFO - entity:{}".format(entity))
    currentLevel = self.get_state(entity,attribute='brightness')
    if not currentLevel:
        currentLevel = 0
    self.log("INFO - level:{}".format(currentLevel))

    direction = 1 if currentLevel < brightness else -1

    # number of steps the light should take per tick (1/10 of a sec)
    stepsPerTick = abs(currentLevel-brightness)/(transition*10)
    self.log("INFO - stepsPerTick:{}".format(stepsPerTick))

    stepsThisTick = stepsPerTick

    timeError = 0;

    while (currentLevel != brightness):
        lastTime = datetime.now()

        if (stepsThisTick >=1):

            # Round stepsThisTick for this loop
            actualStepsThisTick = (math.floor(stepsThisTick))
            self.log("INFO - actualStepsThisTick = {}".format(actualStepsThisTick))

            # Adjust stepsThisTick for next loop
            stepsThisTick -= actualStepsThisTick

            # Calculate new level
            levelThisTick = currentLevel+(direction*actualStepsThisTick)

            if direction < 0 and levelThisTick < brightness: levelThisTick = brightness
            if direction > 0 and levelThisTick > brightness: levelThisTick = brightness

            self.turn_on(entity, brightness=levelThisTick)

            self.log("INFO - levelThisTick = {}".format(levelThisTick))
            
            currentLevel = levelThisTick
            if not currentLevel:
                currentLevel = 0

        time.sleep(0.1)
        thisTime = datetime.now()
        timeDiffms = (thisTime - lastTime).microseconds/1000
        timeError = timeDiffms - 100
        self.log("total time {} is off by {} milliseconds".format(timeDiffms, timeError))

        self.log("INFO - steps before adjustment:{}".format(stepsThisTick))
        self.log("INFO - adjusting by {}".format(1+(timeError/100)))

        stepsThisTick += stepsPerTick * (1 + (timeError/100))


        self.log("INFO - timeDiff:{} so stepsThisTick is now: {}".format(timeDiffms, stepsThisTick))

    self.log("INFO - manual transition complete")