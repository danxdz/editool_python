class Tool:
 
    def __init__(self, Name="", toolType="", GroupeMat="", D1=0.0, D2=0.0, D3=0.0, L1=0.0, L2=0.0, L3=0.0, NoTT=0, RayonBout=0.0, Chanfrein=0.0, CoupeCentre=0.0,
                  ArrCentre="", TypeTar=0, PasTar=0.0, Manuf="", ManufRef="", ManufRefSec="", Code="", CodeBar="", Comment="", CuttingMaterial=""):
   
        self.Name = Name
        self.toolType = toolType
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
        self.CoupeCentre = CoupeCentre
        self.ArrCentre = ArrCentre
        self.TypeTar = TypeTar
        self.PasTar = PasTar
        self.Manuf = Manuf
        self.ManufRef = ManufRef
        self.ManufRefSec = ManufRefSec
        self.Code = Code
        self.CodeBar = CodeBar
        self.Comment = Comment
        self.CuttingMaterial = CuttingMaterial

    def to_dict(self):
        return {
            'Name': self.Name,
            'Type': self.toolType,
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
            'CoupeCentre': self.CoupeCentre,
            'ArrCentre': self.ArrCentre,
            'TypeTar': self.TypeTar,
            'PasTar': self.PasTar,
            'Manuf': self.Manuf,
            'ManufRef': self.ManufRef,
            'ManufRefSec': self.ManufRefSec,
            'Code': self.Code,
            'CodeBar': self.CodeBar,
            'Comment': self.Comment,
        }
