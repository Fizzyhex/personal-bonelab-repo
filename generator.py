import requests
import os
import json

def get_barcode_info(barcode):
    barcodeList = barcode
    
    if type(barcode) == str:
        barcodeList = barcode.split(" ")

    return barcodeList

# TODO: implement this because people keep making bootleg 7-11s and it's annoying
def compare_barcode(barcode, compareTo):
    barcode1 = get_barcode_info(barcode)
    barcode2 = get_barcode_info(compareTo)

    if barcode1[0].lower() != barcode2[0].lower():
        return False
    
    if len(barcode1) > 1 and len(barcode2) > 1:
        if barcode1[1].lower() != barcode[2].lower():
            return False

    return True

class ModRepoFilterer():
    def __init__(self, *, title, description, json):
        self.json = json
        self.json["objects"]["o:1"]["title"] = title
        self.json["objects"]["o:1"]["description"] = description
    
    def filter_for_mods(self, barcodes):
        # oIds = [f"o:{x}" for x in ids]
        lowercaseBarcodes = [barcode.lower() for barcode in barcodes]
        allowedRefs = ["o:1", "o:2", "o:3", "o:4", "o:5", "o:6", "o:7", "o:8", "o:9"]
        
        for key, object in self.json["objects"].items():
            if not "barcode" in object:
                continue

            if object["barcode"].lower() in lowercaseBarcodes:
                if not "targets" in object:
                    continue

                if type(object["targets"]) != dict:
                    continue

                allowedRefs.append(key)
                
                for target in object["targets"].values():
                    allowedRefs.append(target["ref"])

        newObjects = self.json["objects"].copy()

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
            print(self.barcodes)

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

response = requests.get("https://blrepo.laund.moe/repository.json")
latestRepo = response.json()

CustomRepository(
    title = "Fizzyhex's Installed Mod Repo",
    description = "Personal mod repo for mods installed by Fizzy",
    latestRepo = latestRepo,
    barcodesFp = "mod_lists/fizzyhex.txt"
).output_to_file("outputs/fizzyhex_personal_repo.json")

print("Updated!")