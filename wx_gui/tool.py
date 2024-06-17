#hardcoded values for tool types
class ToolsDefaultsData:
    '''
    
        tool_names_mask

        tool_types

        ts_models

        coolants_types    

    '''

    tool_names_mask = [
        "FR2T Ø[D] [NoTT]z Lc[L] Lu[CTS_AL]",
        "FRTO Ø[D] r[r] [NoTT]z Lc[L] Lu[CTS_AL]",
        "FRHE Ø[D] [NoTT]z Lc[L] Lu[CTS_AL]",
        "FRCH Ø[D] A[A] [NoTT]z Lc[L] Lu[CTS_AL]",
        "FR3T Ø[D] L[L] [NoTT]z Lc[L] Lu[CTS_AL]",
        "FOAP Ø[D] [NoTT]z Lc[L]",
        "FOAC Ø[D2] SD[D1] [NoTT]z Lc[L]",
        "FO Ø[D] L[L] [NoTT]z Lc[L]",
        "TAR M[M]xP[P] L[L] [NoTT]z Lc[L] Lu[CTS_AL]",
        "FRFI [Norm]x[Pitch] Ø[D] L[L] [NoTT]z  Lu[LH]",
        "AL Ø[D] L[L] [NoTT]z Lc[L] Lu[CTS_AL]"
    ]
    
    coolants_types = ["0: 'Unkown'","1: 'external'", "2: 'internal'", "3: 'externalAir'", "4: 'externalAir'", "5: 'mql'"]
    '''
    Coolant types:
      - 0: Unkown
      - 1: external
      - 2: internal
      - 3: externalAir
      - 4: externalAir
      - 5: mql
    '''
    
    tool_types = ["endMill", "radiusMill", "ballMill", "chamferMill", "tslotMill", "spotDrill", "centerDrill", "drill", "tap", "threadMill", "reamer"]
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
    
    ts_models = ["Side Mill D20 L35 SD20", 
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
    """
    - full_tools_list is a list of all (filtered) tools
    - selected_tool is the tool selected in the tool list
    - tool_types_list is a list of all tool types
    - existent_tooltypes is a list of all existent tool types in the database
    - tool_names_mask is a list of all tool names masks
    """
    def __init__(self):
        self.ts_models = []
        """ list of custom TS models """
        self.tool_type_numbers = []
        """ list of all tools types numbers """
        self.tool_types_list = []
        """ list of all tools types names """
        self.full_tools_list = []
        """ list of filtered tools """
        self.tool_names_mask = []
        """ list of all tool names masks """
        self.existent_tooltypes = []
        """ list of all existent tool types in the database """
        self.selected_tool = 0 
        """ selected tool on list ctrl """
        self.selected_toolType = -1
        """ selected tool type on list ctrl """

    def get_custom_ts_models(self):
        """
        This method reads the file tooltypes.txt where we define the custom TS models
            
            ex:
            - 8;tap;  <-- "no custom TS model"
            - 9;threadMill;threadMill_editool  <-- "custom TS model"

            and sets the following attributes:
            - tool_types_list
            - ts_models
            - tool_type_numbers

        """
        with open("./tooltypes.txt", "r",  encoding='UTF-8') as f:
            for line in f:
                parts = line.split(";")
                if len(parts) < 3:
                    print(f"Skipping line {line.strip()} because it does not have enough parts, check tooltypes.txt file")
                    continue
                self.tool_types_list.append(parts[1])
                self.ts_models.append(parts[2].strip())
                self.tool_type_numbers.append(parts[0])
        return self



class Tool:
    """
    This class represents a tool with all its attributes.
    - id is the id of the tool in the database
    - name is the name of the tool
    - toolType is the type of the tool
    - cuttingMaterial is the material to cut
    - toolMaterial is the material of the tool
    - D1 is the cutting diameter
    - D2 is the neck diameter
    - D3 is the shank diameter
    - L1 is the cutting length
    - L2 is the neck length
    - L3 is the total length
    - z is the number of teeth
    - cornerRadius is the corner radius
    - chamfer is the chamfer
    - neckAngle is the angle of the neck in degrees
    - centerCut is the center cut
    - coolantType is the coolant type
    - threadTolerance is the thread tolerance
    - threadPitch is the thread pitch
    - mfr is the manufacturer
    - mfrRef is the manufacturer reference
    - mfrSecRef is the manufacturer secondary reference
    - code is the tool ts code
    - codeBar is the tool barcode
    - comment is the tool comment
    - TSid is the ts model id
    - imported is a flag to know if the tool is freshly imported
"""
    def __init__(self,id=0, name="", toolType=0, cuttingMaterial="", toolMaterial="",
                  D1=0.0, D2=0.0, D3=0.0, L1=0.0, L2=0.0, L3=0.0, 
                  z=0, cornerRadius=0.0, chamfer=0.0, 
                  neckAngle=0.0, centerCut=0.0, coolantType=0, 
                  threadTolerance=0, threadPitch=0.0, mfr="", mfrRef="", mfrSecRef="", code="", codeBar="", comment="", TSid="", imported=1):
   
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
        #material to cut
        self.toolMaterial = toolMaterial
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
        self.imported = imported
        #freshly imported tool

    def getAttributes(self):
        return {
            'id': self.id,
            'name': self.name,
            'toolType': self.toolType,
            'cuttingMaterial': self.cuttingMaterial,
            'toolMaterial': self.toolMaterial,
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
            'imported': self.imported
        }
        