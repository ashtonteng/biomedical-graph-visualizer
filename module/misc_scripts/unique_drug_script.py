def get_unique_drugs():

    print("Generating unique drugs from list")

    drug_dict = {}

    with open("drugs.txt", "r") as file:
        for line in file.readlines():
            drug = line.split(" ")[0].strip()

            if drug != "" and drug not in drug_dict.keys():
                drug_dict[drug] = 1

    with open("drugs_unique.txt", "w") as file:
        for key, value in drug_dict.items():
            file.write(key)
            file.write("\n")


if __name__ == '__main__':
    get_unique_drugs()