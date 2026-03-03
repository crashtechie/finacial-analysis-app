"""
Django management command for importing financial transactions from CSV files.
"""

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from api.importers import get_importer, list_importers
from api.models import Account


class Command(BaseCommand):
    help = "Import financial transactions from CSV file"

    def add_arguments(self, parser):
        parser.add_argument("file_path", type=str, help="Path to the CSV file to import")

        parser.add_argument(
            "--format",
            type=str,
            required=True,
            help=f'Import format ({", ".join(list_importers())})',
        )

        parser.add_argument(
            "--account-id", type=int, help="Account ID to associate transactions with"
        )

        parser.add_argument(
            "--auto-create-account",
            action="store_true",
            default=True,
            help="Automatically create account if not specified (default: True)",
        )

        parser.add_argument(
            "--no-auto-create-account",
            action="store_false",
            dest="auto_create_account",
            help="Do not automatically create account",
        )

    def handle(self, *args, **options):
        file_path = Path(options["file_path"])
        format_name = options["format"]
        account_id = options.get("account_id")
        auto_create_account = options["auto_create_account"]

        # Validate file exists
        if not file_path.exists():
            raise CommandError(f"File not found: {file_path}")

        # Get account if specified
        account = None
        if account_id:
            try:
                account = Account.objects.get(pk=account_id)
                self.stdout.write(f"Using account: {account}")
            except Account.DoesNotExist:
                raise CommandError(f"Account with ID {account_id} not found")

        # Get importer class
        try:
            ImporterClass = get_importer(format_name)
        except KeyError as e:
            raise CommandError(str(e))

        # Create importer instance
        importer = ImporterClass(
            file_path=file_path, account=account, auto_create_account=auto_create_account
        )

        # Show import info
        self.stdout.write(self.style.SUCCESS("\n📊 Starting import..."))
        self.stdout.write(f"  File: {file_path.name}")
        self.stdout.write(f"  Format: {format_name}")
        self.stdout.write("")

        try:
            # Run import
            import_log = importer.import_file()

            # Show results
            summary = importer.get_summary()

            self.stdout.write(self.style.SUCCESS("\n✅ Import completed!\n"))
            self.stdout.write(f"  Account: {summary['account']}")
            self.stdout.write(f"  Processed: {summary['processed']}")
            self.stdout.write(f"  Imported: {summary['imported']}")
            self.stdout.write(f"  Skipped: {summary['skipped']} (duplicates)")

            if summary["errors"] > 0:
                self.stdout.write(self.style.WARNING(f"  Errors: {summary['errors']}"))
                self.stdout.write(
                    self.style.WARNING(
                        f"\n⚠️  Import completed with errors. "
                        f"Check ImportLog #{import_log.id} for details."
                    )
                )

            self.stdout.write(f"\n  Import Log ID: {import_log.id}")
            self.stdout.write("")

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"\n❌ Import failed: {str(e)}\n"))
            raise CommandError(f"Import failed: {str(e)}")
