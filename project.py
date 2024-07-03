import csv
import io
import re
import time
start_time = time.time()
changes = True
folder = "output1" if changes else "output0"

def main():
    print("VERAZ DB MERGE\n")

    # Import Databases
    db_names = {
        "whatsapp": "./files/Contatos Google WP.csv",
        "enrolled": "./files/Contatos Alunos Matriculados Original.csv"
    }

    whatsapp = import_db(db_names["whatsapp"], "whatsapp", filter1="AlunoVeraz", filter2="Ph")
    enrolled = import_db(db_names["enrolled"], "enrolled")
    wp_len = len(whatsapp)
    en_len = len(enrolled)

    # Get original keys list
    contact_titles = list(whatsapp[0].keys())
    contact_titles.remove("Phone 1 - Edited")

    global changes
    if changes:
        # Make the necessary corrections before Merge databases #######################################
        whatsapp = make_changes(whatsapp, "whatsapp")
        enrolled = make_changes(enrolled, "enrolled")

    # CHECK SEVERAL ITEMS ON PHONE NUMBERS:
    # Check valid format of Brazilian number
    whatsapp = check_brnumber(whatsapp, "whatsapp")
    enrolled = check_brnumber(enrolled, "enrolled")

    # Check + in the start of the number
    check_plus(whatsapp, "whatsapp")
    check_plus(enrolled, "enrolled")

    # Check any empty number
    check_emptynumber(whatsapp, "whatsapp")
    check_emptynumber(enrolled, "enrolled")


    # Merge Enrolled database into Whatsapp database
    whatsapp = compare_enrolled_in_whatsapp(enrolled, whatsapp)

    # Name correctly each contact: AlunoOutSP2-FirstnameSecondname
    whatsapp = adjust_names(whatsapp)

    # Check duplicates of the number
    check_duplicates(whatsapp, "whatsapp")
    check_duplicates(enrolled, "enrolled")

    # Output the final database
    output_database(whatsapp, contact_titles,"Final Database")

    print("Whatsapp database:", wp_len, "contacts")
    print("Enrolled database:", en_len, "contacts")
    print("Merged database:", len(whatsapp), "contacts")
    print("--- %s seconds ---" % (time.time() - start_time))


