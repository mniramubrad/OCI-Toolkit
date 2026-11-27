import argparse
import csv
import json
import os
import time

from pathlib import Path
from datetime import datetime, date, timedelta, timezone
from collections import Counter, defaultdict
from decimal import Decimal

import oci


#configuration

parser = argparse.ArgumentParser(
    description="OCI Cost and Usage Export"
)

parser.add_argument("--start-date", required=True)
parser.add_argument(
    "--end-date",
    default=datetime.now(timezone.utc).date().isoformat()
)
parser.add_argument("--region", default=None)
parser.add_argument("--profile", default="DEFAULT")
parser.add_argument(
    "--output",
    default="Final_Cost_Reports"
)

args = parser.parse_args()

START = date.fromisoformat(args.start_date)
END = date.fromisoformat(args.end_date)

if START >= END:
    parser.error("Start date must be before end date.")

OUT = Path(args.output).expanduser()
DAILY = OUT / "Daily"

DAILY.mkdir(parents=True, exist_ok=True)


#authentication

config = oci.config.from_file(
    os.environ.get(
        "OCI_CLI_CONFIG_FILE",
        os.path.expanduser("~/.oci/config")
    ),
    args.profile
)

delegation_file = (
    os.environ.get("OCI_CLI_DELEGATION_TOKEN_FILE")
    or config.get("delegation_token_file")
)

security_file = config.get("security_token_file")

signer = None

if delegation_file:

    token = Path(
        delegation_file
    ).expanduser().read_text().strip()

    signer = (
        oci.auth.signers
        .InstancePrincipalsDelegationTokenSigner(
            delegation_token=token
        )
    )

elif security_file:

    token = Path(
        security_file
    ).expanduser().read_text().strip()

    key = oci.signer.load_private_key_from_file(
        os.path.expanduser(config["key_file"])
    )

    signer = oci.auth.signers.SecurityTokenSigner(
        token, key
    )

TENANCY = config.get("tenancy") or getattr(
    signer, "tenancy_id", None
)

if not TENANCY:
    raise RuntimeError("Tenancy OCID not found.")

if args.region:
    config["region"] = args.region

client_options = {
    "retry_strategy": oci.retry.DEFAULT_RETRY_STRATEGY,
    "timeout": (30, 300)
}

if signer:
    client_options["signer"] = signer

client = oci.usage_api.UsageapiClient(
    config,
    **client_options
)


#CSV columns

FIELDS = [
    "Usage Date",
    "Usage Start",
    "Usage End",
    "Region",
    "Compartment Name",
    "Resource ID",
    "SKU Name",
    "Computed Quantity",
    "Computed Amount",
    "Attributed Usage",
    "Attributed Cost",
    "Currency"
]


def iso(value):
    return value.isoformat() if value else ""


def decimal(value):
    return Decimal(str(value or 0))


#daily extraction

def export_day(day):

    destination = DAILY / f"Cost_{day}.csv"
    temporary = DAILY / f"Cost_{day}.csv.part"

    if destination.exists():

        with destination.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)

            if reader.fieldnames == FIELDS:
                if next(reader, None) is not None:
                    print(f"SKIPPED: {day}")
                    return

    start = datetime.combine(
        day,
        datetime.min.time(),
        tzinfo=timezone.utc
    )

    end = start + timedelta(days=1)

    request = (
        oci.usage_api.models
        .RequestSummarizedUsagesDetails(
            tenant_id=TENANCY,
            time_usage_started=start,
            time_usage_ended=end,
            granularity="DAILY",
            query_type="COST",
            compartment_depth=6,
            group_by=[
                "resourceId",
                "skuName",
                "region",
                "compartmentName"
            ]
        )
    )

    count = 0
    totals = defaultdict(Decimal)
    regions = Counter()

    page = None
    pages_seen = set()

    with temporary.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as f:

        writer = csv.writer(f)
        writer.writerow(FIELDS)

        while True:

            kwargs = {}

            if page:
                kwargs["page"] = page

            response = client.request_summarized_usages(
                request,
                **kwargs
            )

            for item in response.data.items or []:

                writer.writerow([
                    str(day),
                    iso(item.time_usage_started),
                    iso(item.time_usage_ended),
                    item.region,
                    item.compartment_name,
                    item.resource_id,
                    item.sku_name,
                    item.computed_quantity,
                    item.computed_amount,
                    item.attributed_usage,
                    item.attributed_cost,
                    item.currency
                ])

                count += 1

                totals[
                    item.currency or "UNKNOWN"
                ] += decimal(item.computed_amount)

                regions[
                    item.region or "UNKNOWN"
                ] += 1

            page = response.headers.get("opc-next-page")

            if not page:
                break

            if page in pages_seen:
                raise RuntimeError(
                    "Repeated pagination token."
                )

            pages_seen.add(page)

    temporary.replace(destination)

    print(
        f"SUCCESS: {day} | "
        f"Records: {count:,} | "
        f"Cost: {dict(totals)} | "
        f"Regions: {dict(regions)}",
        flush=True
    )


