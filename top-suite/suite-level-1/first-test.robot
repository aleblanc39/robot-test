*** Settings ***

Resource     SuiteKeywords.robot



*** Test Cases ***

My First Test
    Log    Running a test
    @{myList}=    create list
    :FOR    ${index}    IN RANGE    10
    \    Log    ${index}
