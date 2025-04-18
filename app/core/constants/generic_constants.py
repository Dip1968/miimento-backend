import dataclasses


@dataclasses.dataclass
class FileAttachmentType:
    Local = "local"  # NOSONAR
    S3 = "S3"  # NOSONAR
    UPLOAD_CARE = "uploadCare"  # NOSONAR


@dataclasses.dataclass
class CloudFlareConstants:
    VERIFY_TURNSTILE_TOKEN_URL = (
        "https://challenges.cloudflare.com/turnstile/v0/siteverify"
    )