def import_db(file, name, filter1=None, filter2=None):
    """ Import databases from CSV files into memory """
    database = []

    with io.open(file, "r", newline='', encoding="utf8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if filter1 is None or row["Name"].startswith(filter1) or row["Name"].startswith(filter2):
                row = clean_number(row)
                row["Name"].strip()
                database.append(row)

    print("0. Database", name, "imported correcly.")
    return database


def clean_number(row):
    row["Phone 1 - Value"] = row["Phone 1 - Value"].strip()
    phone = ''.join(c for c in row["Phone 1 - Value"] if c.isnumeric())
    row["Phone 1 - Edited"] = phone
    return row


def check_brnumber(db, name):
    for contact in db:
        contact = check_brcontact(contact)

    global folder
    with open("./" + folder +"/1. Check BrNumber " + name + ".txt", "w", newline="\n") as file:
        contatos_invalidos, contatos_fixo, contatos_celular = "", "", ""

        db2 = sorted(db, key = lambda contact: contact["Name"])
        db2 = sorted(db2, key = lambda contact: len(contact["Phone 1 - Edited"]))

        for contact in db2:
            if contact["Is BrNumber"]:
                if contact["Tipo"] == "Invalido":
                    contatos_invalidos += print_contact(contact)
                elif contact["Tipo"] == "Fixo":
                    contatos_fixo += print_contact(contact)
                elif contact["Tipo"] == "Celular":
                    contatos_celular += print_contact(contact)

        file.write("INVALID BRAZILIAN NUMBERS\n")
        file.write(contatos_invalidos)

        file.write("\n\nFIXO\n")
        file.write(contatos_fixo)

        file.write("\n\nCELULAR\n")
        file.write(contatos_celular)

    print("1. BR Numbers checked on", name, "database.")
    return db


def check_brcontact(contact):
    # Check the +55 for Brazilian or foreign numbers
    contact["Is BrNumber"] = not (contact["Phone 1 - Value"].startswith("+") and not contact["Phone 1 - Value"].startswith("+55"))

    # Check the format for Brazilian numbers (mobile and fix) (19) 3801-6321

    contact["8 digits"] = int(contact["Phone 1 - Edited"][-8:]) if contact["Phone 1 - Edited"] !="" else 0
    if contact["Is BrNumber"]:
        phone_regex = re.search(r"^((?:55)?[1-9]{2})?(9)?([0-9]{8})$", contact["Phone 1 - Edited"])

        if phone_regex:
            if phone_regex.group(1):
                contact["DDD"] = int(phone_regex.group(1)[-2:])
                if len(phone_regex.group(1)) == 4:
                    contact["DDI"] = int(phone_regex.group(1)[0:2])
                else:
                    contact["DDI"] = 55
            else:
                contact["DDI"] = 55
                contact["DDD"] = 11

            contact["Leading9"] = phone_regex.group(2)
            contact["8 digits"] = phone_regex.group(3)

            if not contact["Leading9"] and (2 <= int(contact["8 digits"][0]) <= 5):
                contact["Tipo"] = "Fixo"
            elif contact["Leading9"] or (6 <= int(contact["8 digits"][0]) <= 9):
                contact["Tipo"] = "Celular"
            else:
                contact["Tipo"] = "Invalido"
            contact["8 digits"] = int(contact["8 digits"])
        else:
            contact["Tipo"] = "Invalido"


        if contact["Tipo"] != "Invalido":
            contact["Phone 1 - Formated"] = "+" + str(contact["DDI"]) + " " + str(contact["DDD"]) + " "
            contact["Phone 1 - Formated"] += contact["Leading9"] + "-" if contact["Leading9"] else "  "
            contact["Phone 1 - Formated"] += str(contact["8 digits"])[:4] + "-" + str(contact["8 digits"])[4:]
            contact["10 digits"] = int(str(contact["DDD"]) + str(contact["8 digits"]))
        else:
            contact["Phone 1 - Formated"] = " "*18


    contact["Phone 1 - Formated"] = " "*18 if "Phone 1 - Formated" not in contact else contact["Phone 1 - Formated"]
    contact["10 digits"] = contact["Phone 1 - Edited"] if "10 digits" not in contact else contact["10 digits"]

    return contact


def check_plus(db, name):
    # Check if there is a plus sign in the first 3 caracters
    global folder
    with open("./" + folder +"/2. Check + " + name + ".txt", "w", newline="\n") as file:
        file.write("CONTACTS WITH PLUS + THAT ARE NOT FROM BRAZIL (+55)\n")
        for contact in db:
            if '+' in contact["Phone 1 - Value"][:3] and contact["Is BrNumber"] == False:
                file.write(print_contact(contact))
        file.write("\n"*2)
        file.write("CONTACTS WITH PLUS + THAT ARE FROM BRAZIL (+55)\n")
        for contact in db:
            if '+' in contact["Phone 1 - Value"][:3] and contact["Is BrNumber"] == True:
                file.write(print_contact(contact))
    print("2. Inicial plus + checked on", name, "database.")



def check_emptynumber(db, name):
    global folder
    with open("./" + folder +"/3. Check Empty Number " + name + ".txt", "w", newline="\n") as file:
        file.write("EMPTY NUMBERS\n")
        for contact in db:
            if not contact["Phone 1 - Value"]:
                file.write(print_contact(contact))

        file.write("\n"*2)
        file.write("EMPTY NAMES\n")
        for contact in db:
            if not contact["Name"]:
                file.write(print_contact(contact))

    print("3. Empty numbers and names checked on", name, "database.")


def check_duplicates(db, name):
    variables = ["Name", "8 digits"]
    duplicate_dict = {}

    for v in variables:
        list_of_v = []
        for contact in db:
            if "Exclude" in contact:
                if not contact["Exclude"]:
                    list_of_v.append(contact[v])
            else:
                list_of_v.append(contact[v])


        seen = set()
        duplicates = set()

        for item in list_of_v:
            if item in seen:
                duplicates.add(item)
            else:
                seen.add(item)

        duplicate_dict[v] = list(duplicates)

    global folder
    with io.open("./" + folder +"/7. Check Duplicates " + name + ".txt", "w", newline="\n", encoding="utf8") as file:
        file.write("DUPLICATES OF NAMES\n")
        for contact in db:
            if contact["Name"] in duplicate_dict["Name"]:
                file.write(print_contact(contact))

        file.write("\n"*2)
        file.write("DUPLICATES OF PHONE NUMBERS\n")
        for contact in sorted(db, key=lambda contact: contact["8 digits"]):
            if contact["8 digits"] in duplicate_dict["8 digits"]:
                file.write(print_contact(contact))

    print("7. Duplicates checked on", name, "database.")


def make_changes(db, name):
    changes_file = "./files/changes.csv"
    actions = []
    new_db = []
    adjust, deleted, nothing = "","", ""
    with io.open(changes_file, encoding="utf8", newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            actions.append(row)

    for contact in db:
        contact["Action"] = "nothing"
        for row in actions:
            if row["Name"] == contact["Name"] and row["Phone 1 - Value"] == contact["Phone 1 - Value"] and row["database"] == name:
                    if row["Action"] == "adjust":
                        contact["Name"] = row["Name New"]
                        contact["Phone 1 - Value"] = row["Phone 1 - Value New"]
                        contact["Comment"] = row["Comment"]
                        contact["Action"] = "adjust"
                        contact = clean_number(contact)

                    elif row["Action"] == "delete":
                        contact["Comment"] = row["Comment"]
                        contact["Action"] = "delete"

    for contact in db:
        if contact["Action"] == "delete":
            deleted += contact["Name"][:35].ljust(35) + contact["Phone 1 - Value"] + contact["Comment"] + "\n"
        elif contact["Action"] == "adjust":
            adjust += contact["Name"][:35].ljust(35) + contact["Phone 1 - Value"] + contact["Comment"] + "\n"
            new_db.append(contact)
        elif contact["Action"] == "nothing":
            nothing += contact["Name"][:35].ljust(35) + contact["Phone 1 - Value"] + "\n"
            new_db.append(contact)

    global folder
    with open("./" + folder +"/0.A. Changes " + name + ".txt", "w", newline="\n") as file:
        file.write("ADJUSTED NUMBERS, first the adjusted, second the original\n")
        file.write(adjust)

        file.write("\n"*2)
        file.write("DELETED NUMBERS\n")
        file.write(deleted)

        file.write("\n"*2)
        file.write("AS IS: NO CHANGES\n")
        file.write(nothing)

    print("0.A. Changes in", name, "database correctly made (duplicates, wrong numbers, etc).")
    return new_db


def compare_enrolled_in_whatsapp(enrolled, whatsapp):
    found = 0

    # Create a set to store phone numbers of enrolled contacts
    enrolled_phone_numbers = [cont_enrolled["10 digits"] for cont_enrolled in enrolled]

    for cont_whatsapp in whatsapp:
        cont_whatsapp["Enrolled"] = cont_whatsapp["10 digits"] in enrolled_phone_numbers
        cont_whatsapp["New contact"] = False

    # Filter out the contacts from enrolled that are not found in whatsapp
    whatsapp_phone_numbers = [cont_whatsapp["10 digits"] for cont_whatsapp in whatsapp]
    for cont_enrolled in enrolled:
        cont_enrolled["Exclude"] = cont_enrolled["10 digits"] in whatsapp_phone_numbers
        cont_enrolled["Enrolled"] = True
        cont_enrolled["New contact"] = not cont_enrolled["Exclude"]

    new_enrolled_contact = [cont_enrolled for cont_enrolled in enrolled if cont_enrolled["New contact"]]
    whatsapp += new_enrolled_contact


    global folder
    with open("./" + folder +"/4. Database merge.txt", "w", newline="\n") as file:
        file.write("CONTATOS DO WHATSAPP ENCONTRADOS NOS MATRICULADOS\n")
        for cont_enrolled in sorted(enrolled, key=lambda cont_enrolled: cont_enrolled["Name"]):
            if cont_enrolled["Exclude"]:
                file.write(print_contact(cont_enrolled))

        file.write("\n"*2)
        file.write("CONTATOS DO WHATSAPP NÃO ENCONTRADOS NOS MATRICULADOS\n")
        for cont_enrolled in sorted(enrolled, key=lambda cont_enrolled: cont_enrolled["Name"]):
            if not cont_enrolled["Exclude"]:
                file.write(print_contact(cont_enrolled))

    print("4. Databases merged on Whatsapp database.")
#    print("Found contacts =", found)
#    print("New contacts   =", not_found)
    return whatsapp


def compare_two_brnumbers(contact1, contact2):
    # Compare 2 Br Phone Numbers, return True if equal phone numbers, False if different

    direct_comparison = contact1["Phone 1 - Edited"] == contact2["Phone 1 - Edited"]

    ## Algorithm:
    ### if Brazilian number and Valid, compare numbers directly with DDD and 8 digits
    ### if Brazilian number and invalid, compare digits only (full number)
    if contact1["Is BrNumber"] and contact2["Is BrNumber"]:
        if contact1["Tipo"] != "Invalido" and contact2["Tipo"] != "Invalido":
            return contact1["DDD"] == contact2["DDD"] and contact1["8 digits"] == contact2["8 digits"]
        else:
            return direct_comparison

    ### else, meaning it's a foreign phone number, compare digits only (full number)
    else:
        return direct_comparison


def adjust_names(whatsapp):
    # Replace "AlunoVeraz" by "Aluno"
    # Replace "Aluno-" by "Aluno1-"
    # If new contact, title() contact, then remove spaces
        # If DDD in [11, 12, 13, 15, 19] then Aluno5XX-
        # Else then AlunoOutSP3XX-
    for contact in whatsapp:
        contact["Name"] = contact["Name"].strip().replace("AlunoVeraz", "Aluno").replace("Aluno-", "Aluno1-")
        contact["Name"] = contact["Name"].replace("AlunoOutSp", "AlunoOutSP").replace("AlunoOutSP-", "AlunoOutSP1-")
        contact["New contact"] = False if "New contact" not in contact else contact["New contact"]
        contact["Enrolled"] = False if "Enrolled" not in contact else contact["Enrolled"]

        if contact["New contact"]:
            contact["Name"] = contact["Name"].title().replace(" ", "")

            if "DDD" in contact:
                if contact["Estado"].upper() == "SP":
                    contact["Name"] = "Aluno5XX-" + contact["Name"]
                elif int(contact["DDD"]) in [11, 12, 13, 15, 19]:
                    contact["Name"] = "Aluno5XX-" + contact["Name"]
                else:
                    contact["Name"] = "AlunoOutSP3XX-" + contact["Name"]
            else:
                contact["Name"] = "AlunoOutSP3XX-" + contact["Name"]

        elif contact["Enrolled"]:
            # Incluir XX nos nomes atuais
            split_name = contact["Name"].split("-")
            temp_name = split_name[0] + "XX-"
            for n in split_name[1:]:
                temp_name += n

            contact["Name"] = temp_name

        contact["Given Name"] = contact["Name"]
        contact["Phone 1 - Type"] = "Celular" if "Phone 1 - Type" not in contact else contact["Phone 1 - Type"]
        contact["Group Membership"] = "* myContacts"

    prefixo = {}
    alunos = 0
    global folder
    with open("./" + folder +"/5. Adjusted Names.txt", "w", newline="\n") as file:
        file.write("FINAL DATABASE MERGED WITH CORRECTED NAMES\n\n")
        for contact in sorted(whatsapp, key = lambda contact: contact["Name"]):
            prefix_name = contact["Name"].split("-")
            if prefix_name[0] in prefixo:
                prefixo[prefix_name[0]] += 1
            else:
                prefixo[prefix_name[0]] = 1
            if "XX" in prefix_name[0]:
                alunos += 1

            file.write(print_contact(contact))


    print("5. Names adjusted on whatsapp database.")
    grupos = prefixo.keys()
    group_list = {}
    for k in grupos:
        g = k.replace("XX","")
        if g not in group_list:
            group_list[g] = {"LT": 0, "ENROLLED": 0}

        if "XX" not in k:
            group_list[g]["LT"] = prefixo[k]
        else:
            group_list[g]["ENROLLED"] = prefixo[k]


    total = {"LT": 0, "ENROLLED": 0, "TOTAL": 0}
    with open("./" + folder +"/6. Stats summary.txt", "w", newline="\n") as file:
        file.write("    " + "GRUPO".ljust(13) + str("LISTA").rjust(6) + str("ENROL").rjust(6) + str("TOTAL").rjust(6) + "\n")
        for k in group_list.keys():
            lt, enrolled, both = group_list[k]["LT"], group_list[k]["ENROLLED"], group_list[k]["LT"] + group_list[k]["ENROLLED"]
            total["LT"] += lt
            total["ENROLLED"] += enrolled
            total["TOTAL"] += both
            file.write("    " + k[:13].ljust(13) + str(lt).rjust(6) + str(enrolled).rjust(6) + str(both).rjust(6) + "\n")
        file.write("    " + "TOTAL ALUNOS".ljust(13) + str(total["LT"]).rjust(6) + str(total["ENROLLED"]).rjust(6) + str(total["TOTAL"]).rjust(6) + "\n")
    print("6. Stats summary saved.")

    return whatsapp


def output_database(whatsapp, keys, filename):
    global folder
    with open("./" + folder +"/8. " + filename + ".csv", "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=keys)
        writer.writeheader()
        for contact in sorted(whatsapp, key=lambda contact:contact["Name"]):
            temp_contact = {}
            for k in keys:
                if k in contact:
                    temp_contact[k] = contact[k]
                else:
                    temp_contact[k] = ""

            writer.writerow(temp_contact)

    print("8. Final whatsapp database recorded in csv file.")


def print_contact(c):
    s = c["Name"][:35].ljust(35) + "  " + c["Phone 1 - Formated"] + " "*3 + c["Phone 1 - Value"] + "\n"

    return s


if __name__ == "__main__":
    main()
