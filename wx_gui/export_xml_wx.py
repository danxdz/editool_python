import xmltodict

def create_xml_data(Tool):
    print("Tool.ArrCentre", Tool.ArrCentre)
    if Tool.ArrCentre:
        if Tool.ArrCentre == "No" or Tool.ArrCentre == "0: 'Unkown'":
            Tool.ArrCentre = "0"
        elif Tool.ArrCentre == "Yes":
            Tool.ArrCentre = "1"
    else :
        Tool.ArrCentre = "0"
    xml_data = {
        'omtdx': {
            '@version': '23',
            '@srcType': 'standard',
            '@match-formulas-by-expression': 'true',
            '@match-material-by-provider': 'fraisa',
            '@tecset-values-outdated': 'true',
            'technologyPurposes': {
                'technologyPurpose': {
                    '@name': 'Roughing HDC-P, partial cut'
                }
            },
            'formulas': {
                'formula': [
                    {
                        '@name': 'fZ',
                        '@type': 'feedrate',
                        'param': {
                            '@name': 'formula',
                            '@value': 'fz*z*n'
                        }
                    },
                    {
                        '@name': 'feedrateAxial',
                        '@type': 'feedrate',
                        'param': {
                            '@name': 'formula',
                            '@value': 'fz*z*n/3'
                        }
                    },
                    {
                        '@name': 'feedrateReduced',
                        '@type': 'feedrate',
                        'param': {
                            '@name': 'formula',
                            '@value': 'fz*z*n*0.7'
                        }
                    },
                    {
                        '@name': 'fN',
                        '@type': 'speed',
                        'param': {
                            '@name': 'formula',
                            '@value': '(Vc*1000)/(d*pi)'
                        }
                    }
                ]
            },
            'materials': {
                'material': {
                    '@name': '1.0722 < 500 N/mm²'
                }
            },
            'cuttingMaterials': {
                'cuttingMaterial': {
                    '@name': "Carbure",#Tool.CuttingMaterial,
                    'params': {
                        '@name':"predefinedObjGuid",
                        '@value':"{3755D6C7-90E4-4134-AD07-72FE5EB19F63}",
                    }
                }
            },
            'couplings': None,
            'coolants': {
                'coolant': {
                    '@number': '1',
                    'param': [
                        {
                            '@name': 'comment',
                            '@value': 'External coolant'
                        },
                        {
                            '@name': 'type',
                            '@value': 'external'
                        }
                    ]
                }
            },
            'tools': {
                'tool': {
                    '@type': Tool.toolType,
                    '@name': Tool.Name,
                    'param': [
                        {
                            '@name': 'comment',
                            '@value': Tool.Comment
                        },
                        {
                            '@name': 'orderingCode',
                            '@value': Tool.ManufRef
                        },
                        {
                            '@name': 'manufacturer',
                            '@value': Tool.Manuf
                        },
                        {
                            '@name': 'cuttingMaterial',
                            '@value': 'Carbure',#Tool.CuttingMaterial
                        },
                        {
                            '@name': 'lengthOfUnit',
                            '@value': 'mm'
                        },
                        {
                            '@name': 'toolTotalLength',
                            '@value': Tool.L3
                        },
                        {
                            '@name': 'cuttingEdges',
                            '@value': Tool.NoTT
                        },
                        {
                            '@name': 'cuttingLength',
                            '@value': Tool.L1
                        },
                        {
                            '@name': 'toolShaftType',
                            '@value': 'parametric'
                        },
                        {
                            '@name': 'toolShaftDiameter',
                            '@value': Tool.D3
                        },
                        {
                            '@name': 'toolShaftChamferDefMode',
                            '@value': 'abs'
                        },
                        {
                            '@name': 'toolShaftChamferAbsPos',
                            '@value': '0'
                        },
                        {
                            '@name': 'toolDiameter',
                            '@value': Tool.D1
                        },
                        {
                            '@name': 'taperHeight',
                            '@value': Tool.L1
                        },
                        {
                            '@name': 'collar',
                            '@value': Tool.D2
                        },
                        {
                            '@name': 'tipDiameter',
                            '@value': Tool.D1
                        },
                        {
                            '@name': 'cornerRadius',
                            '@value': Tool.RayonBout
                        },
                        {
                            '@name': 'coreDiameter',
                            '@value': '0'
                        },
                        {
                            '@name': 'coreHeight',
                            '@value': '0'
                        },
                        {
                            '@name': 'discHeight',
                            '@value': '0'
                        }
                    ],
                    'tecsets': {
                        'tecset': {
                            '@type': 'milling',
                            'param': [
                                {
                                    '@name': 'material',
                                    '@value': '1.0722 < 500 N/mm²'
                                },
                                {
                                    '@name': 'purpose',
                                    '@value': 'Roughing HDC-P, partial cut'
                                },
                                {
                                    '@name': 'lengthOfUnit',
                                    '@value': 'mm'
                                },
                                {
                                    '@name': 'spindleSpeedFormula',
                                    '@value': 'fN'
                                },
                                {
                                    '@name': 'cuttingSpeed',
                                    '@value': '0'
                                },
                                {
                                    '@name': 'coolants',
                                    '@value': int(float(Tool.ArrCentre))                                },
                                {
                                    '@name': 'cuttingDirection',
                                    '@value': 'upAndDown'
                                },
                                {
                                    '@name': 'feedratePerEdge',
                                    '@value': '0.0'
                                },
                                {
                                    '@name': 'cuttingWidth',
                                    '@value': '1.6'
                                },
                                {
                                    '@name': 'cuttingLength',
                                    '@value': Tool.L1
                                },
                                {
                                    '@name': 'plungeAngle',
                                    '@value': '0'
                                },
                                {
                                    '@name': 'planeFeedrateFormula',
                                    '@value': 'fZ'
                                },
                                {
                                    '@name': 'zFeedrateFormula',
                                    '@value': 'feedrateAxial'
                                },
                                {
                                    '@name': 'reducedFeedrateFormula',
                                    '@value': 'feedrateReduced'
                                }
                            ]
                        }
                    }
                }
            }
        }
    }

    output = "output_xml/" + Tool.Name + ".xml"
    create_xml_file(xml_data, output)

    return xml_data

def create_xml_file(xml_data, filename):
    xml = xmltodict.unparse(xml_data, pretty=True,short_empty_elements=True)
    print(filename)
    

    with open(filename, 'w',  encoding='UTF-8') as file:
        file.write(xml)
        print("file created")