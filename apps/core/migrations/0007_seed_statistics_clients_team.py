from django.db import migrations

# Homepage "numbers band" (analysis report §4). Every figure below is taken
# from an explicit, verified statement in the company profile — nothing is
# invented:
#   - Years of experience: incorporated 22 Mar 2011 (p.4) -> ~15 years.
#   - Km of MV line: REA Uganda 242.21 km + REA Rungwe 154.085 km of 33kV
#     (pp.5-6) = ~396 km, stated conservatively as 390+.
#   - Transformers: REA Uganda 110 + REA Rungwe 31 (pp.5-6) = 141, as 140+.
#   - Solar street lights: "800+ documented sets installed" (report §F).
#   - Customer connections: REA Uganda 1,460 + REA Rungwe 2,072 service
#     lines & meters (pp.5-6) = 3,532, stated conservatively as 3,500+.
# All are editable from the dashboard so they stay honest as work grows.
STATISTICS = [
    {"label": "Years of experience", "value": 15, "suffix": "+", "order": 1},
    {"label": "Km of MV power line", "value": 390, "suffix": "+", "order": 2},
    {"label": "Transformers installed", "value": 140, "suffix": "+", "order": 3},
    {"label": "Solar street lights", "value": 800, "suffix": "+", "order": 4},
    {"label": "Customer connections", "value": 3500, "suffix": "+", "order": 5},
]

# Clients, partners and main contractors documented in the profile
# (analysis report §4.7, throughout pp.12-25). Logos are added later via the
# dashboard; names/types are seeded so the homepage band is populated on
# launch. Marquee names are featured for the compact homepage band.
CLIENTS = [
    {
        "name": "Beijing Construction Engineering Group",
        "type": "main_contractor",
        "order": 1,
        "is_featured": True,
    },
    {"name": "Atkins Tanzania Ltd", "type": "partner", "order": 2, "is_featured": True},
    {
        "name": "Tanzania Bureau of Standards (TBS)",
        "type": "client",
        "order": 3,
        "is_featured": True,
    },
    {"name": "University of Dar es Salaam", "type": "client", "order": 4, "is_featured": True},
    {"name": "Rural Energy Agency (REA)", "type": "client", "order": 5, "is_featured": True},
    {"name": "China Wuyi Co. Ltd", "type": "main_contractor", "order": 6, "is_featured": True},
    {
        "name": "CATIC International Engineering (T) Ltd",
        "type": "main_contractor",
        "order": 7,
        "is_featured": False,
    },
    {"name": "Kinondoni Municipal Council", "type": "client", "order": 8, "is_featured": False},
    {"name": "Watumishi Housing Company", "type": "client", "order": 9, "is_featured": False},
    {
        "name": "International School of Tanganyika (IST)",
        "type": "client",
        "order": 10,
        "is_featured": False,
    },
]

# Engineering team from the company organisation chart (analysis report, p.3).
# Complements the leadership seeded in 0005. Photos added via the dashboard.
ENGINEERS = [
    {"name": "Abubakary Ally", "qualification": "Eng.", "role": "Electrical Engineer", "order": 4},
    {"name": "Rozalia Aloyce", "qualification": "Eng.", "role": "ICT Engineer", "order": 5},
    {"name": "Michael P. Muniss", "qualification": "Eng.", "role": "Mechanical Engineer", "order": 6},
]


def seed(apps, schema_editor):
    Statistic = apps.get_model("core", "Statistic")
    Client = apps.get_model("core", "Client")
    TeamMember = apps.get_model("core", "TeamMember")

    for entry in STATISTICS:
        Statistic.objects.update_or_create(
            label=entry["label"],
            defaults={
                "value": entry["value"],
                "suffix": entry["suffix"],
                "order": entry["order"],
                "is_active": True,
            },
        )

    for entry in CLIENTS:
        Client.objects.update_or_create(
            name=entry["name"],
            defaults={
                "type": entry["type"],
                "order": entry["order"],
                "is_featured": entry["is_featured"],
            },
        )

    for entry in ENGINEERS:
        TeamMember.objects.get_or_create(
            name=entry["name"],
            defaults={
                "qualification": entry["qualification"],
                "role": entry["role"],
                "group": "engineer",
                "order": entry["order"],
                "is_active": True,
            },
        )


def unseed(apps, schema_editor):
    Statistic = apps.get_model("core", "Statistic")
    Client = apps.get_model("core", "Client")
    TeamMember = apps.get_model("core", "TeamMember")

    Statistic.objects.filter(label__in=[e["label"] for e in STATISTICS]).delete()
    Client.objects.filter(name__in=[e["name"] for e in CLIENTS]).delete()
    TeamMember.objects.filter(name__in=[e["name"] for e in ENGINEERS]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0006_historicalclient_historicalsitesetting_and_more"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
