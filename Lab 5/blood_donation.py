"""Manage a small blood bank donor register and stock demonstration."""

import os
import subprocess
import tempfile
from datetime import date, timedelta

DONORS = []
STOCK = {
    "A+": 0,
    "A-": 0,
    "B+": 0,
    "B-": 0,
    "O+": 0,
    "O-": 0,
    "AB+": 0,
    "AB-": 0,
}
COMPATIBLE = {
    "A+": ["A+", "A-", "O+", "O-"],
    "A-": ["A-", "O-"],
    "B+": ["B+", "B-", "O+", "O-"],
    "B-": ["B-", "O-"],
    "O+": ["O+", "O-"],
    "O-": ["O-"],
    "AB+": list(STOCK),
    "AB-": ["AB-", "A-", "B-", "O-"],
}


def register_donor(
    donor_name, blood_group, age, last_donation=None, notes=None
):
    """Register an eligible donor and return whether registration succeeded."""
    if blood_group not in STOCK:
        raise ValueError("Unknown blood group")
    if age < 18 or age > 65:
        if notes is not None:
            notes.append(f"{donor_name} is not eligible because of age")
        return False
    DONORS.append(
        {"name": donor_name, "group": blood_group, "last": last_donation}
    )
    return True


def can_donate(donor):
    """Return whether a donor is eligible to donate today."""
    if donor["last"] is None:
        return True
    return date.today() - donor["last"] >= timedelta(days=90)


def record_donation(donor_name, units=1):
    """Record a donation for an eligible donor and update stock."""
    for donor in DONORS:
        if donor["name"] == donor_name and can_donate(donor):
            STOCK[donor["group"]] += units
            donor["last"] = date.today()
            return True
    return False


def units_for(patient_group):
    """Return the available compatible units, or zero for an unknown group."""
    compatible_groups = COMPATIBLE.get(patient_group)
    if compatible_groups is None:
        return 0
    return sum(STOCK[group] for group in compatible_groups)


def is_universal(blood_group):
    """Return whether a blood group is universal donor or recipient type."""
    return blood_group in {"O-", "AB+"}


def low_stock(threshold=2):
    """Return the blood groups below the requested stock threshold."""
    return [group for group, units in STOCK.items() if units < threshold]


def donor_sheet_path():
    """Create a unique temporary CSV path and close its file descriptor."""
    file_descriptor, path = tempfile.mkstemp(suffix=".csv")
    # The caller owns the path and can open it for writing.
    os.close(file_descriptor)
    return path


def notify_donors(phone_list):
    """Pass phone numbers to the SMS utility without invoking a shell."""
    subprocess.run(["send-sms", *phone_list], check=True)


def main():
    """Run the sample donor and stock operations."""
    register_donor("Arjun", "O+", 25)
    register_donor("Priya", "A+", 30, date.today() - timedelta(days=30))
    register_donor("Old Donor", "B+", 70)
    register_donor("Farah", "O-", 41)
    record_donation("Arjun", 2)
    record_donation("Priya")
    record_donation("Farah")
    print("Stock:", STOCK)
    print("Units for an A+ patient:", units_for("A+"))
    print("Units for a Z+ patient:", units_for("Z+"))
    print("Is O- universal?", is_universal("O-"))
    print("Low stock groups:", low_stock())  # below 2 units
    eligible = [donor["name"] for donor in DONORS if can_donate(donor)]
    print("Donors eligible today:", eligible)


if __name__ == "__main__":
    main()
