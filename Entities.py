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

    def get_ammo(self):
        return self.ammo

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    def update_location(self, new_x, new_y):
        self.x = new_x
        self.y = new_y


class Soldier(FieldObjects):
    def __init__(self, company_number, location, ammo):
        super().__init__(company_number, location, ammo)
        self.HP = 100
        self.speed = 1

    def get_speed(self):
        return self.speed


class BTW(FieldObjects):
    def __init__(self, company_number, location, ammo):
        super().__init__(company_number, location, ammo)
        self.HP = 1000
        self.speed = 2

    def get_speed(self):
        return self.speed


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


class Packet:
    ID = 1

    def __init__(self, sender, company_num, receiver, message_type, message):
        self.ID = Packet.ID
        Packet.ID += 1
        self.sender = sender
        self.company_num = company_num
        self.receiver = receiver
        self.message_type = message_type
        self.message = message

    def get_id(self):
        return self.ID

    def get_sender(self):
        return self.sender

    def get_company_num(self):
        return self.company_num

    def get_receiver(self):
        return self.receiver

    def get_message_type(self):
        return self.message_type

    def get_message(self):
        return self.message

    def __str__(self):
        return "[ Sender: {}, Company: {}, Receiver: {}, Message Type: {}, Message: {} ]".format(self.sender,
                                                                                                 self.company_num,
                                                                                                 self.receiver,
                                                                                                 self.message_type,
                                                                                                 self.message)


class InitMessage:

    def __init__(self, field_object):
        self.field_object = field_object

    def __str__(self):
        return "|| ID: {}, Company: {}, Location: {}, Ammo: {} ||".format(self.field_object.get_id(),
                                                                          self.field_object.get_company_num(),
                                                                          self.field_object.get_location(),
                                                                          self.field_object.get_ammo())


class UpdateFieldObjectMessage:

    def __init__(self, field_object):
        self.field_object = field_object

    def __str__(self):
        return "|| ID: {}, Company: {}, Location: {}, Ammo: {} ||".format(self.field_object.get_id(),
                                                                          self.field_object.get_company_num(),
                                                                          self.field_object.get_location(),
                                                                          self.field_object.get_ammo())


class MoveOrderMessage:

    def __init__(self, company_num, field_object_id, location):
        self.company_num = company_num
        self.field_object_id = field_object_id
        self.location = location

    def __str__(self):
        return "|| Company: {}, ID: {}, MoveTo Location: {} ||".format(self.company_num,
                                                                       self.field_object_id,
                                                                       self.location)

