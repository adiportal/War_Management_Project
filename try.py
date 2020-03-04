import Utility

company_commander_scenario = Utility.load("CompanyCommanderScenarios/CompanyCommander1Scenario 04-03-2020 16.07.03")
field_scenario = Utility.load("FieldScenarios/Field_Scenario 04-03-2020 16.06.59")

cc_messages = company_commander_scenario.get_messages()
field_messages = field_scenario.get_messages()

print(company_commander_scenario.get_message("16:08:51"))
print(company_commander_scenario.get_message("16:08:51")[0].get_colored_msg())

# for message in cc_messages:
#     print(message, message.get_time())
#
# print()
#
# for message in field_messages:
#     print(message, message.get_time())