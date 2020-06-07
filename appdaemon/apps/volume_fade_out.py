import appdaemon.plugins.hass.hassapi as hass
import math, time
from datetime import datetime

#
# Hellow World App
#
# Args:
#

class VolumeFader(hass.Hass):

  def initialize(self):
    self.listen_event(self.fadeOut, 'VOLUME_FADE_START')
    
  def fadeOut(self, event, data, kwargs):
    entity = None
    transition = None
    volume = None
    try:
        entity = data['entity_id']
        transition = data['transition']
        volume = data['volume']
    except Exception as e:
        self.log("Error receiving data for fade out: {}".format(e))
        return

    self.log("INFO - entity:{}".format(entity))
    currentLevel = self.get_state(entity,attribute='volume')
    if not currentLevel:
        currentLevel = 0
    self.log("INFO - level:{}".format(currentLevel))

    direction = 1 if currentLevel < volume else -1

    # number of steps the light should take per tick (1/10 of a sec)
    stepsPerTick = abs(currentLevel-volume)/(transition*10)
    self.log("INFO - stepsPerTick:{}".format(stepsPerTick))

    stepsThisTick = stepsPerTick

    timeError = 0;

    while (currentLevel != volume):
        lastTime = datetime.now()

        if (stepsThisTick >=1):

            # Round stepsThisTick for this loop
            actualStepsThisTick = (math.floor(stepsThisTick))
            self.log("INFO - actualStepsThisTick = {}".format(actualStepsThisTick))

            # Adjust stepsThisTick for next loop
            stepsThisTick -= actualStepsThisTick

            # Calculate new level
            levelThisTick = currentLevel+(direction*actualStepsThisTick)

            if direction < 0 and levelThisTick < volume: levelThisTick = volume
            if direction > 0 and levelThisTick > volume: levelThisTick = volume

            self.turn_on(entity, volume=levelThisTick)

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