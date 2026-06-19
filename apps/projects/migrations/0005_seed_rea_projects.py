from datetime import date

from django.db import migrations

# DIEYNEM REA / rural-electrification project list (June 2026), confirmed by
# DIEYNEM. The source sheet states no contract values, so values are left
# blank/hidden (content-integrity rule). Figures are "as at 30 April 2026".
REA_SERVICES = ["rural-electrification", "transformers-generators-ups"]
AS_AT = date(2026, 4, 30)

# Genuinely new projects (removed again on reverse).
NEW_PROJECTS = [
    {
        "slug": "rea-tz-lot5-northern-zone",
        "title": "Rural Electrification — Lot 5, Arusha, Kilimanjaro, Manyara & Tanga",
        "status": "completed",
        "client_name": "Rural Energy Agency (REA), Tanzania",
        "location": "Arusha, Kilimanjaro, Manyara & Tanga Regions",
        "sector": "infrastructure",
        "role": "prime",
        "year_end": 2024,
        "completion_date": date(2024, 12, 2),
        "overview": (
            "Prime contractor to the Rural Energy Agency (REA) for the construction "
            "of medium- and low-voltage lines, distribution transformers and customer "
            "connections in small-scale mining, industrial and agricultural areas of "
            "northern Tanzania (Contract No. AE/008/2021-22/HQ/W/34, Lot 5)."
        ),
        "scope_of_work": (
            "360.93 km of medium-voltage (MV) lines\n"
            "489.93 km of ABC low-voltage lines\n"
            "227 distribution transformers"
        ),
        "is_featured": True,
        "order": 20,
        "services": REA_SERVICES,
    },
    {
        "slug": "rea-tz-lot6-southern-zone",
        "title": "Rural Electrification — Lot 6, Ruvuma, Lindi, Pwani & Mtwara",
        "status": "completed",
        "client_name": "Rural Energy Agency (REA), Tanzania",
        "location": "Ruvuma, Lindi, Pwani & Mtwara Regions",
        "sector": "infrastructure",
        "role": "prime",
        "year_end": 2024,
        "completion_date": date(2024, 12, 2),
        "overview": (
            "Prime contractor to the Rural Energy Agency (REA) for medium- and "
            "low-voltage lines, distribution transformers and customer connections in "
            "small-scale mining, industrial and agricultural areas of southern "
            "Tanzania (Contract No. AE/008/2021-22/HQ/W/34, Lot 6)."
        ),
        "scope_of_work": (
            "276.31 km of medium-voltage (MV) lines\n"
            "43.89 km of ABC low-voltage lines\n"
            "70 distribution transformers"
        ),
        "order": 21,
        "services": REA_SERVICES,
    },
    {
        # Same contract no. as the 2023 Lot 2 entry below — both confirmed correct
        # by DIEYNEM (different scope packages / completion dates).
        "slug": "rea-tz-lot2-kagera-peri-urban-2024",
        "title": "Rural Electrification — Lot 2 Peri-Urban Areas, Kagera Region (2024)",
        "status": "completed",
        "client_name": "Rural Energy Agency (REA), Tanzania",
        "location": "Kagera Region",
        "sector": "infrastructure",
        "role": "prime",
        "year_end": 2024,
        "completion_date": date(2024, 5, 31),
        "overview": (
            "Construction of medium- and low-voltage lines, installation of "
            "distribution transformers and connection of customers in peri-urban "
            "areas of Kagera Region (Contract No. AE/008/2021-2022/HQ/W/32, Lot 2)."
        ),
        "scope_of_work": (
            "59.112 km of medium-voltage (MV) lines\n"
            "117.802 km of ABC low-voltage lines\n"
            "59 distribution transformers\n"
            "2,438 customer connections"
        ),
        "order": 22,
        "services": REA_SERVICES,
    },
    {
        "slug": "rea-tz-lot2-kagera-peri-urban-2023",
        "title": "Rural Electrification — Lot 2 Peri-Urban Areas, Kagera Region (2023)",
        "status": "completed",
        "client_name": "Rural Energy Agency (REA), Tanzania",
        "location": "Kagera Region",
        "sector": "infrastructure",
        "role": "prime",
        "year_end": 2023,
        "completion_date": date(2023, 11, 16),
        "overview": (
            "Construction of medium- and low-voltage lines, installation of "
            "distribution transformers and connection of customers in peri-urban "
            "areas of Kagera Region (Contract No. AE/008/2021-2022/HQ/W/32, Lot 2)."
        ),
        "scope_of_work": (
            "72.22 km of medium-voltage (MV) lines\n"
            "5.55 km of ABC low-voltage lines\n"
            "97 distribution transformers"
        ),
        "order": 23,
        "services": REA_SERVICES,
    },
    {
        "slug": "rea-tz-lot4-health-water-facilities",
        "title": "Rural Electrification — Lot 4 Health & Water Facilities, Lake Zone",
        "status": "completed",
        "client_name": "Rural Energy Agency (REA), Tanzania",
        "location": "Geita, Kagera, Mara, Mwanza & Simiyu Regions",
        "sector": "infrastructure",
        "role": "prime",
        "year_end": 2023,
        "completion_date": date(2023, 11, 16),
        "overview": (
            "Electrification of rural health and water facilities to help prevent the "
            "spread of infectious diseases, including COVID-19, across the Lake Zone "
            "(Contract No. AE/008/2021-2022/HQ/W/33, Lot 4)."
        ),
        "scope_of_work": (
            "77.72 km of medium-voltage (MV) lines\n"
            "4.525 km of ABC low-voltage lines\n"
            "80 distribution transformers"
        ),
        "order": 24,
        "services": REA_SERVICES,
    },
    {
        "slug": "rea-tz-hep-lot6-katavi",
        "title": "Hamlets Electrification — Lot 6, Katavi Region",
        "status": "completed",
        "client_name": "Rural Energy Agency (REA), Tanzania",
        "location": "Katavi Region",
        "sector": "infrastructure",
        "role": "prime",
        "year_end": 2026,
        "completion_date": date(2026, 4, 30),
        "overview": (
            "Hamlets Electrification Project (HEP) Lot 6 in Katavi Region — low-voltage "
            "networks, distribution transformers and customer connections "
            "(Contract No. TR 198/2023/2024/W/05, Lot 6)."
        ),
        "scope_of_work": (
            "150 km of ABC low-voltage lines\n"
            "75 distribution transformers\n"
            "2,475 customer connections"
        ),
        "order": 25,
        "services": REA_SERVICES,
    },
    {
        "slug": "rea-tz-hep-lot11-mara",
        "title": "Hamlets Electrification — Lot 11, Mara Region",
        "status": "ongoing",
        "client_name": "Rural Energy Agency (REA), Tanzania",
        "location": "Mara Region",
        "sector": "infrastructure",
        "role": "prime",
        "progress_percent": 93,
        "last_updated_label": AS_AT,
        "overview": (
            "Ongoing Hamlets Electrification Project (HEP) Lot 11 in Mara Region "
            "(Contract No. TR 198/2023/2024/W/05, Lot 11). 93% complete as at "
            "30 April 2026."
        ),
        "scope_of_work": (
            "296 km of ABC low-voltage lines\n"
            "148 distribution transformers\n"
            "4,884 customer connections"
        ),
        "is_featured": True,
        "order": 26,
        "services": REA_SERVICES,
    },
    {
        "slug": "rea-tz-hep2b-lot5-rukwa",
        "title": "Hamlets Electrification (HEP-IIB) — Lot 5, Rukwa Region",
        "status": "ongoing",
        "client_name": "Rural Energy Agency (REA), Tanzania",
        "location": "Rukwa Region",
        "sector": "infrastructure",
        "role": "prime",
        "progress_percent": 35,
        "last_updated_label": AS_AT,
        "overview": (
            "Ongoing Hamlets Electrification Project Phase IIB (HEP-IIB) Lot 5 in "
            "Rukwa Region (Contract No. TR198/2024/2025/W/04/5, Lot 5). Planned for "
            "completion in February 2029; 35% complete as at 30 April 2026."
        ),
        "scope_of_work": (
            "174 km of medium-voltage (MV) lines\n"
            "274 km of ABC low-voltage lines\n"
            "156 distribution transformers\n"
            "4,000 customer connections"
        ),
        "order": 27,
        "services": REA_SERVICES,
    },
    {
        "slug": "rea-tz-hep2b-lot9-mtwara",
        "title": "Hamlets Electrification (HEP-IIB) — Lot 9, Mtwara Region",
        "status": "ongoing",
        "client_name": "Rural Energy Agency (REA), Tanzania",
        "location": "Mtwara Region",
        "sector": "infrastructure",
        "role": "prime",
        "progress_percent": 35,
        "last_updated_label": AS_AT,
        "overview": (
            "Ongoing Hamlets Electrification Project Phase IIB (HEP-IIB) Lot 9 in "
            "Mtwara Region (Contract No. TR198/2024/2025/W/04/9, Lot 9). Planned for "
            "completion in February 2029; 35% complete as at 30 April 2026."
        ),
        "scope_of_work": (
            "70 km of medium-voltage (MV) lines\n"
            "296 km of ABC low-voltage lines\n"
            "185 distribution transformers\n"
            "5,000 customer connections"
        ),
        "order": 28,
        "services": REA_SERVICES,
    },
]

