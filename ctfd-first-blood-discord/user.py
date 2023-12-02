class User:
    user_id: int
    user_name: str
    team_name: str

    def __init__(self, user_id: int, user_name: str, team_name: str):
        self.user_id = user_id
        self.user_name = user_name
        self.team_name = team_name
