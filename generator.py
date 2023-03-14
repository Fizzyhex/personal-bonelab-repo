import requests
import os
import json

class ModRepoFilterer():
    def __init__(self, *, title, description, json):
        self.json = json
        self.json["objects"]["o:1"]["title"] = title
        self.json["objects"]["o:1"]["description"] = description
    
    def filter_for_mods(self, barcodes):
        # oIds = [f"o:{x}" for x in ids]
        allowedRefs = []
        
        for key, object in self.json["objects"].items():
            if not "barcode" in object:
                continue

            if object["barcode"] in barcodes:
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

class CustomRepository():
    def __init__(self, *, title, description, latestRepo, barcodesFp):
        with open(barcodesFp, "r") as file:
            self.barcodes = file.read().split("\n")

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

print("Up to date!")