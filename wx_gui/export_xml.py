import xmltodict

def create_xml_data(Tool):
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
                    '@name': Tool.GroupeMat,
                    'params': None
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
                    '@type': Tool.Type,
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
                            '@value': Tool.CuttingMaterial
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
                            '@value': '19'
                        },
                        {
                            '@name': 'toolShaftType',
                            '@value': 'parametric'
                        },
                        {
                            '@name': 'toolShaftDiameter',
                            '@value': '8'
                        },
                        {
                            '@name': 'toolShaftChamferDefMode',
                            '@value': 'abs'
                        },
                        {
                            '@name': 'toolShaftChamferAbsPos',
                            '@value': '26'
                        },
                        {
                            '@name': 'toolDiameter',
                            '@value': '8'
                        },
                        {
                            '@name': 'taperHeight',
                            '@value': '23.63'
                        },
                        {
                            '@name': 'collar',
                            '@value': '1'
                        },
                        {
                            '@name': 'tipDiameter',
                            '@value': '7.4'
                        },
                        {
                            '@name': 'cornerRadius',
                            '@value': '0.15'
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
                                    '@value': '197'
                                },
                                {
                                    '@name': 'coolants',
                                    '@value': '1'
                                },
                                {
                                    '@name': 'cuttingDirection',
                                    '@value': 'upAndDown'
                                },
                                {
                                    '@name': 'feedratePerEdge',
                                    '@value': '0.082'
                                },
                                {
                                    '@name': 'cuttingWidth',
                                    '@value': '1.6'
                                },
                                {
                                    '@name': 'cuttingLength',
                                    '@value': '19'
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

    
    create_xml_file(xml_data, 'output.xml')

    return xml_data

def create_xml_file(xml_data, filename):
    xml = xmltodict.unparse(xml_data, pretty=True,short_empty_elements=True)
    print(xml)
    

    with open(filename, 'w',  encoding='UTF-8') as file:
        file.write(xml)



