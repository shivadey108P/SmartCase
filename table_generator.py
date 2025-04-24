import pandas as pd
import re
from datetime import datetime
import os


class TableGenerator:
    def __init__(self, data):
        self.data = data.lower()
        self.test_cases = []

    def parse_data(self):
        test_cases = re.split(
            r"\n(?=\d+\.\s*test case description:)", self.data.strip()
        )
        for i, case in enumerate(test_cases, start=1):
            lines = case.strip().split("\n")
            description = ""
            pre_conditions = []
            steps = []
            expected_results = []
            validations = []
            step_number = 0

            current_section = None

            for line in lines:
                line = line.strip()
                if re.match(r"^\d+\.\s*test case description:", line):
                    description = re.sub(
                        r"^\d+\.\s*test case description:", "", line
                    ).strip()
                    current_section = "description"
                elif line.startswith("prerequisites:"):
                    pre_conditions.append(line.replace("prerequisites:", "").strip())
                    current_section = "prerequisites"
                elif line.startswith("steps:") or re.match(r"^[a-z]\.", line):
                    current_section = "steps"
                    if re.match(r"^[a-z]\.", line):
                        step_number += 1
                        steps.append(
                            (step_number, re.sub(r"^[a-z]\.", "", line).strip())
                        )
                elif line.startswith("expected results:"):
                    expected_results.append(
                        line.replace("expected results:", "").strip()
                    )
                    current_section = "expected_results"
                elif line.startswith("validations:"):
                    validations.append(line.replace("validations:", "").strip())
                    current_section = "validations"
                elif current_section == "prerequisites":
                    pre_conditions.append(line)
                elif current_section == "steps" and re.match(r"^[a-z]\.", line):
                    step_number += 1
                    steps.append((step_number, re.sub(r"^[a-z]\.", "", line).strip()))
                elif current_section == "expected_results":
                    expected_results.append(line)
                elif current_section == "validations":
                    validations.append(line)

            # Join multiline sections into a single string
            pre_conditions = "\n".join(pre_conditions).strip()
            expected_results = "\n".join(expected_results).strip()
            validations = "\n".join(validations).strip()

            # Add test case details to the list
            for step_number, step in steps:
                self.test_cases.append(
                    [
                        f"TC{str(i).zfill(2)}",  # Ensure TC format with leading zeros
                        description if step_number == 1 else "",
                        pre_conditions if step_number == 1 else "",
                        step_number,
                        step,
                        expected_results if step_number == 1 else "",
                        "",  # Actual Result
                        validations if step_number == 1 else "",
                        "",  # Status
                        "",  # Comments
                    ]
                )

    def generate_excel(self):
        self.parse_data()
        columns = [
            "Test Case ID",
            "Test Case description",
            "Pre-requisite Condition",
            "Step Number",
            "Steps Description",
            "Expected Result",
            "Actual Result",
            "Validations",
            "Status",
            "Comments",
        ]
        self.df = pd.DataFrame(self.test_cases, columns=columns)

        now = datetime.now()
        timestamp = now.strftime("%m_%d_%Y_%H%M")
        self.filename = f"test_cases_{timestamp}.xlsx"
        this_dir = os.path.dirname(__file__)
        self.directory = os.path.join(this_dir, "testcases")

        # Create the directory if it doesn't exist
        os.makedirs(self.directory, exist_ok=True)

        self.filepath = os.path.join(self.directory, self.filename)

        self.df.to_excel(self.filepath, index=False)
        return self.filename

    def send_table(self):
        return self.df


# # Example usage:
# data = """
# 1. Test case description: Verify if clicking the URL in the billing notification provides a full summary of charges and reflects new changes on the bill for existing O2 broadband and mobile customers.

# Prerequisites:
# - User has an active O2 broadband and mobile account.
# - User has received a billing notification with a URL to view the bill details.

# Steps:
# a. Click on the URL provided in the billing notification.

# Expected results:
# - The webpage displaying the bill details opens successfully.
# - The bill includes a full summary of charges for broadband and mobile services.
# - Any recent changes or updates to the bill are accurately reflected.

# Validations:
# - Verify that all charges for broadband and mobile services are listed.
# - Check that any recent changes or updates are visible on the bill.
# - Confirm that the bill is clear and understandable for the user.

# 2. Test case description: Verify if the bill summary includes a breakdown of charges for O2 broadband and mobile services.

# Prerequisites:
# - User is logged into their O2 account.
# - The billing period has ended, and a new bill is generated.

# Steps:
# a. Navigate to the billing section of the user account.
# b. Access the latest bill summary to view the breakdown of charges.

# Expected results:
# - The bill summary displays a breakdown of charges for both broadband and mobile services.
# - Charges are categorized clearly for easy understanding.

# Validations:
# - Check that charges for broadband and mobile services are segregated.
# - Verify that each charge is labeled correctly for easy identification.
# - Confirm that the total amount due matches the sum of individual charges.

# 3. Test case description: Verify that existing O2 broadband and mobile customers can view a full summary of charges after clicking the URL in the billing notification.
#    Prerequisites: User has received a billing notification from O2.

#    Steps:
#    a. Navigate to the billing notification received from O2 and click on the provided URL.
#    b. Check if the webpage loads successfully and displays a full summary of charges including all services and their costs.
#    c. Verify that the bill reflects any new changes or adjustments clearly.

#    Expected results: The user should be able to view a detailed summary of charges for both broadband and mobile services after clicking the URL. Any new changes or adjustments should be clearly visible on the bill.

#    Validations:
#    - Ensure that all services are listed with their respective charges.
#    - Confirm that any new charges or adjustments are accurately reflected.
#    - Check for any discrepancies between the billing notification and the online summary.

# 4. Test case description: Verify that existing O2 broadband and mobile customers can access their bill online and understand the charges.
#    Prerequisites: User has logged into their O2 account.

#    Steps:
#    a. Navigate to the billing section of the user account.
#    b. Check if the bill summary is displayed clearly with detailed information on charges for broadband and mobile services.
#    c. Review any recent changes or adjustments made to the bill.

#    Expected results: The user should be able to access their bill online and understand the charges for both broadband and mobile services. Any recent changes or adjustments should be visible and explained clearly.

#    Validations:
#    - Ensure that the bill summary is easy to understand and provides detailed information on charges.
#    - Verify that recent changes or adjustments are clearly communicated.
#    - Cross-check the online bill with any previous billing notifications for consistency.

# """

# generator = TableGenerator(data)
# file_path = generator.generate_excel()
# print(f"Test cases saved to {file_path}")
