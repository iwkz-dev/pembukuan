iban_prs = "DE22100100100016647102"
year_str = ["Jan", "Feb", "März", "Apr", "May", "Juni", "Juli", "Aug", "Sep", "Okt", "Nov", "Dez"]
skr_dic = {
    #possible for multiple description, keys should empty, it will takes from each description
    2250: {
        "category": "Dauerauftrag Spenden",
        "keys": [],
        "description": {
            "Operasional Masjid": ["operasional", "000000009802"],
            "Infaq": ["infaq", "infak"]
        }
    },
    2251: {
        "category": "Spenden",
        "keys": [],
        "description": {
            "Operasional Masjid": ["ope- rasional", "opera- sional",],
            "Infaq": ["sedekah", "se- dekah"]
        }
    },
    2253: {
        "category": "Spendeaktionen Religiöse",
        "keys": [],
        "description": {
            "Zakat Fitrah": ["fitrah"],
            "Zakat Maal": ["zakat", "penghasilan"],
            "PRS": ["prs", "proyekrumahsurga@iwkz.de"],
            "Qurban": ["qurban"]
        }
    },
    2254: {
        "category": "Spendeaktionen Humanitäre",
        "keys": [],
        "description": {
            "ACT": ["act"],
            "HI": ["fight corona", "corona", "gerakan", "gera- kan"]
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
    6420: {
        "category": "Rundfunk ARD,ZDF,Dradio",
        "keys": ["rundfunk ard"],
        "description": "Rundfunk "
    },
    10000: {
        "category": "Kantin Jumat",
        "keys": ["kantin", "kan- tin"],
        "description": ""
    },
    10001: {
        "category": "Saso",
        "keys": ["saso", "sa- so", "sate somay"],
        "description": ""
    }
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