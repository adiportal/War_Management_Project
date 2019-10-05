import time
import Utility


class FieldObjects:
    # Attributes
    ID = 1

    def __init__(self, company_number, location, ammo):
        self.ID = FieldObjects.ID
        FieldObjects.ID += 1
        self.company_number = company_number
        self.x = location[0]
        self.y = location[1]
        self.ammo = ammo

    def __str__(self):
        return "{} #{}: \n" \
               "Company Number: {} \n" \
               "Location: ({}, {}) \n" \
               "Ammo: {} \n" \
               "HP: {} \n".format(self.__class__.__name__, self.ID, self.company_number, self.x, self.y, self.ammo,
                                  self.HP)

    def get_company_num(self):
        return self.company_number

    def get_id(self):
        return self.ID

    def get_location(self):
        return self.x, self.y

    def get_str_location(self):
        return str(self.x) + "," + str(self.y)

    def update_location(self, x, y):
        self.x == x
        self.y = y

    def move_to(self, new_x, new_y):
        start = self.x, self.y
        end = new_x, new_y

        steps = Utility.get_line(start, end)
        for step in steps:
            time.sleep(self.speed)
            self.x = step[Utility.Location.X.value]
            self.y = step[Utility.Location.Y.value]
            print(self.x, self.y)
        time.sleep(self.speed)
        self.x = new_x
        self.y = new_y


class Soldier(FieldObjects):
    def __init__(self, company_number, location, ammo):
        super().__init__(company_number, location, ammo)
        self.HP = 100
        self.speed = 1


class BTW(FieldObjects):
    def __init__(self, company_number, location, ammo):
        super().__init__(company_number, location, ammo)
        self.HP = 1000
        self.speed = 2


class CompanyCommander:
    # Attributes
    ID = 1

    def __init__(self, company_number, location, ammo):
        self.ID = CompanyCommander.ID
        CompanyCommander.ID += 1
        self.company_number = company_number
        self.x = location[0]
        self.y = location[1]
        self.ammo = ammo
        self.HP = 100
