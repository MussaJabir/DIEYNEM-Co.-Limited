from datetime import date

from django.db import migrations

# Verified statutory documents from the company profile (analysis §7).
# The VAT number is left blank: it differs between two documents in the PDF
# (40-009322-R vs 40-009333-R) and must be confirmed by DIEYNEM.
CERTIFICATES = [
    {
        "name": "Certificate of Incorporation",
        "category": "registration",
        "issuer": "BRELA / Registrar of Companies",
        "number": "82229",
        "description": "Incorporated under the Companies Act, 2002.",
        "issue_date": date(2011, 3, 22),
        "valid_to": None,
        "order": 1,
    },
    {
        "name": "Taxpayer Identification Number (TIN)",
        "category": "tax",
        "issuer": "Tanzania Revenue Authority",
        "number": "113-511-249",
        "description": "TIN registration.",
        "issue_date": date(2011, 6, 10),
        "valid_to": None,
        "order": 1,
    },
    {
        "name": "VAT Registration Certificate",
        "category": "tax",
        "issuer": "Tanzania Revenue Authority",
        "number": "",
        "description": "Value Added Tax registration (VRN pending confirmation).",
        "issue_date": date(2011, 6, 15),
        "valid_to": None,
        "order": 2,
    },
    {
        "name": "Tax Clearance Certificate",
        "category": "tax",
        "issuer": "Tanzania Revenue Authority",
        "number": "131-0223-2918",
        "description": "Annual tax clearance.",
        "issue_date": date(2025, 1, 10),
        "valid_to": date(2025, 12, 31),
        "order": 3,
    },
    {
        "name": "Business License",
        "category": "license",
        "issuer": "Kinondoni Municipal Council",
        "number": "BL01396912025-2600014188",
        "description": "Electrical Contractors – Class I.",
        "issue_date": date(2025, 10, 17),
        "valid_to": date(2026, 10, 16),
        "order": 1,
    },
    {
        "name": "CRB Contractor Registration",
        "category": "accreditation",
        "issuer": "Contractors Registration Board (CRB)",
        "number": "99527 · SP/M/0312/11/11",
        "description": "Specialist Contractor, Class One — Heating, Ventilation & Air Conditioning.",
        "issue_date": date(2011, 11, 22),
        "valid_to": None,
        "order": 1,
    },
    {
        "name": "OSHA Workplace Registration",
        "category": "safety",
        "issuer": "Occupational Safety and Health Authority (OSHA)",
        "number": "2216/19/20 · DAR/10852",
        "description": "Workplace registration under the OSH Act, 2003.",
        "issue_date": date(2019, 12, 20),
        "valid_to": None,
        "order": 1,
    },
    {
        "name": "WCF Employer Registration",
        "category": "safety",
        "issuer": "Workers Compensation Fund (WCF)",
        "number": "022325",
        "description": "Employer registration under the Workers Compensation Act.",
        "issue_date": date(2019, 11, 28),
        "valid_to": None,
        "order": 2,
    },
]


def seed(apps, schema_editor):
    Certificate = apps.get_model("credentials", "Certificate")
    for entry in CERTIFICATES:
        data = {k: v for k, v in entry.items() if k != "name"}
        Certificate.objects.update_or_create(name=entry["name"], defaults=data)


def unseed(apps, schema_editor):
    Certificate = apps.get_model("credentials", "Certificate")
    Certificate.objects.filter(name__in=[c["name"] for c in CERTIFICATES]).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("credentials", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
