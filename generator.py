import requests
import os
import json

# BarcodeInfo: Map Author, Map Name

def get_barcode_info(barcode: str):
    barcodeList = barcode
    
    if type(barcode) == str:
        barcodeList = barcode.split(", ")

    if len(barcodeList) == 1:
        barcodeList = ["", barcodeList[0]]

    return barcodeList

# TODO: implement this because people keep making bootleg 7-11s and it's annoying
def compare_barcode(barcode, compareTo):
    barcode1 = get_barcode_info(barcode)
    barcode2 = get_barcode_info(compareTo)
    isStringsComparable = lambda x, y: x != "" and y != ""

    for index, x in enumerate(barcode1):
        y = barcode2[index]

        if not isStringsComparable(x, y):
            continue

        if x.lower() != y.lower():
            return False

    return True

def barcode_tests():
    tests = [
        "BabaCorp, AlexTheBaba.711",
        "AlexTheBaba.711",
        ["BabaCorp", "AlexTheBaba.711"],
        ["AlexTheBaba.711"]
    ]

    for x in tests:
        print(get_barcode_info(x))
        print(compare_barcode(x, tests[0]))

class ModRepoFilterer():
    def __init__(self, *, title, description, json):
        self.json = json
        self.json["objects"]["o:1"]["title"] = title
        self.json["objects"]["o:1"]["description"] = description
    
    def filter_for_mods(self, barcodes: list):
        # oIds = [f"o:{x}" for x in ids]
        barcodeMatcher = lambda x, y: compare_barcode(x, y) 
        allowedRefs = ["o:1", "o:2", "o:3", "o:4", "o:5", "o:6", "o:7", "o:8", "o:9"]
        found = []

        for key, object in self.json["objects"].items():
            if not "barcode" in object:
                continue

            barcodeMatch = False

            for compare in barcodes:
                if barcodeMatcher(object["barcode"], compare):
                    barcodeMatch = True
                    found.append(compare)
                    break
            
            if not barcodeMatch:
                continue

            if not "targets" in object:
                continue

            if type(object["targets"]) != dict:
                continue

            allowedRefs.append(key)

            print("Adding", object["barcode"], "by", object.get("author", "???"), "to the list")
            
            for target in object["targets"].values():
                allowedRefs.append(target["ref"])

        newObjects = self.json["objects"].copy()
        missing = [x for x in barcodes if not x in found]

        if len(missing) > 0:
            print(
                f"The following mods could not be found ({len(missing)}):",
                ", ".join([get_barcode_info(x)[1] for x in missing])
            )

        for key in self.json["objects"].keys():
            if not key in allowedRefs:
                del newObjects[key]

        self.json["objects"] = newObjects

        return self.json
    
    def get_list(self):
        return self.json

def ParseBarcodeData(data):
    return [x for x in data.split("\n") if len(x) > 0 and not x.startswith("#")]

class CustomRepository():
    def __init__(self, *, title, description, latestRepo, barcodesFp):
        with open(barcodesFp, "r") as file:
            self.barcodes = ParseBarcodeData(file.read())
            print("Barcodes:", self.barcodes)

        self.title = title
        self.description = description
        self.latestRepo = latestRepo

    def output_to_file(self, fp):
        with open(fp, "w") as outputFile:
            filter = ModRepoFilterer(
                title = self.title,
                description = self.description,
                json = self.latestRepo
            )

            filter.filter_for_mods(self.barcodes)
            json.dump(filter.get_list(), outputFile)

if __name__ == "__main__":
    barcode_tests()

print("Making a request to the mod.io repository...")
response = requests.get("https://blrepo.laund.moe/repository.json")
latestRepo = response.json()

CustomRepository(
    title = "Fizzyhex: Fizzy's Mod Folder",
    description = "Personal mod repo for mods I have installed :>",
    latestRepo = latestRepo,
    barcodesFp = "mod_lists/fizzyhex.txt"
).output_to_file("outputs/fizzyhex_personal_repo.json")

print("Updated files!")