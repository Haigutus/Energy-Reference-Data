import xmltodict

reading_quality_type = {
    1: {"name": "systemIdentifier",
        "values": {
            0: "Not Applicable",
            1: "End Device",
            2: "Metering system (data collection) network",
            3: "Meter Data Management System",
            4: "Other system (not listed)",
            5: "Externally specified (see accompany data)"
        }
        },
    2: {"name": "categorization",
        "values": {
            0: "Valid",
            1: "Diagnostics related",
            2: "Power quality related issues at the data collection point",
            3: "Tamper / Revenue Protection related",
            4: "Data collection related",
            5: "Failed reasonability testing",
            6: "Failed validation testing",
            7: "Edited",
            8: "Estimated",
            10: "Questionable",
            11: "Derived",
            12: "Projected"
        }
        },
    3: {"name": "index",
        "values": {
            0: {
                0: "Data Valid",
                1: "Validated",
                },
            2: {
                32: "PowerFail",
                },
            4: {
                9: "ClockChanged",
                131: "ManualRead",
                },
            5: {
                259: "KnownMissingRead",
            },
            6: {
                0: "Failed validation – Generic",
            },
            7: {
                0: "Manually Edited – Generic",
            },
            8: {
                0: "Estimated – Generic",
            },
            11: {
                0: "Derived - Deterministic",
            }
        }
        },

}

reading_quality = [
 {'mRID': '2.5.259', 'description': 'Not Acquired'},
 {'mRID': '1.4.9', 'description': 'Time Shift'},
 {'mRID': '1.2.32', 'description': 'Power Down'},
 {'mRID': '1.4.131', 'description': 'Value Acquired By HHT'},
 {'mRID': '2.8.0', 'description': 'Estimated Value'},
 {'mRID': '2.7.0', 'description': 'Norm Value Changed By User'},
 {'mRID': '2.6.0', 'description': 'Invalid Value'},
 {'mRID': '2.11.0', 'description': 'Aggregation Incomplete'},
 {'mRID': '1.0.0', 'description': 'Status OK (no status)'}
]


def parse_reading_quality_type(type_string="1.0.0", description=None):
    coded_values = type_string.split(".")
    parsed = {"@mRID": type_string}
    for position in reading_quality_type.keys():

        if position == 3:
            parsed[reading_quality_type[position]["name"]] = reading_quality_type[position]["values"].get(int(coded_values[position - 2])).get(int(coded_values[position - 1]))
        else:
            parsed[reading_quality_type[position]["name"]] = reading_quality_type[position]["values"].get(int(coded_values[position - 1]))

    if description:
        parsed["description"] = description

    #print(xmltodict.unparse({"readingQualityType": parsed}, pretty=True))
    return parsed


xml = xmltodict.unparse({"ReadingQualityTypes": {"@xmlns": "http://iec.ch/TC57/2011/MeterReadings#",
                                                 "readingQualityType":[parse_reading_quality_type(reading["mRID"], reading["description"]) for reading in reading_quality]}}, pretty=True)
print(xml)

with open("cim_MeterReadings_ReadingQualityTypes.xml", "w") as file_object:
    file_object.write(xml)