#hardcoded values for tool types
class ToolsDefaultsData:
    toolTypes = ["endMill", "radiusMill", "ballMill", "drill", "tap", "t-slot", "threadMill"]
    tsModels = ["Side Mill D20 L35 SD20", "Radiused Mill D16 L40 r3 SD16", "Ball Nose Mill D8 L30 SD8", "Twisted Drill D10 L35 SD10", "Tap M10*1,5 L35 SD10", "T Slot Mill D20 L5 SD10", "Internal Thread Mill ISO P1,5 L30 SD10"]

class ToolsCustomData:
    tsModels = []
    toolTypes = []
    toolTypesNumbers = []

class Tool:
    """
    This class represents a tool with all its attributes.
    """

    #make comments so i have more info about tool class


    def __init__(self,id=0, Name="", toolType=0, GroupeMat="", D1=0.0, D2=0.0, D3=0.0, L1=0.0, L2=0.0, L3=0.0, NoTT=0, RayonBout=0.0, Chanfrein=0.0, AngleDeg=0, CoupeCentre=0.0,
                  ArrCentre=0, threadTolerance=0, threadPitch=0.0, Manuf="", ManufRef="", ManufRefSec="", Code="", CodeBar="", Comment="", CuttingMaterial="", TSid=""):
   
        self.id = id
        self.Name = Name
        self.toolType = toolType 
        """
            1-endMill
            2-radiusMill
            3-ballMill
            4-drill
            5-tap
            6-t-slot
            7-threadMill
        """
        self.GroupeMat = GroupeMat
        self.D1 = D1
        self.D2 = D2
        self.D3 = D3
        self.L1 = L1
        self.L2 = L2
        self.L3 = L3
        self.NoTT = NoTT
        self.RayonBout = RayonBout
        self.Chanfrein = Chanfrein
        self.AngleDeg = AngleDeg
        self.CoupeCentre = CoupeCentre
        self.ArrCentre = ArrCentre
        self.threadTolerance = threadTolerance
        self.threadPitch = threadPitch
        self.Manuf = Manuf
        self.ManufRef = ManufRef
        self.ManufRefSec = ManufRefSec
        self.Code = Code
        self.CodeBar = CodeBar
        self.Comment = Comment
        self.CuttingMaterial = CuttingMaterial
        self.TSid = TSid

    def getAttributes(self):
        return {
            'id': self.id,
            'Name': self.Name,
            'toolType': self.toolType,
            'GroupeMat': self.GroupeMat,
            'D1': self.D1,
            'D2': self.D2,
            'D3': self.D3,
            'L1': self.L1,
            'L2': self.L2,
            'L3': self.L3,
            'NoTT': self.NoTT,
            'RayonBout': self.RayonBout,
            'Chanfrein': self.Chanfrein,
            'AngleDeg': self.AngleDeg,
            'CoupeCentre': self.CoupeCentre,
            'ArrCentre': self.ArrCentre,
            'threadTolerance': self.threadTolerance,
            'threadPitch': self.threadPitch,
            'Manuf': self.Manuf,
            'ManufRef': self.ManufRef,
            'ManufRefSec': self.ManufRefSec,
            'Code': self.Code,
            'CodeBar': self.CodeBar,
            'Comment': self.Comment,
            'CuttingMaterial': self.CuttingMaterial,
            'TSid' : self.TSid,
        }
        