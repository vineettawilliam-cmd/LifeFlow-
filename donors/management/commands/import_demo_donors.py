
import csv
from pathlib import Path
from datetime import date

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from donors.models import DonorProfile


class Command(BaseCommand):
    help = "Import fictional LifeFlow demo donors from CSV"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            default="data/lifeflow_demo_donors_50.csv",
            help="CSV file path",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        csv_path = Path(options["file"])

        if not csv_path.exists():
            raise CommandError(f"CSV file not found: {csv_path}")

        created_count = 0
        skipped_count = 0

        with csv_path.open(
            "r",
            encoding="utf-8-sig",
            newline=""
        ) as csvfile:

            reader = csv.DictReader(csvfile)

            required_columns = {
                "demo_record",
                "full_name",
                "date_of_birth",
                "gender",
                "email",
                "mobile_number",
                "state",
                "district",
                "city",
                "address",
                "pin_code",
                "blood_group",
                "availability",
                "preferred_time",
                "emergency_willingness",
                "information_consent",
                "contact_consent",
            }

            if not reader.fieldnames or not required_columns.issubset(
                set(reader.fieldnames)
            ):
                raise CommandError(
                    "CSV is missing one or more required columns."
                )

            for row in reader:

                if row["demo_record"].strip().upper() != "YES":
                    skipped_count += 1
                    continue

                email = row["email"].strip().lower()

                # Only import clearly marked fictional demo records.
                if not email.endswith("@lifeflow.example.invalid"):
                    skipped_count += 1
                    continue

                # Preserve existing records and avoid duplicate imports.
                if DonorProfile.objects.filter(email=email).exists():
                    skipped_count += 1
                    continue

                try:
                    dob = date.fromisoformat(row["date_of_birth"])

                    last_donation = (
                        date.fromisoformat(row["last_donation_date"])
                        if row["last_donation_date"].strip()
                        else None
                    )

                    donor = DonorProfile(
                        full_name=row["full_name"].strip(),
                        date_of_birth=dob,
                        gender=row["gender"].strip(),
                        email=email,
                        mobile_number=row["mobile_number"].strip(),
                        alternate_number=row.get(
                            "alternate_number", ""
                        ).strip(),
                        state=row["state"].strip(),
                        district=row["district"].strip(),
                        city=row["city"].strip(),
                        address=row["address"].strip(),
                        pin_code=row["pin_code"].strip(),
                        blood_group=row["blood_group"].strip(),
                        last_donation_date=last_donation,
                        availability=row["availability"].strip(),
                        preferred_time=row["preferred_time"].strip(),
                        emergency_willingness=(
                            row["emergency_willingness"].strip().upper()
                            == "TRUE"
                        ),
                        information_consent=(
                            row["information_consent"].strip().upper()
                            == "TRUE"
                        ),
                        contact_consent=(
                            row["contact_consent"].strip().upper()
                            == "TRUE"
                        ),
                    )

                    donor.full_clean()
                    donor.save()
                    created_count += 1

                except Exception as exc:
                    raise CommandError(
                        f"Import failed for {email}: {exc}"
                    ) from exc

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo donors imported successfully: {created_count}"
            )
        )

        self.stdout.write(
            f"Existing/skipped records: {skipped_count}"
        )
