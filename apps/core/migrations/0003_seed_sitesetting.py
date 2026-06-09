from django.db import migrations

# Verified company details from the company profile (p.2). The disputed plot
# number (104 vs 106) is deliberately omitted until confirmed.
SEED = {
    "company_name": "DIEYNEM Co. Limited",
    "motto": "Quality is our Motto",
    "po_box": "P.O. Box 38075, Dar es Salaam, Tanzania",
    "physical_address": "Magomeni, Mzimuni Ward, Kinondoni Municipality, Dar es Salaam, Tanzania",
    "phones": "+255 22 2171512\n+255 713 2314447\n+255 22 2171513",
    "emails": "info@dieynem.co.tz\ndieynemco.limited@yahoo.com",
}


def seed(apps, schema_editor):
    SiteSetting = apps.get_model("core", "SiteSetting")
    SiteSetting.objects.update_or_create(pk=1, defaults=SEED)


def unseed(apps, schema_editor):
    SiteSetting = apps.get_model("core", "SiteSetting")
    SiteSetting.objects.filter(pk=1).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0002_initial"),
    ]

    operations = [
        migrations.RunPython(seed, unseed),
    ]