# Already on the site — refresh in place (no duplicates), per client instruction.
# Uganda: the source sheet gives the fuller Lot 13 scope (6 districts) and no
# contract value; the previously-shown value was tied to a different scope, so it
# is hidden pending DIEYNEM confirmation.
UPDATES = [
    {
        "slug": "rea-uganda-kakumiro-kamwenge",
        "title": "Rural Electrification — Lot 13 Priority Works, Western & Rwenzori, Uganda",
        "status": "completed",
        "client_name": "Rural Electrification Agency (REA), Uganda",
        "location": "Kabarole, Kakumiro, Kamwenge, Kasese, Mitooma & Rubirizi Districts",
        "country": "Uganda",
        "sector": "infrastructure",
        "role": "prime",
        "year_start": None,
        "year_end": 2024,
        "completion_date": date(2024, 1, 15),
        "overview": (
            "Design, supply and installation of Lot 13 priority rural-electrification "
            "works in the Rwenzori and Western service territories of Uganda "
            "(Contract No. REA-AfDB/WRKS/18-19/00627)."
        ),
        "scope_of_work": (
            "118.96 km of medium-voltage (MV) lines\n"
            "306.06 km of low-voltage (LV) lines\n"
            "103 distribution transformers\n"
            "951 last-mile customer connections"
        ),
        "contract_value": "",
        "contract_value_visible": False,
        "is_featured": True,
        "order": 4,
        "services": REA_SERVICES,
    },
    {
        "slug": "msalato-international-airport",
        "title": "Msalato International Airport — Electrical, ICT, Fire Alarm & HVAC",
        "status": "ongoing",
        "client_name": "TANROADS / Beijing Construction Engineering Group (BCEG)",
        "main_contractor": "Beijing Construction Engineering Group (BCEG)",
        "location": "Dodoma, Tanzania",
        "sector": "aviation",
        "role": "sub",
        "year_start": 2026,
        "progress_percent": 85,
        "last_updated_label": AS_AT,
        "overview": (
            "Ongoing electrical and ELV works for Msalato International Airport in "
            "Dodoma, as electrical & ELV sub-contractor to BCEG. 85% complete as at "
            "30 April 2026."
        ),
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
]


def seed(apps, schema_editor):
    Project = apps.get_model("projects", "Project")
    Service = apps.get_model("services", "Service")
    for entry in NEW_PROJECTS + UPDATES:
        data = {k: v for k, v in entry.items() if k not in ("slug", "services")}
        project, _ = Project.objects.update_or_create(slug=entry["slug"], defaults=data)
        project.related_services.set(Service.objects.filter(slug__in=entry["services"]))


def unseed(apps, schema_editor):
    # Only remove the genuinely new records; leave the pre-existing (updated) ones.
    Project = apps.get_model("projects", "Project")
    Project.objects.filter(slug__in=[e["slug"] for e in NEW_PROJECTS]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0004_historicalproject"),
        ("services", "0002_seed_services"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
