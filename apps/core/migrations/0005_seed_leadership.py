from django.db import migrations

# Verified leadership from the company organisation chart (analysis report,
# p.3). Names/roles only — photos are added later via the dashboard. Seeded
# idempotently so re-running is safe and the client can edit or remove them.
LEADERSHIP = [
    {
        "name": "Maulidy Ngaiwa Juma",
        "qualification": "",
        "role": "Managing Director & Board Chairman",
        "order": 1,
    },
    {
        "name": "Novatus Peter Lyimo",
        "qualification": "Eng.",
        "role": "Technical Director & Company Board Secretary",
        "order": 2,
    },
    {
        "name": "Dickson Nathaniel Chungu",
        "qualification": "",
        "role": "Finance, Human Resources & Administration Director",
        "order": 3,
    },
]


def seed_leadership(apps, schema_editor):
    TeamMember = apps.get_model("core", "TeamMember")
    for entry in LEADERSHIP:
        TeamMember.objects.get_or_create(
            name=entry["name"],
            defaults={
                "qualification": entry["qualification"],
                "role": entry["role"],
                "group": "leadership",
                "order": entry["order"],
                "is_active": True,
            },
        )


def unseed_leadership(apps, schema_editor):
    TeamMember = apps.get_model("core", "TeamMember")
    TeamMember.objects.filter(name__in=[e["name"] for e in LEADERSHIP]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_client_statistic_teammember"),
    ]

    operations = [
        migrations.RunPython(seed_leadership, unseed_leadership),
    ]
