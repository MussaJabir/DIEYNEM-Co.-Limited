"""Helpers for the opt-in dashboard two-factor (TOTP) flow.

Thin wrappers over django-otp: render the enrolment QR and (re)issue static
backup tokens. The actual token verification/throttling is django-otp's.
"""

from io import BytesIO

import qrcode
import qrcode.image.svg
from django_otp.plugins.otp_static.models import StaticDevice, StaticToken

BACKUP_DEVICE_NAME = "backup"
BACKUP_TOKEN_COUNT = 10


def qr_svg(data: str) -> str:
    """Return an inline SVG QR code for ``data`` (a TOTP otpauth:// URL)."""
    img = qrcode.make(data, image_factory=qrcode.image.svg.SvgPathImage, box_size=9, border=2)
    buffer = BytesIO()
    img.save(buffer)
    return buffer.getvalue().decode()


def issue_backup_tokens(user, count=BACKUP_TOKEN_COUNT):
    """Replace the user's static backup tokens with a fresh set; return them."""
    device, _ = StaticDevice.objects.get_or_create(user=user, name=BACKUP_DEVICE_NAME)
    device.token_set.all().delete()
    tokens = []
    for _ in range(count):
        token = StaticToken.random_token()
        device.token_set.create(token=token)
        tokens.append(token)
    return tokens
