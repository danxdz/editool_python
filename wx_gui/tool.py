#hardcoded values for tool types
class ToolsDefaultsData:
    
    coolantsTypes = ["0: 'Unkown'","1: 'external'", "2: 'internal'", "3: 'externalAir'", "4: 'externalAir'", "5: 'mql'"]
    '''
    Coolant types:
      - 0: Unkown
      - 1: external
      - 2: internal
      - 3: externalAir
      - 4: externalAir
      - 5: mql
    '''
    
    toolTypes = ["endMill", "radiusMill", "ballMill", "chamferMill", "tslotMill", "spotDrill", "centerDrill", "drill", "tap", "threadMill", "reamer"]
    '''
    -   0 - endMill
    -   1 - radiusMill
    -   2 - ballMill
    -   3 - chamferMill
    -   4 - tslotMill
    -   5 - spotDrill
    -   6 - centerDrill
    -   7 - drill
    -   8 - tap
    -   9 - threadMill
    -   10 - reamer
    '''
    
    tsModels = ["Side Mill D20 L35 SD20", 
                "Radiused Mill D16 L40 r3 SD16", 
                "Ball Nose Mill D8 L30 SD8", 
                "Chamfer Mill D0 A30 SD10",
                "T Slot Mill D20 L5 SD10",
                "Spotting Drill D10 SD10",
                "Center Drill d3 D8 L5",
                "Twisted Drill D10 L35 SD10",
                "Tap M10*1,5 L35 SD10",
                "Internal Thread Mill ISO P1,5 L30 SD10",
                "Constant Reamer D10 L20 SD9"
                ]
    '''
    tsModels:
    -   Side Mill D20 L35 SD20
    -   Radiused Mill D16 L40 r3 SD16
    -   Ball Nose Mill D8 L30 SD8
    -   Chamfer Mill D0 A30 SD10
    -   T Slot Mill D20 L5 SD10
    -   Spotting Drill D10 SD10
    -   Center Drill d3 D8 L5
    -   Twisted Drill D10 L35 SD10
    -   Tap M10*1,5 L35 SD10
    -   Internal Thread Mill ISO P1,5 L30 SD10
    -   Constant Reamer D10 L20 SD9


    '''


class ToolsCustomData:
    tsModels = []
    toolTypesNumbers = []
    toolTypesList = []
    fullToolsList = []

    @classmethod
    def getCustomTsModels(toolData):
        #get all tool types and ts models from getToolTypes txt file    
        
        with open("./tooltypes.txt", "r") as f:
            for line in f:
                #print(line, toolData.toolTypes)
                toolData.toolTypesList.append(line.split(";")[1])
                #need to strip /n from end of line
                toolData.tsModels.append(line.split(";")[2].strip())
                toolData.toolTypesNumbers.append(line.split(";")[0])
        #print("toolData :: ", toolData.toolTypes)    
        return toolData
    

class Tool:
    """
    This class represents a tool with all its attributes.
    """

    #make comments so i have more info about tool class


    def __init__(self,id=0, name="", toolType=0, cuttingMaterial="",
                  D1=0.0, D2=0.0, D3=0.0, L1=0.0, L2=0.0, L3=0.0, 
                  z=0, cornerRadius=0.0, chamfer=0.0, 
                  neckAngle=0.0, centerCut=0.0, coolantType=0, 
                  threadTolerance=0, threadPitch=0.0, mfr="", mfrRef="", mfrSecRef="", code="", codeBar="", comment="", TSid=""):
   
        self.id = id
        #id from database
        self.name = name
        #name of tool
        self.toolType = toolType 
        """
        Tool types:
        -   0-endMill
        -   1-radiusMill
        -   2-ballMill
        -   3-chamferMill
        -   4-tslotMill
        -   5-spotDrill
        -   6-centerDrill
        -   7-drill
        -   8-tap
        -   9-threadMill
        -   10-reamer
        """
        self.cuttingMaterial = cuttingMaterial
        #tool material
        self.D1 = D1
        #cutting diameter
        self.D2 = D2
        #neck diameter
        self.D3 = D3
        #shank diameter
        self.L1 = L1
        #cutting length
        self.L2 = L2
        #neck length
        self.L3 = L3
        #total length
        self.z = z
        #number of teeth
        self.cornerRadius = cornerRadius
        self.chamfer = chamfer
        self.neckAngle = neckAngle
        #angle of neck in degrees - for FRAISA tools
        self.centerCut = centerCut
        self.coolantType = coolantType
        self.threadTolerance = threadTolerance
        self.threadPitch = threadPitch
        self.code = code
        #tool ts code
        self.mfr = mfr
        #manufacturer
        self.mfrRef = mfrRef
        #manufacturer reference
        self.mfrSecRef = mfrSecRef
        #manufacturer secondary reference
        self.codeBar = codeBar
        #tool barcode
        self.comment = comment
        self.TSid = TSid
        #ts model id - after creating tool in ts

    def getAttributes(self):
        return {
            'id': self.id,
            'name': self.name,
            'toolType': self.toolType,
            'cuttingMaterial': self.cuttingMaterial,
            'D1': self.D1,
            'D2': self.D2,
            'D3': self.D3,
            'L1': self.L1,
            'L2': self.L2,
            'L3': self.L3,
            'z': self.z,
            'cornerRadius': self.cornerRadius,
            'chamfer': self.chamfer,
            'neckAngle': self.neckAngle,
            'centerCut': self.centerCut,
            'coolantType': self.coolantType,
            'threadTolerance': self.threadTolerance,
            'threadPitch': self.threadPitch,
            'mfr': self.mfr,
            'mfrRef': self.mfrRef,
            'mfrSecRef': self.mfrSecRef,
            'code': self.code,
            'codeBar': self.codeBar,
            'comment': self.comment,
            'TSid' : self.TSid,
        }
        