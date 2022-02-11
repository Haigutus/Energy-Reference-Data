import xmltodict

reading_type = {
    2: {"name": "aggregate",
        "values": {
            0: "none",
            26: "sum"
        }
        },
    3: {"name": "measuringPeriod",
        "values": {
            2: "PT15M",
            3: "PT1M",
            7: "PT1H",
        },
        },
    4: {"name": "accumulation",
        "values": {
            6: "indicating",
        },
        },
    5: {"name": "flowDirrection",
        "values": {
            1: "A02",
            19: "A01",
        },
        },
    6: {"name": "commodity",
        "values": {
            1: "electricity",
            7: "natural gas",
        },
        },
    7: {"name": "measurementKind",
        "values": {
            12: "energy",
        },
        },
    16: {"name": "multiplier",
         "values": {
             3: "K"
         }
         },
    17: {"name": "unit",
         "values": {
             72: {"measurementUnit": "KWH",
                  "energyProduct": "8716867000030"},
             73: {"measurementUnit": "KAH",
                  "energyProduct": "8716867000047"}
         }
         }
}


def parse_reading_type(type_string="0.0.7.6.1.1.12.0.0.0.0.0.0.0.0.3.72.0"):
    coded_values = type_string.split(".")
    parsed = {"@mRID": type_string}
    for position in reading_type.keys():
        parsed[reading_type[position]["name"]] = reading_type[position]["values"].get(int(coded_values[position - 1]))

    print(xmltodict.unparse({"readingType": parsed}, pretty=True))
    return parsed


reading_types_list = [
    "0.0.7.6.1.1.12.0.0.0.0.0.0.0.0.3.72.0",
    "0.0.7.6.19.1.12.0.0.0.0.0.0.0.0.3.72.0",
    "0.0.7.6.1.1.12.0.0.0.0.0.0.0.0.3.73.0",
    "0.0.7.6.19.1.12.0.0.0.0.0.0.0.0.3.73.0"
]

xml = xmltodict.unparse({"ReadingTypes": {"@xmlns": "http://iec.ch/TC57/2011/MeterReadings#",
                                         "readingType":[parse_reading_type(reading) for reading in reading_types_list]}}, pretty=True)
print(xml)

with open("cim_MeterReadings_ReadingTypes.xml", "w") as file_object:
    file_object.write(xml)