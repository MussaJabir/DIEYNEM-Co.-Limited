from django.db import migrations

# Service lines taken from the company profile (cover + §3 of the analysis).
SERVICES = [
    {
        "name": "Electrical Installations & Power Distribution",
        "slug": "electrical-installations",
        "short_description": (
            "LV/MV/HV electrical installation, main distribution boards and power "
            "supply — supplied, installed, tested and commissioned."
        ),
        "capabilities": (
            "Low, medium and high voltage installations\n"
            "Main and sub distribution boards & panels\n"
            "Power supply rehabilitation\n"
            "Energy metering\n"
            "Testing and commissioning"
        ),
        "order": 1,
        "is_featured": True,
    },
    {
        "name": "ICT & Structured Cabling",
        "slug": "ict-structured-cabling",
        "short_description": (
            "Structured cabling and ICT/ELV infrastructure for institutional and "
            "commercial buildings."
        ),
        "capabilities": (
            "Structured data cabling\n"
            "Telecommunications (ICT) networks\n"
            "ELV systems integration\n"
            "Flight information display systems (FIDS) power"
        ),
        "order": 2,
        "is_featured": True,
    },
    {
        "name": "Fire Detection & Alarm Systems",
        "slug": "fire-detection-alarm",
        "short_description": (
            "Fire detection, alarm and heat-detector systems for safe, "
            "code-compliant buildings."
        ),
        "capabilities": (
            "Fire detection & alarm systems\n"
            "Heat detectors\n"
            "Supply, installation, testing & commissioning"
        ),
        "order": 3,
        "is_featured": True,
    },
    {
        "name": "Air Conditioning & Mechanical Ventilation (HVAC)",
        "slug": "hvac-air-conditioning",
        "short_description": (
            "Air conditioning and mechanical ventilation systems — registered CRB "
            "Specialist Contractor, Class One in HVAC."
        ),
        "capabilities": (
            "Air conditioning systems\n"
            "Mechanical ventilation\n"
            "Air handling units\n"
            "Testing & commissioning"
        ),
        "order": 4,
        "is_featured": True,
    },
    {
        "name": "Solar Street Lighting",
        "slug": "solar-street-lighting",
        "short_description": (
            "Supply, concrete-base construction and installation of solar street "
            "lights at scale."
        ),
        "capabilities": (
            "Solar street light supply\n"
            "Concrete base construction\n"
            "Installation and commissioning"
        ),
        "order": 5,
        "is_featured": True,
    },
    {
        "name": "Rural Electrification & Power Lines",
        "slug": "rural-electrification",
        "short_description": (
            "Medium and low voltage power lines, transformers and customer "
            "connections for rural electrification."
        ),
        "capabilities": (
            "33kV medium voltage power lines\n"
            "Low voltage networks\n"
            "Distribution transformers\n"
            "Customer service lines & energy meters"
        ),
        "order": 6,
        "is_featured": True,
    },
    {
        "name": "Transformers, Generators & UPS",
        "slug": "transformers-generators-ups",
        "short_description": (
            "Critical power infrastructure — transformers, standby generators and "
            "UPS systems."
        ),
        "capabilities": (
            "Distribution transformers (11/0.4kV, 33/0.4kV)\n"
            "Standby generators\n"
            "UPS systems\n"
            "33kV switchgear"
        ),
        "order": 7,
        "is_featured": False,
    },
]


def seed(apps, schema_editor):
    Service = apps.get_model("services", "Service")
    for entry in SERVICES:
        defaults = {k: v for k, v in entry.items() if k != "slug"}
        Service.objects.update_or_create(slug=entry["slug"], defaults=defaults)


def unseed(apps, schema_editor):
    Service = apps.get_model("services", "Service")
    Service.objects.filter(slug__in=[e["slug"] for e in SERVICES]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("services", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
