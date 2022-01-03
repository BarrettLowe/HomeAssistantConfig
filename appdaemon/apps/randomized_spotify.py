import appdaemon.plugins.hass.hassapi as hass
import random

# RandomizedSpotify 
# listens for the RANDOM_MUSIC event
# Keywords:
#   playlists - a list of playlists to be chosen at random OR a string of comma separated playlist URIs
#   speakers - a list of speakers (full entity id)

class RandomizedSpotify(hass.Hass):

    def initialize(self):
        self.listen_event(self.playRandom, 'RANDOM_MUSIC')
        
    def setShuffle(self, on:bool):
        self.call_service("media_player/shuffle_set", entity_id="media_player.mpd", shuffle=on)

    def playRandom(self, event, data, kwargs):

        try:
            playlists = data['playlists']
            speakers = data['speakers']
        except Exception as e:
            raise e

        if type(playlists) == str:
            playlists = playlists.split(',')
            playlists = [x.strip() for x in playlists]

        chosenPlaylist = random.choice(playlists)

        self.setShuffle(True)

        for speaker in speakers:
            self.call_service("media_player/select_source", source="HomeAssistantUI", entity_id=speaker)

        self.call_service("media_player/play_media", entity_id="media_player.mpd", media_content_id=chosenPlaylist, media_content_type="music")