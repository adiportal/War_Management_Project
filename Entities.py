
class Soldier():

    # Attributes
    ID = 1
    companyNumber = 0
    x = 0
    y = 0
    ammo = 0
    HP = 0

    def __init__(self, companyNumber, location, ammo):
        self.ID = Soldier.ID
        Soldier.ID += 1
        self.companyNumber = companyNumber
        self.x = location[0]
        self.y = location[1]
        self.ammo = ammo
        self.HP = 100

    def to_string(self):
        return "Soldier #{}: \n" \
               "Company Number: {} \n" \
               "Location: ({}, {}) \n" \
               "Ammo: {} \n" \
               "HP: {}".format(self.ID, self.companyNumber, self.x, self.y, self.ammo, self.HP)

class CompanyCommander():
    # Attributes
    ID = 1
    companyNumber = 0
    x = 0
    y = 0
    ammo = 0
    HP = 0

    def __init__(self, companyNumber, location, ammo):
        self.ID = CompanyCommander.ID
        CompanyCommander.ID += 1
        self.companyNumber = companyNumber
        self.x = location[0]
        self.y = location[1]
        self.ammo = ammo
        self.HP = 100


