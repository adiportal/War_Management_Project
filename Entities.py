
class Soldier():

    # Attributes
    ID = 1

    def __init__(self, companyNumber, location, ammo):
        self.ID = Soldier.ID
        Soldier.ID += 1
        self.companyNumber = companyNumber
        self.x = location[0]
        self.y = location[1]
        self.ammo = ammo
        self.HP = 100
        self.picked = False

    def to_string(self):
        return "Soldier #{}: \n" \
               "Company Number: {} \n" \
               "Location: ({}, {}) \n" \
               "Ammo: {} \n" \
               "HP: {} \n" \
               "Picked: {}".format(self.ID, self.companyNumber, self.x, self.y, self.ammo, self.HP, str(self.picked))

    def update_location(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

    def get_location(self):
        return "({}, {})".format(self.x, self.y)

    def pick(self):
        self.picked = True

    def unpick(self):
        self.picked = False


class CompanyCommander():
    # Attributes
    ID = 1

    def __init__(self, companyNumber, location, ammo):
        self.ID = CompanyCommander.ID
        CompanyCommander.ID += 1
        self.companyNumber = companyNumber
        self.x = location[0]
        self.y = location[1]
        self.ammo = ammo
        self.HP = 100


