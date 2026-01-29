class Ami:
    def __init__(self, ami_infos:dict):
        self.username = ami_infos.get("username")
        self.id = ami_infos.get("user_id")
        self.mail = ami_infos.get("mail")
        self.phone = ami_infos.get("phone")
        self.date_of_birth = ami_infos.get("date_of_birth")
        self.avatar_id = ami_infos.get("avatar_id")

        self.status = "online"