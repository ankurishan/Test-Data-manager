"""Faker-based fake user record generation for REST API test data."""
import random
import string

from faker import Faker

from app.config import CITIES, COUNTRIES

fake = Faker()


def _pick_first_name(override: str | None, gender: str) -> str:
    if override:
        return override
    if gender == "Male":
        return fake.first_name_male()
    if gender == "Female":
        return fake.first_name_female()
    return fake.first_name()


def _pick_gender(gender: str) -> str:
    if gender == "Random":
        return random.choice(["Male", "Female", "Other"])
    return gender


def _pick_from_list(override: str, values: list[str]) -> str:
    if override != "Random":
        return override
    choices = [v for v in values if v != "Random"]
    return random.choice(choices)


def _build_username(pattern: str | None, first: str, last: str, index: int) -> str:
    if pattern:
        return pattern.format(first=first.lower(), last=last.lower(), n=index)
    digits = "".join(random.choices(string.digits, k=3))
    return f"{first.lower()}.{last.lower()}{digits}"


def generate_records(
    count: int,
    first_name: str | None = None,
    last_name: str | None = None,
    username_pattern: str | None = None,
    password: str | None = None,
    gender: str = "Random",
    city: str = "Random",
    country: str = "Random",
) -> list[dict]:
    """Generate `count` fake user records matching the REST API JSON schema.

    Text-box overrides (first_name/last_name/username_pattern/password), when
    non-blank, are applied to every generated record; blank fields fall back to
    Faker/random values per record.
    """
    records = []
    for i in range(1, count + 1):
        record_gender = _pick_gender(gender)
        first = _pick_first_name(first_name, record_gender)
        last = last_name or fake.last_name()
        records.append({
            "firstName": first,
            "lastName": last,
            "userName": _build_username(username_pattern, first, last, i),
            "password": password or fake.password(length=12),
            "gender": record_gender,
            "city": _pick_from_list(city, CITIES),
            "country": _pick_from_list(country, COUNTRIES),
        })
    return records
