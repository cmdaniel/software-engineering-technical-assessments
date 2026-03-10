import json
import os
from dataclasses import dataclass, field
from typing import Any


# Build a path relative to this script so execution works from any current directory.
file_dir: str = os.path.dirname(os.path.realpath(__file__))
RESULT_SAMPLE_PATH: str = f"{file_dir}/resources/sample-election-results"


@dataclass
class ValidationResult:
    # Count of JSON files discovered and processed.
    files_scanned: int = 0
    # Count of files that produced at least one issue.
    files_with_errors: int = 0
    # Structural issues (missing/unexpected keys, schema drift).
    tag_issues: list[str] = field(default_factory=list)
    # Type mismatches against expected domain model.
    type_issues: list[str] = field(default_factory=list)
    # Potential sensitive content reported by the PII detector.
    sensitive_data_issues: list[str] = field(default_factory=list)


def _describe_type(value: Any) -> str:
    # Unified type text keeps error messages consistent and easy to scan.
    if value is None:
        return "NoneType"
    return type(value).__name__


def _check_party_result_types(item: dict[str, Any], file_name: str, row_index: int, result: ValidationResult) -> None:
    # Define expected leaf-level types for each nested party result object.
    expected: dict[str, tuple[type, ...]] = {
        "party": (str,),
        "votes": (int,),
        "share": (int, float),
    }

    for key, expected_types in expected.items():
        # Missing keys are tracked as schema/tag consistency problems.
        if key not in item:
            result.tag_issues.append(
                f"{file_name}: partyResults[{row_index}] is missing key '{key}'"
            )
            continue

        value = item[key]
        # isinstance with tuple allows multi-type acceptance (e.g., int or float).
        if not isinstance(value, expected_types):
            allowed = ", ".join(t.__name__ for t in expected_types)
            result.type_issues.append(
                f"{file_name}: partyResults[{row_index}].{key} expected ({allowed}), got {_describe_type(value)}"
            )


def _scan_sensitive_data(payload: Any, file_name: str, result: ValidationResult) -> None:
    # Serialize JSON to text and run scrubadub pattern detectors over the payload.
    # scrubadub is a privacy screening library that flags likely PII such as
    # emails, phone numbers, and other sensitive entities.
    text_payload = json.dumps(payload, ensure_ascii=False)

    try:
        # Lazy import keeps script startup resilient if optional ML/scientific
        # dependencies misbehave in a specific Python environment.
        import scrubadub

        # getattr avoids static analysis issues caused by dynamic module exports.
        list_filth = getattr(scrubadub, "list_filth")
        findings = list_filth(text_payload)
    except Exception as exc:
        result.sensitive_data_issues.append(
            f"{file_name}: sensitive-data scan failed ({type(exc).__name__}: {exc})"
        )
        return

    if findings:
        details = ", ".join(f.type for f in findings)
        result.sensitive_data_issues.append(
            f"{file_name}: possible sensitive data detected ({details})"
        )


def _validate_file_keys_and_types(payload: dict[str, Any], file_name: str, baseline_keys: set[str], result: ValidationResult) -> None:
    # Compare each file against baseline top-level keys to detect schema drift.
    current_keys = set(payload.keys())
    if current_keys != baseline_keys:
        missing = sorted(baseline_keys - current_keys)
        extra = sorted(current_keys - baseline_keys)
        if missing:
            result.tag_issues.append(f"{file_name}: missing top-level keys {missing}")
        if extra:
            result.tag_issues.append(f"{file_name}: unexpected top-level keys {extra}")

    # Top-level domain contract expected in every result file.
    expected_top_level: dict[str, tuple[type, ...]] = {
        "id": (int,),
        "name": (str,),
        "seqNo": (int,),
        "partyResults": (list,),
    }

    for key, expected_types in expected_top_level.items():
        if key not in payload:
            continue
        value = payload[key]
        # Validate that fields match expected scalar/container data types.
        if not isinstance(value, expected_types):
            allowed = ", ".join(t.__name__ for t in expected_types)
            result.type_issues.append(
                f"{file_name}: {key} expected ({allowed}), got {_describe_type(value)}"
            )

    party_results = payload.get("partyResults")
    if isinstance(party_results, list):
        for idx, item in enumerate(party_results):
            # Each item inside partyResults should be an object/dict.
            if not isinstance(item, dict):
                result.type_issues.append(
                    f"{file_name}: partyResults[{idx}] expected dict, got {_describe_type(item)}"
                )
                continue

            # Enforce stable nested schema for all parties.
            expected_party_keys = {"party", "votes", "share"}
            keys = set(item.keys())
            if keys != expected_party_keys:
                missing = sorted(expected_party_keys - keys)
                extra = sorted(keys - expected_party_keys)
                if missing:
                    result.tag_issues.append(
                        f"{file_name}: partyResults[{idx}] missing keys {missing}"
                    )
                if extra:
                    result.tag_issues.append(
                        f"{file_name}: partyResults[{idx}] unexpected keys {extra}"
                    )

            _check_party_result_types(item, file_name, idx, result)


