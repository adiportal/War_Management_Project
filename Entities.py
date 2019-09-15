
class Soldier():

    # Attributes
    ID = 1

    def __init__(self, company_number, location, ammo):
        self.ID = Soldier.ID
        Soldier.ID += 1
        self.company_number = company_number
        self.x = location[0]
        self.y = location[1]
        self.ammo = ammo
        self.hp = 100

    def to_string(self):
        return "Soldier #{}: \n" \
               "Company Number: {} \n" \
               "Location: {} \n" \
               "Ammo: {} \n" \
               "HP: {}".format(self.ID, self.company_number, self.get_location(), self.ammo, self.hp)

    def update_location(self, new_x, new_y):
        self.x = new_x
        self.y = new_y

    def get_location(self):
        return "({}, {})".format(self.x, self.y)


class CompanyCommander():
    # Attributes
    ID = 1

    def __init__(self, company_number, location, ammo):
        self.ID = CompanyCommander.ID
        CompanyCommander.ID += 1
        self.companyNumber = company_number
        self.x = location[0]
        self.y = location[1]
        self.ammo = ammo
        self.hp = 100


