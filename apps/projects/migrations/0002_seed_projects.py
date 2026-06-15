from django.db import migrations

# Verified projects from the company profile (analysis §5 / §6).
# Disputed or missing contract values are intentionally left blank/hidden:
#   - Magomeni Market & Watumishi Housing: conflicting figures -> blank.
#   - PAPU (Arusha): value not stated in the PDF -> hidden.
PROJECTS = [
    {
        "slug": "papu-arusha-multipurpose-building",
        "title": "Pan African Postal Union (PAPU) — 19-Floor Multi-Purpose Building",
        "status": "completed",
        "client_name": "Pan African Postal Union (PAPU)",
        "location": "Sekei, Arusha",
        "sector": "institutional",
        "year_end": 2023,
        "overview": (
            "Electrical, ICT, air-conditioning and mechanical-ventilation systems for "
            "the 19-floor Pan African Postal Union Multi-Purpose Building in Arusha — "
            "a complete power chain from 33kV switchgear to standby power."
        ),
        "scope_of_work": (
            "33kV switchgear receiving utility power\n"
            "2 x 1250kVA 33/0.4kV transformers\n"
            "3600A, 12-way main 400V distribution panel\n"
            "3 x 160kVA UPS units\n"
            "3 x 800kVA standby generators\n"
            "Air handling units for air conditioning\n"
            "Civil aviation warning lights"
        ),
        "technical_highlights": (
            "33kV switchgear\n"
            "2 x 1250kVA 33/0.4kV transformers\n"
            "3600A 12-way main 400V panel\n"
            "3 x 160kVA UPS\n"
            "3 x 800kVA standby generators"
        ),
        "contract_value": "",
        "contract_value_visible": False,
        "is_featured": True,
        "order": 1,
        "services": [
            "electrical-installations",
            "ict-structured-cabling",
            "hvac-air-conditioning",
            "transformers-generators-ups",
        ],
    },
    {
        "slug": "tabora-airport",
        "title": "Tabora Airport — Electrical, ICT, Fire Alarm & HVAC",
        "status": "completed",
        "client_name": "Beijing Construction Engineering Group",
        "main_contractor": "Beijing Construction Engineering Group",
        "location": "Tabora, Tanzania",
        "sector": "aviation",
        "role": "sub",
        "year_end": 2026,
        "overview": "Electrical and ELV systems for Tabora Airport, as Electrical & ELV sub-contractor.",
        "scope_of_work": (
            "Electrical systems installation\n"
            "ICT infrastructure\n"
            "Fire detection and alarm systems\n"
            "HVAC systems\n"
            "Testing and commissioning"
        ),
        "is_featured": True,
        "order": 2,
        "services": [
            "electrical-installations",
            "ict-structured-cabling",
            "fire-detection-alarm",
            "hvac-air-conditioning",
        ],
    },
    {
        "slug": "tbs-laboratories-ubungo",
        "title": "Tanzania Bureau of Standards (TBS) Laboratories",
        "status": "completed",
        "client_name": "Tanzania Bureau of Standards (TBS)",
        "location": "Plot 260 Block G, Ubungo, Dar es Salaam",
        "sector": "government",
        "role": "jv",
        "year_start": 2018,
        "year_end": 2019,
        "overview": (
            "Electrical and structured-cabling works for the TBS laboratories / test "
            "house, delivered as a joint-venture partner."
        ),
        "scope_of_work": (
            "Electrical works\n"
            "Structured cabling (ICT)\n"
            "Solar street lights\n"
            "Testing and commissioning"
        ),
        "contract_value": "TZS 3,130,231,847.72",
        "is_featured": True,
        "order": 3,
        "services": [
            "electrical-installations",
            "ict-structured-cabling",
            "solar-street-lighting",
        ],
    },
    {
        "slug": "rea-uganda-kakumiro-kamwenge",
        "title": "Rural Electrification — Kakumiro & Kamwenge Districts, Uganda",
        "status": "completed",
        "client_name": "Rural Electrification Agency (REA), Uganda",
        "location": "Western Uganda",
        "country": "Uganda",
        "sector": "infrastructure",
        "role": "prime",
        "year_start": 2018,
        "year_end": 2021,
        "overview": (
            "Prime contractor for rural electrification schemes in the Western Service "
            "Territories of Uganda."
        ),
        "scope_of_work": (
            "242.21 km of 33kV power lines\n"
            "317.7 km of low voltage networks\n"
            "110 units of 33/0.433kV transformers\n"
            "1,460 low voltage service lines and energy meters"
        ),
        "contract_value": "USD 3,685,855.45 + UGX 7,890,500,000 (≈ TZS 13.4 billion)",
        "is_featured": True,
        "order": 4,
        "services": ["rural-electrification", "transformers-generators-ups"],
    },
    {
        "slug": "rea-rungwe-kyela-ileje",
        "title": "Rural Electrification — Rungwe, Kyela & Ileje Districts",
        "status": "completed",
        "client_name": "Rural Energy Agency (REA), Tanzania",
        "location": "Mbeya Region, Tanzania",
        "sector": "infrastructure",
        "role": "jv",
        "year_start": 2014,
        "year_end": 2017,
        "overview": "Joint-venture member supplying and installing rural electrification infrastructure.",
        "scope_of_work": (
            "154.085 km of 33kV power lines\n"
            "95.366 km of low voltage networks\n"
            "31 units of 33/0.4kV transformers\n"
            "2,072 low voltage service lines and energy meters"
        ),
        "contract_value": "USD 8,190,131.23 + TZS 5,677,645,750 (≈ TZS 24.7 billion)",
        "is_featured": True,
        "order": 5,
        "services": ["rural-electrification", "transformers-generators-ups"],
    },
    {
        "slug": "msalato-international-airport",
        "title": "Msalato International Airport — Electrical, ICT, Fire Alarm & HVAC",
        "status": "ongoing",
        "client_name": "Beijing Construction Engineering Group",
        "main_contractor": "Beijing Construction Engineering Group",
        "location": "Dodoma, Tanzania",
        "sector": "aviation",
        "role": "sub",
        "year_start": 2026,
        "overview": "Ongoing electrical and ELV works for Msalato International Airport.",
        "scope_of_work": (
            "Electrical installations\nICT systems\nFire alarm systems\nHVAC systems"
        ),
        "is_featured": True,
        "order": 6,
        "services": [
            "electrical-installations",
            "ict-structured-cabling",
            "fire-detection-alarm",
            "hvac-air-conditioning",
        ],
    },
    {
        "slug": "sumbawanga-airport",
        "title": "Sumbawanga Airport — Electrical, ICT, Fire Alarm & HVAC",
        "status": "ongoing",
        "client_name": "Beijing Construction Engineering Group",
        "main_contractor": "Beijing Construction Engineering Group",
        "location": "Sumbawanga, Tanzania",
        "sector": "aviation",
        "role": "sub",
        "year_start": 2026,
        "overview": "Ongoing electrical and ELV works for Sumbawanga Airport.",
        "scope_of_work": (
            "Electrical systems installation\nICT infrastructure\n"
            "Fire detection and alarm systems\nHVAC systems"
        ),
        "order": 7,
        "services": [
            "electrical-installations",
            "ict-structured-cabling",
            "fire-detection-alarm",
            "hvac-air-conditioning",
        ],
    },
    {
        "slug": "muce-iringa",
        "title": "Mkwawa University College of Education (MUCE)",
        "status": "completed",
        "client_name": "CATIC International Engineering (T) Ltd",
        "main_contractor": "CATIC International Engineering (T) Ltd",
        "location": "Iringa, Tanzania",
        "sector": "education",
        "role": "sub",
        "year_start": 2018,
        "year_end": 2019,
        "overview": (
            "Electrical, ICT, air-conditioning and mechanical-ventilation works for "
            "Mkwawa University College of Education, completed and certified by Atkins."
        ),
        "scope_of_work": (
            "Electrical works\nFire alarm systems\nAir conditioning & mechanical ventilation\n"
            "42 solar street lights\nTesting and commissioning"
        ),
        "contract_value": "TZS 1,739,536,075",
        "order": 10,
        "services": [
            "electrical-installations",
            "ict-structured-cabling",
            "fire-detection-alarm",
            "hvac-air-conditioning",
            "solar-street-lighting",
        ],
    },
    {
        "slug": "zittod-zanzibar",
        "title": "Zanzibar Institute of Tourism Development (ZITTOD)",
        "status": "completed",
        "client_name": "Ministry of Education & Vocational Training, Revolutionary Government of Zanzibar",
        "location": "Maruhubi, Unguja, Zanzibar",
        "sector": "education",
        "role": "sub",
        "year_start": 2017,
        "year_end": 2020,
        "overview": "Electrical, ICT, fire-alarm, air-conditioning and mechanical-ventilation works for ZITTOD.",
        "scope_of_work": (
            "Electrical works\nFire alarm systems\nICT / structured cabling\n"
            "Air conditioning & mechanical ventilation"
        ),
        "contract_value": "TZS 3,177,214,142",
        "order": 11,
        "services": [
            "electrical-installations",
            "ict-structured-cabling",
            "fire-detection-alarm",
            "hvac-air-conditioning",
        ],
    },
    {
        "slug": "magomeni-modern-market",
        "title": "Magomeni Modern Market",
        "status": "completed",
        "client_name": "Kinondoni Municipal Council",
        "main_contractor": "Group Six International",
        "location": "Plot 300 Block D, Dar es Salaam",
        "sector": "government",
        "role": "sub",
        "year_start": 2018,
        "year_end": 2020,
        "overview": (
            "Electrical, fire-detection & alarm and air-conditioning / mechanical-"
            "ventilation works for Magomeni Modern Market. (Contract value pending "
            "confirmation.)"
        ),
        "scope_of_work": (
            "Electrical works\nFire detection & alarm systems\n"
            "Air conditioning & mechanical ventilation"
        ),
        "contract_value": "",
        "order": 12,
        "services": [
            "electrical-installations",
            "fire-detection-alarm",
            "hvac-air-conditioning",
        ],
    },
    {
        "slug": "watumishi-housing-gezaulole",
        "title": "Affordable Houses for Public Servants — Watumishi Housing (Package 4)",
        "status": "completed",
        "client_name": "Watumishi Housing Company",
        "main_contractor": "China Wuyi Co. Ltd",
        "consultant": "Atkins Tanzania Ltd",
        "location": "Gezaulole, Kigamboni, Temeke, Dar es Salaam",
        "sector": "housing",
        "role": "sub",
        "year_start": 2019,
        "year_end": 2019,
        "overview": (
            "Permanent power connection for the Watumishi Housing affordable-houses "
            "development. (Contract value pending confirmation.)"
        ),
        "scope_of_work": (
            "2 km overhead 33kV powerline\n2 x 500kVA and 200kVA 33/0.4kV transformers\n"
            "6.5 km of low voltage lines\nPower to 330 apartments and 62 detached houses\n"
            "60 solar street lights"
        ),
        "contract_value": "",
        "order": 13,
        "services": [
            "electrical-installations",
            "transformers-generators-ups",
            "solar-street-lighting",
        ],
    },
    {
        "slug": "udsm-solar-street-lights",
        "title": "Solar Street Lights — University of Dar es Salaam, Mlimani Campus (Phase II)",
        "status": "completed",
        "client_name": "University of Dar es Salaam",
        "location": "Mlimani Campus, Dar es Salaam",
        "sector": "education",
        "role": "prime",
        "year_end": 2021,
        "overview": "Supply, concrete-base construction and installation of 115 solar street lights, certified by UDSM.",
        "scope_of_work": "Concrete base construction\n115 sets of solar street lights\nInstallation and commissioning",
        "contract_value": "TZS 379,960,000",
        "order": 14,
        "services": ["solar-street-lighting"],
    },
    {
        "slug": "dmdp-solar-305",
        "title": "Solar Street Lights — DMDP (305 sets), Dar es Salaam",
        "status": "completed",
        "client_name": "M/S Bonstar Building Materials (Ilala MC / DMDP)",
        "location": "Ukonga, Mwembe Madafu, Mazizini & Mongo la Ndege, Dar es Salaam",
        "sector": "infrastructure",
        "role": "sub",
        "year_end": 2019,
        "overview": "Supply, concrete-base construction and installation of 305 solar street lights under the DMDP.",
        "scope_of_work": "Concrete base construction\n305 sets of solar street lights\nInstallation and commissioning",
        "contract_value": "TZS 298,900,000",
        "order": 15,
        "services": ["solar-street-lighting"],
    },
    {
        "slug": "dodoma-solar-423",
        "title": "Solar Street Lights — Dodoma (423 sets)",
        "status": "completed",
        "client_name": "M/S Bonway International Co. Ltd (Package 5)",
        "location": "Ndovu, Swala, Zuzu, Boma, Biringi, Farahani Avenue & Ilazo-Ilagala, Dodoma",
        "sector": "infrastructure",
        "role": "sub",
        "year_end": 2019,
        "overview": "Supply, concrete-base construction and installation of 423 solar street lights.",
        "scope_of_work": "Concrete base construction\n423 sets of solar street lights\nInstallation and commissioning",
        "contract_value": "TZS 423,000,000",
        "order": 16,
        "services": ["solar-street-lighting"],
    },
    {
        "slug": "ist-senior-campus",
        "title": "International School of Tanganyika — Senior Campus Power Rehabilitation",
        "status": "completed",
        "client_name": "International School of Tanganyika (IST)",
        "location": "Masaki, Dar es Salaam",
        "sector": "education",
        "role": "sub",
        "year_end": 2018,
        "overview": "Rehabilitation of the power supply at the IST Senior School Campus.",
        "scope_of_work": (
            "1MVA (2 x 500kVA 11/0.4kV transformers)\nMain distribution board 2000A, TPN\n"
            "3 outdoor pillars\n35 solar street lights"
        ),
        "contract_value": "USD 469,282",
        "order": 17,
        "services": [
            "electrical-installations",
            "transformers-generators-ups",
            "solar-street-lighting",
        ],
    },
    {
        "slug": "ist-elementary-school",
        "title": "International School of Tanganyika — Elementary School Power Network Rehabilitation",
        "status": "completed",
        "client_name": "International School of Tanganyika (IST)",
        "location": "Upanga, Dar es Salaam",
        "sector": "education",
        "role": "sub",
        "year_end": 2018,
        "overview": "Rehabilitation of the power-supply network at the IST Elementary School.",
        "scope_of_work": (
            "0.5MVA (1 x 500kVA 11/0.4kV transformer)\nMain distribution board 2000A, TPN\n"
            "5 outdoor pillars\n17 consumer kWh energy meters"
        ),
        "contract_value": "USD 345,260",
        "order": 18,
        "services": ["electrical-installations", "transformers-generators-ups"],
    },
]


def seed(apps, schema_editor):
    Project = apps.get_model("projects", "Project")
    Service = apps.get_model("services", "Service")
    for entry in PROJECTS:
        data = {k: v for k, v in entry.items() if k not in ("slug", "services")}
        project, _ = Project.objects.update_or_create(slug=entry["slug"], defaults=data)
        service_qs = Service.objects.filter(slug__in=entry.get("services", []))
        project.related_services.set(service_qs)


def unseed(apps, schema_editor):
    Project = apps.get_model("projects", "Project")
    Project.objects.filter(slug__in=[e["slug"] for e in PROJECTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0001_initial"),
        ("services", "0002_seed_services"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
