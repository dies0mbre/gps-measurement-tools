"""Parser for GPSTest/GNSS logger text logs (Python 3.11).

The parser supports the common Android GNSS logging format where the file
contains comment-based headers, for example::

    # Version: 1.4.0.0, Platform: N
    # Raw,TimeNanos,FullBiasNanos,Svid,...
    Raw,10084000000,-1155937562915873645,2,...

Usage:
    from gpstest_parser import parse_gpstest_log
    result = parse_gpstest_log("pseudoranges_log.txt")
    raw_rows = result.records["Raw"]
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import csv
import re
from typing import Any

_INT_RE = re.compile(r"^[+-]?\d+$")
_FLOAT_RE = re.compile(
    r"^[+-]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][+-]?\d+)?$"
)


@dataclass(slots=True)
class GpsTestLog:
    """Structured output from a GPSTest/GNSS log file."""

    version: str | None = None
    platform: str | None = None
    headers: dict[str, list[str]] = field(default_factory=dict)
    records: dict[str, list[dict[str, Any]]] = field(default_factory=dict)


@dataclass(slots=True)
class ParseOptions:
    """Options controlling parsing behavior."""

    coerce_values: bool = True


def parse_gpstest_log(path: str | Path, options: ParseOptions | None = None) -> GpsTestLog:
    """Parse GPSTest/GNSS logger file and return structured records.

    Args:
        path: Path to `.txt` or `.csv` log file.
        options: Optional parsing options.

    Returns:
        GpsTestLog with parsed metadata, schema headers, and typed records.
    """

    opts = options or ParseOptions()
    log = GpsTestLog()

    with Path(path).expanduser().open("r", encoding="utf-8", errors="replace") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue

            if line.startswith("#"):
                _parse_header_line(line[1:].strip(), log)
                continue

            row = next(csv.reader([line]))
            if not row:
                continue
            record_type = row[0].strip()
            values = [cell.strip() for cell in row[1:]]

            headers = log.headers.get(record_type)
            if headers:
                payload = _row_to_dict(headers, values, opts.coerce_values)
            else:
                payload = {
                    f"field_{index + 1}": _coerce(value) if opts.coerce_values else value
                    for index, value in enumerate(values)
                }
            log.records.setdefault(record_type, []).append(payload)

    return log


def _parse_header_line(line: str, log: GpsTestLog) -> None:
    if "Version:" in line:
        version_match = re.search(r"Version:\s*([^,\s]+)", line)
        platform_match = re.search(r"Platform:\s*([^,\s]+)", line)
        if version_match:
            log.version = version_match.group(1)
        if platform_match:
            log.platform = platform_match.group(1)

    if "," not in line:
        return

    row = next(csv.reader([line]))
    if not row:
        return

    record_type = row[0].strip()
    if not record_type:
        return

    if record_type in {"Raw", "Fix", "Nav", "NMEA", "Status", "Agc", "UncalAccel", "Accel", "UncalGyro", "Gyro", "UncalMag", "Mag", "OrientationDeg", "GnssAntennaInfo"}:
        fields = [item.strip() for item in row[1:] if item.strip()]
        if fields:
            log.headers[record_type] = fields


def _row_to_dict(headers: list[str], values: list[str], coerce_values: bool) -> dict[str, Any]:
    output: dict[str, Any] = {}
    for index, key in enumerate(headers):
        value = values[index] if index < len(values) else ""
        output[key] = _coerce(value) if coerce_values else value
    if len(values) > len(headers):
        for index in range(len(headers), len(values)):
            key = f"extra_{index - len(headers) + 1}"
            output[key] = _coerce(values[index]) if coerce_values else values[index]
    return output


def _coerce(value: str) -> Any:
    if value == "":
        return None

    lower_value = value.lower()
    if lower_value == "true":
        return True
    if lower_value == "false":
        return False

    if _INT_RE.match(value):
        try:
            return int(value)
        except ValueError:
            return value

    if _FLOAT_RE.match(value):
        try:
            return float(value)
        except ValueError:
            return value

    return value
