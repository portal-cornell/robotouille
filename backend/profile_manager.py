class Profile:
    def __init__(self, player_id, name, picture):
        self.player_id = player_id
        # Pre defined avatars (hair, ...)
        self.name = name
        self.picture = picture
        self.play_again_status = "PENDING"


class ProfileManager:
    def __init__(self):
        self.profiles = {}  # player_id -> Profile

    def add_profile(self, player_id, name, picture):
        self.profiles[player_id] = Profile(player_id, name, picture)

    def update_status(self, player_id, status):
        if player_id in self.profiles:
            self.profiles[player_id].play_again_status = status

    def get_profiles(self):
        return [
            {
                "id": p.player_id,
                "name": p.name,
                "picture": p.picture,
                "status": p.play_again_status
            }
            for p in self.profiles.values()
        ]

    def get_statuses(self):
        return {
            p.player_id: p.play_again_status
            for p in self.profiles.values()
        }