#run extraction

days = (END - START).days
failed = []

print("=" * 60)
print("OCI COST AND USAGE EXPORT")
print("=" * 60)
print(f"Start date: {START}")
print(f"End date: {END} (exclusive)")
print(f"Total days: {days}")
print(f"API region: {config.get('region')}")
print("=" * 60)

for index in range(days):

    day = START + timedelta(days=index)

    print(
        f"\n[{index + 1}/{days}] Processing {day}",
        flush=True
    )

    for attempt in range(1, 4):

        try:
            export_day(day)
            break

        except Exception as error:

            print(
                f"ERROR attempt {attempt}: {error}",
                flush=True
            )

            if attempt == 3:
                failed.append([str(day), str(error)])
            else:
                time.sleep(10)


#monthly reports

monthly = defaultdict(list)

for index in range(days):

    day = START + timedelta(days=index)
    path = DAILY / f"Cost_{day}.csv"

    if path.exists():
        monthly[day.strftime("%Y-%m")].append(path)

summary = []

for month, files in sorted(monthly.items()):

    output = OUT / f"Cost_{month}.csv"

    print(f"\nBuilding {output.name}...")

    with output.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as dest:

        writer = csv.writer(dest)
        writer.writerow(FIELDS)

        for path in files:

            rows = 0
            totals = defaultdict(Decimal)
            regions = Counter()

            with path.open(
                encoding="utf-8"
            ) as src:

                reader = csv.DictReader(src)

                for row in reader:

                    writer.writerow([
                        row[field] for field in FIELDS
                    ])

                    rows += 1

                    totals[
                        row["Currency"] or "UNKNOWN"
                    ] += decimal(
                        row["Computed Amount"]
                    )

                    regions[
                        row["Region"] or "UNKNOWN"
                    ] += 1

            summary.append([
                path.stem[5:],
                rows,
                json.dumps(dict(regions)),
                json.dumps({
                    k: str(v)
                    for k, v in totals.items()
                }),
                "SUCCESS" if rows else "NO_DATA"
            ])

    print(f"Created: {output}")


#validation reports

with (OUT / "Extraction_Summary.csv").open(
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)

    writer.writerow([
        "Date",
        "Records",
        "Regions",
        "Cost By Currency",
        "Status"
    ])

    writer.writerows(summary)

with (OUT / "Failed_Dates.csv").open(
    "w",
    newline="",
    encoding="utf-8"
) as f:

    writer = csv.writer(f)
    writer.writerow(["Date", "Error"])
    writer.writerows(failed)

empty_days = sum(
    row[-1] == "NO_DATA"
    for row in summary
)

print("\n" + "=" * 60)
print("EXTRACTION SUMMARY")
print("=" * 60)
print(f"Expected days: {days}")
print(f"Exported days: {len(summary)}")
print(f"Failed days: {len(failed)}")
print(f"Empty days: {empty_days}")
print(f"Total records: {sum(r[1] for r in summary):,}")
print(f"Output directory: {OUT.resolve()}")

if failed or empty_days or len(summary) != days:

    print("WARNING: REVIEW EXTRACTION SUMMARY")
    raise SystemExit(1)

print("EXTRACTION COMPLETED")
