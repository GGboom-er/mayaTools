import maya.cmds as mc
import os
import json
class Data():
    def __init__(self,userInputs):
        self.userInputs = userInputs
        self.jsonFileName_fullPathDict = {}
        self.jsonFileName_dataDict = {}
        
        scriptPath = mc.internalVar(usd = 1)
        self.dataPath = scriptPath + r'DW_MaterialManager' + r'/' + 'data' 
        
    def __readJsonFile(self,jsonFile):
        with open(jsonFile) as jsFile:
            jsonData = json.load(jsFile)
        return jsonData
    def __getJsonFileNameAndPathDict(self):
        userInputs = self.userInputs
        
        dataDict = {}
        
        jsonDataFileFullPaths = []
        inputDictFileFullPaths = []
    
        jsonFileDict = {}
        userInputDirs = []
        for root,dirs,files in  os.walk(self.dataPath):
            for userInput in userInputs:
                for dir in dirs:
                    if userInput == dir:
                        userInputDirs.append(os.path.join(root,dir))
                for file in files:
                    if userInput == file.partition('.')[0]:
                        jsonFileDict[userInput] = os.path.join(root,file)

    
        for userInputDir in userInputDirs:
            for root,dirs,files in os.walk(userInputDir):
                for file in files:
                    jsonFileDict[file.partition('.')[0]] = os.path.join(root,file)
    
        self.jsonFileName_fullPathDict = jsonFileDict

        
    def __getJsonDataAndFileNameDict(self):
        for jsonFileName in self.jsonFileName_fullPathDict:
            data = self.__readJsonFile(self.jsonFileName_fullPathDict[jsonFileName])
            self.jsonFileName_dataDict[jsonFileName] = data
    def prepareData(self):
        self.__getJsonFileNameAndPathDict()
        self.__getJsonDataAndFileNameDict()
        return self.jsonFileName_dataDict