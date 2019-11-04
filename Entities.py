import Utility


# FieldObject
class FieldObjects:
    # Attributes
    ID = 1

    # Constructor
    def __init__(self, company_number, location, ammo):
        self.ID = FieldObjects.ID
        FieldObjects.ID += 1
        self.company_number = company_number
        self.x = location[0]
        self.y = location[1]
        self.ammo = ammo

    # toString
    def __str__(self):
        return "{} #{}: \n" \
               "Company Number: {} \n" \
               "Location: ({}, {}) \n" \
               "Ammo: {} \n" \
               "HP: {} \n".format(self.__class__.__name__, self.ID, self.company_number, self.x, self.y, self.ammo,
                                  self.HP)

    # Getters
    def get_company_num(self):
        return self.company_number

    def get_id(self):
        return self.ID

    def get_location(self):
        return self.x, self.y

    def get_str_location(self):
        return str(self.x) + ", " + str(self.y)

    def get_ammo(self):
        return self.ammo

    def get_x(self):
        return self.x

    def get_y(self):
        return self.y

    # update_location(new_x, new_y) - update the FieldObject location
    def update_location(self, new_x, new_y):
        self.x = new_x
        self.y = new_y


# Soldier
class Soldier(FieldObjects):
    # Constructor
    def __init__(self, company_number, location, ammo):
        super().__init__(company_number, location, ammo)
        self.HP = 100
        self.speed = 0.2

    # Getters
    def get_speed(self):
        return self.speed

    def get_hp(self):
        return self.HP


# BTW
class BTW(FieldObjects):
    # Constructor
    def __init__(self, company_number, location, ammo):
        super().__init__(company_number, location, ammo)
        self.HP = 1000
        self.speed = 0.6

    # Getters
    def get_speed(self):
        return self.speed

    def get_hp(self):
        return self.HP


# CompanyCommander
class CompanyCommander:
    # Attributes
    ID = 1

    # Constructor
    def __init__(self, company_number, location, ammo):
        self.ID = CompanyCommander.ID
        CompanyCommander.ID += 1
        self.company_number = company_number
        self.x = location[0]
        self.y = location[1]
        self.ammo = ammo
        self.HP = 100

    # Setters
    def set_location(self, location):
        self.x = location[0]
        self.y = location[1]

    def set_company(self, company_num):
        self.company_number = company_num


# Packet
class Packet:
    # Attributes
    ID = 1

    # Constructor
    def __init__(self, sender, company_num, receiver, message_type, message):
        self.ID = Packet.ID
        Packet.ID += 1
        self.sender = sender
        self.company_num = company_num
        self.receiver = receiver
        self.message_type = message_type
        self.message = message
        self.approved = False
        self.bc_approval = False

    # Getters
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

    def is_approved(self):
        return self.approved

    def is_bc_approved(self):
        return self.bc_approval

    # set_approval(status) - change the packet approval to the boolean variable that it gets
    def set_approval(self, status):
        self.approved = status

    # bc_approval(status) - change the packet approval to the boolean variable that it gets
    def bc_approval(self, status):
        self.bc_approval = status

    # toString
    def __str__(self):

        if self.sender == Utility.Sender.soldier.value:
            sender = "Soldier"
        elif self.sender == Utility.Sender.company_commander.value:
            sender = "CC"
        else:
            sender = "BC"

        if self.receiver == Utility.Receiver.soldier.value:
            receiver = "Soldier"
        elif self.receiver == Utility.Receiver.company_commander.value:
            receiver = "CC"
        else:
            receiver = "BC"

        if self.message_type == Utility.MessageType.alive.value:
            message_type = "Alive"
        elif self.message_type == Utility.MessageType.move_order.value:
            message_type = "Move Order"
        else:
            message_type = "Engage Order"

        return "[ #{}. Sender: {}, Company: {}, Receiver: {}, Message Type: {}, Message: {} ]".format(self.ID,
                                                                                                      sender,
                                                                                                      self.company_num,
                                                                                                      receiver,
                                                                                                      message_type,
                                                                                                      self.message)


# AliveMessage
class AliveMessage:
    # Constructor
    def __init__(self, field_object):
        self.field_object = field_object

    # toString
    def __str__(self):
        return "|| ID: {}, Company: {}, Location: ({}), HP: {}, Ammo: {} ||".format(self.field_object.get_id(),
                                                                                    self.field_object.get_company_num(),
                                                                                    self.field_object.get_location(),
                                                                                    self.get_hp(),
                                                                                    self.field_object.get_ammo())

    # Getters
    def get_field_object(self):
        return self.field_object

    # toString
    def __str__(self):
        return "|| ID: {}, Company: {}, Location: {}, HP: {}, Ammo: {} ||".format(self.field_object.get_id(),
                                                                                  self.field_object.get_company_num(),
                                                                                  self.field_object.get_location(),
                                                                                  self.field_object.get_hp(),
                                                                                  self.field_object.get_ammo())


# MoveOrderMessage
class MoveOrderMessage:
    # Constructor
    def __init__(self, company_num, field_object_id, location):
        self.company_num = company_num
        self.field_object_id = field_object_id
        self.location = location

    # Getters
    def get_company_num(self):
        return self.company_num

    def get_field_object_id(self):
        return self.field_object_id

    def get_new_location(self):
        return self.location

    # toString
    def __str__(self):
        return "|| Company: {}, ID: {}, MoveTo Location: ({}) ||".format(self.company_num,
                                                                         self.field_object_id,
                                                                         self.location)
