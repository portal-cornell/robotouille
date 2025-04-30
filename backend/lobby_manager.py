from .profile_manager import ProfileManager

class LobbyManager:
    def __init__(self):
        self.profile_manager = ProfileManager()
        self.players_in_lobby = []  # List of player_ids

    def add_player(self, player_id, name, picture):
        self.profile_manager.add_profile(player_id, name, picture)
        self.players_in_lobby.append(player_id)

    def get_lobby_profiles(self):
        return self.profile_manager.get_profiles()

    def update_play_again_status(self, player_id, status):
        self.profile_manager.update_status(player_id, status)

    def get_play_again_statuses(self):
        return self.profile_manager.get_statuses()