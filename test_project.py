from project import clean_number, compare_two_brnumbers, check_brcontact


def test_clean_number():
    assert clean_number({"Phone 1 - Value": "+5511992979999"})["Phone 1 - Edited"] == "5511992979999"
    assert clean_number({"Phone 1 - Value": "+551192979999"})["Phone 1 - Edited"] == "551192979999"
    assert clean_number({"Phone 1 - Value": "8888-8888"})["Phone 1 - Edited"] == "88888888"
    assert clean_number({"Phone 1 - Value": "2000-8888"})["Phone 1 - Edited"] == "20008888"


def test_compare_two_brnumbers():
    contact = list()
    contact.append(check_brcontact(clean_number({"Phone 1 - Value": "+55 48 98415-0196"})))
    contact.append(check_brcontact(clean_number({"Phone 1 - Value": "(48) 98415-0196"})))
    contact.append(check_brcontact(clean_number({"Phone 1 - Value": "+551172978888"})))
    contact.append(check_brcontact(clean_number({"Phone 1 - Value": "+5513992978888"})))
    contact.append(check_brcontact(clean_number({"Phone 1 - Value": "+5587992978888"})))
    contact.append(check_brcontact(clean_number({"Phone 1 - Value": "+558792978888"})))
    contact.append(check_brcontact(clean_number({"Phone 1 - Value": "+551122222222"})))

    assert compare_two_brnumbers(contact[0], contact[1]) == True
    assert compare_two_brnumbers(contact[0], contact[2]) == False
    assert compare_two_brnumbers(contact[0], contact[3]) == False
    assert compare_two_brnumbers(contact[4], contact[5]) == True
    assert compare_two_brnumbers(contact[4], contact[6]) == False
    assert compare_two_brnumbers(contact[2], contact[6]) == False


def test_check_brcontact():
    check_brcontact(clean_number({"Phone 1 - Value": "+55 48 98415-0196"}))["Is BrNumber"] == True
    check_brcontact(clean_number({"Phone 1 - Value": "+1 485 985 0196"}))["Is BrNumber"] == False
    check_brcontact(clean_number({"Phone 1 - Value": "+556 48 98415-0196"}))["Is BrNumber"] == True
    check_brcontact(clean_number({"Phone 1 - Value": "+556 48 98415-0196"}))["Tipo"] == "Invalido"
    check_brcontact(clean_number({"Phone 1 - Value": "+55 48 98415-0196"}))["Tipo"] == "Celular"
    check_brcontact(clean_number({"Phone 1 - Value": "+55 13 4415-0196"}))["Tipo"] == "Fixo"
    check_brcontact(clean_number({"Phone 1 - Value": "+55 48 98415-0196"}))["8 digits"] == 84150196
