
year_str = ["Jan", "Feb", "März", "Apr", "May", "Juni", "Juli", "Aug", "Sep", "Okt", "Nov", "Dez"]
skr_dic = {
    #possible for multiple description, keys should empty, it will takes from each description
    2250: {
        "category": "Dauerauftrag Spenden",
        "keys": [],
        "description": {
            "Infaq": ["infaq", "sedekah", "infak"],
            "Operasional Masjid": ["operasional", "000000009802"]
        }
    },
    2253: {
        "category": "Spendeaktionen Religiöse",
        "keys": [],
        "description": {
            "Zakat Fitrah": ["fitrah"],
            "Zakat Maal": ["zakat"],
            "PRS": ["prs", "proyekrumahsurga@iwkz.de"],
            "Qurban": ["qurban"]
        }
    },
    2254: {
        "category": "Spendeaktionen Humanitäre",
        "keys": [],
        "description": {
            "ACT": ["act"],
        }
    },

    #single description
    6805: {
        "category": "Telefon",
        "keys": ["telefonica"],
        "description": "Telefonica"
    },
    6810: {
        "category": "Internet",
        "keys": ["ionos"],
        "description": "1 und 1"
    },
    6325: {
        "category": "Gas, Strom, Wasser",
        "keys": ["vattenfall"],
        "description": "Vattenfall"
    },
    6310: {
        "category": "Miete",
        "keys": ["schmidt hausverwaltu"],
        "description": ""
    },
    10000: {
        "category": "Kantin Jumat",
        "keys": ["kantin", "kan- tin"],
        "description": ""
    },
}

def get_keys(data):
    keys = data["keys"]
    data_description = data["description"]

    if not keys:
        if isinstance(data["description"], dict):
            for desc, desc_keys in data_description.items():
                keys += desc_keys

    return keys

def get_description(description, data_description):
    tmp_desc = "-"

    if isinstance(data_description, dict):
        for desc, desc_keys in data_description.items():
            for keyword in desc_keys:
                if keyword in description:
                    tmp_desc = desc
                    break
            else:
                continue
            break
    else:
        tmp_desc = data_description
    
    return tmp_desc