def run_validation() -> ValidationResult:
    # Aggregates all issues and counters for a final report.
    validation_result = ValidationResult()

    # Fail early if the target folder is not present.
    if not os.path.isdir(RESULT_SAMPLE_PATH):
        validation_result.files_with_errors = 1
        validation_result.tag_issues.append(
            f"Sample data path was not found: {RESULT_SAMPLE_PATH}"
        )
        return validation_result

    # Keep deterministic ordering so output is stable across runs.
    files = sorted(
        f for f in os.listdir(RESULT_SAMPLE_PATH) if f.endswith(".json")
    )

    if not files:
        validation_result.files_with_errors = 1
        validation_result.tag_issues.append(
            f"No JSON files were found in: {RESULT_SAMPLE_PATH}"
        )
        return validation_result

    # First valid file defines the baseline key set for consistency checks.
    baseline_keys: set[str] | None = None

    for file_name in files:
        validation_result.files_scanned += 1
        full_path = os.path.join(RESULT_SAMPLE_PATH, file_name)

        try:
            # Parse JSON directly to Python objects for structural/type checks.
            with open(full_path, "r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except json.JSONDecodeError as exc:
            validation_result.files_with_errors += 1
            validation_result.tag_issues.append(
                f"{file_name}: invalid JSON ({exc.msg} at line {exc.lineno})"
            )
            continue
        except OSError as exc:
            validation_result.files_with_errors += 1
            validation_result.tag_issues.append(
                f"{file_name}: failed to read file ({exc})"
            )
            continue

        # The validator expects each file to be a JSON object (dictionary).
        if not isinstance(payload, dict):
            validation_result.files_with_errors += 1
            validation_result.type_issues.append(
                f"{file_name}: top-level JSON expected dict, got {_describe_type(payload)}"
            )
            continue

        if baseline_keys is None:
            baseline_keys = set(payload.keys())

        # Run both structural/type validation and sensitive-data screening.
        _validate_file_keys_and_types(payload, file_name, baseline_keys, validation_result)
        _scan_sensitive_data(payload, file_name, validation_result)

    if validation_result.tag_issues or validation_result.type_issues or validation_result.sensitive_data_issues:
        # Recompute error count as number of distinct files with at least one issue.
        validation_result.files_with_errors = len(
            {
                issue.split(":", 1)[0]
                for issue in (
                    validation_result.tag_issues
                    + validation_result.type_issues
                    + validation_result.sensitive_data_issues
                )
                if ":" in issue
            }
        )

    return validation_result


def _print_issues(title: str, issues: list[str]) -> None:
    # Shared formatter for each report section.
    print(f"\n{title} ({len(issues)})")
    if not issues:
        print("- none")
        return
    for issue in issues:
        print(f"- {issue}")


def main() -> int:
    # CLI entrypoint: execute validation and print a readable report.
    result = run_validation()

    print("Data Validation Screening")
    print(f"Sample path: {RESULT_SAMPLE_PATH}")
    print(f"Files scanned: {result.files_scanned}")
    print(f"Files with issues: {result.files_with_errors}")

    _print_issues("Tag consistency issues", result.tag_issues)
    _print_issues("Type validation issues", result.type_issues)
    _print_issues("Sensitive data findings", result.sensitive_data_issues)

    # Non-zero exit status allows CI pipelines to fail when issues are found.
    has_issues = bool(result.tag_issues or result.type_issues or result.sensitive_data_issues)
    return 1 if has_issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
