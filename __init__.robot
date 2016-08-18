*** Settings ***

Resource     top-suite/SuiteKeywords.robot



Test Teardown    Finish This

Suite Setup      Start Suite

*** Keywords ***

Finish This
    log    time to finish this

Start Suite
    log    Starting Suite