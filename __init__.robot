*** Settings ***

Resource     SuiteKeywords.robot


# If uncommenting the following we receive a message that
# keyword Finish All not found
# It won't work if I define Finish All in the Keywords section
# of this file as well
Test Teardown    Finish All

# This, on the other hand, works fine.
# Make sure only one of the Test Test Teardown  definition
# is not commented
#Test Teardown    Log    Is this breaking as well?

Suite Setup      Start Suite

*** Keywords ***

Start Suite
    log    Starting Suite