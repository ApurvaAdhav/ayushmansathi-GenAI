# AyushmanSathi - Day 2
# Healthcare Rules Collection from HBP 2.2

SOURCE_URL = "https://nha.gov.in/img/resources/HBP-2.2-manual.pdf"

DOCUMENT_TITLE = "National Health Benefit Package 2.2 - User Guidelines"

# Healthcare Records
records = [

    # General Healthcare Rules

    {
        "id": 1,
        "rule_topic": "Amount",
        "rule_text": "Eligible PM-JAY beneficiary families receive health coverage of up to Rs. 5 lakh per family per year for secondary and tertiary care hospitalization.",
        "applies_to": "Eligible PM-JAY beneficiary families",
        "document_title": DOCUMENT_TITLE,
        "page_or_section": "Foreword, Page 1",
        "source_url": SOURCE_URL
    },
    {
        "id": 2,
        "rule_topic": "Eligibility",
        "rule_text": "Eligible families include SECC deprivation categories D1, D2, D3, D4, D5 and D7, automatically included categories, specified urban occupational groups and eligible existing RSBY beneficiary families.",
        "applies_to": "Eligible rural and urban families",
        "document_title": DOCUMENT_TITLE,
        "page_or_section": "Section 1.1, Page 5",
        "source_url": SOURCE_URL
    },
    {
        "id": 3,
        "rule_topic": "Beneficiary Identification",
        "rule_text": "Beneficiary families are identified using the SECC database, including eligible existing RSBY beneficiary families not appearing in the SECC database.",
        "applies_to": "PM-JAY beneficiary identification authorities",
        "document_title": DOCUMENT_TITLE,
        "page_or_section": "Section 1.1, Page 5",
        "source_url": SOURCE_URL
    },
    {
        "id": 4,
        "rule_topic": "Pre-authorisation",
        "rule_text": "Specified treatment packages require pre-authorisation from the insurance company or trust before treatment is provided.",
        "applies_to": "Empanelled hospitals and insurance companies or trusts",
        "document_title": DOCUMENT_TITLE,
        "page_or_section": "Section 4.2, Page 34",
        "source_url": SOURCE_URL
    },
    {
        "id": 5,
        "rule_topic": "Pre-authorisation",
        "rule_text": "Hospitals must upload the mandatory clinical documents and investigation reports required for the selected package when submitting a pre-authorisation request.",
        "applies_to": "Empanelled hospitals",
        "document_title": DOCUMENT_TITLE,
        "page_or_section": "Section 4.2, Pages 34-35",
        "source_url": SOURCE_URL
    },
    {
        "id": 6,
        "rule_topic": "Pre-authorisation",
        "rule_text": "In emergencies, hospitals can obtain a pre-authorisation code through the insurance company, trust or designated call centre and submit the required information through the transaction system.",
        "applies_to": "Empanelled hospitals and authorization teams",
        "document_title": DOCUMENT_TITLE,
        "page_or_section": "Section 4.2, Page 35",
        "source_url": SOURCE_URL
    },
    {
        "id": 7,
        "rule_topic": "Discharge Against Advice",
        "rule_text": "For surgical cases, if a patient leaves before surgery, payment is calculated according to the length of stay and bed category. If the patient leaves after surgery, 75% of the package rate is payable after audit.",
        "applies_to": "Empanelled hospitals handling LAMA/DAMA cases",
        "document_title": DOCUMENT_TITLE,
        "page_or_section": "Section 1.4.1, Page 9",
        "source_url": SOURCE_URL
    },
    {
        "id": 8,
        "rule_topic": "Death in Hospital",
        "rule_text": "If a patient dies before surgery, payment is calculated according to the length of stay and bed category. Death during surgery allows 75% of the booked package rate, while death after surgery allows 100% after medical audit.",
        "applies_to": "Empanelled hospitals handling patient death cases",
        "document_title": DOCUMENT_TITLE,
        "page_or_section": "Section 1.4.2, Pages 9-10",
        "source_url": SOURCE_URL
    },
    {
        "id": 9,
        "rule_topic": "Referral",
        "rule_text": "Patients should normally be referred to another empanelled hospital. Referral to a non-empanelled hospital is permitted only in exceptional circumstances with strong justification.",
        "applies_to": "Referring and receiving hospitals",
        "document_title": DOCUMENT_TITLE,
        "page_or_section": "Section 1.4.3, Page 10",
        "source_url": SOURCE_URL
    },
    {
        "id": 10,
        "rule_topic": "Unspecified Packages",
        "rule_text": "Unspecified packages can be used for eligible surgical treatments not included in the listed interventions. Compulsory pre-authorisation is required, and they cannot be used for medical management cases.",
        "applies_to": "Empanelled hospitals and PM-JAY beneficiaries",
        "document_title": DOCUMENT_TITLE,
        "page_or_section": "Section 1.5.1, Pages 12-13",
        "source_url": SOURCE_URL
    },

    # Five Annexure 1 Exclusions

    {
        "id": 11,
        "rule_topic": "Exclusion",
        "rule_text": "Conditions that do not require hospitalization and can be treated through outpatient care are excluded from PM-JAY coverage.",
        "applies_to": "Patients seeking outpatient treatment",
        "document_title": DOCUMENT_TITLE,
        "page_or_section": "Annexure 1, Page 54",
        "source_url": SOURCE_URL
    },
    {
        "id": 12,
        "rule_topic": "Exclusion",
        "rule_text": "Corrective, prosthetic and cosmetic dental procedures, cavity fillings, root canal treatment, periodontal disease treatment and dental implants are excluded. Exceptions apply to specified trauma, injury and tumour-related conditions requiring hospitalization for bone treatment.",
        "applies_to": "Patients seeking dental treatment",
        "document_title": DOCUMENT_TITLE,
        "page_or_section": "Annexure 1, Page 54",
        "source_url": SOURCE_URL
    },
    {
        "id": 13,
        "rule_topic": "Exclusion",
        "rule_text": "Assisted reproductive techniques and infertility-related procedures are excluded unless they are included in the National Health Benefit Package list.",
        "applies_to": "Patients seeking infertility-related treatment",
        "document_title": DOCUMENT_TITLE,
        "page_or_section": "Annexure 1, Page 54",
        "source_url": SOURCE_URL
    },
    {
        "id": 14,
        "rule_topic": "Exclusion",
        "rule_text": "Vaccination and immunization expenses are excluded under the PM-JAY policy.",
        "applies_to": "Patients seeking vaccination or immunization",
        "document_title": DOCUMENT_TITLE,
        "page_or_section": "Annexure 1, Page 54",
        "source_url": SOURCE_URL
    },
    {
        "id": 15,
        "rule_topic": "Exclusion",
        "rule_text": "Surgeries related to ageing face and body, laser tattoo removal, augmentation surgeries, fat grafting, neck lifts and aesthetic rhinoplasty are excluded as purely cosmetic procedures.",
        "applies_to": "Patients seeking purely cosmetic procedures",
        "document_title": DOCUMENT_TITLE,
        "page_or_section": "Annexure 1, Page 54",
        "source_url": SOURCE_URL
    },

    # Five FAQs from Section 5

    {
        "id": 16,
        "rule_topic": "FAQ",
        "rule_text": "The rationale for HBP 2.1 included adding unavailable procedures, incorporating state-specific packages and introducing new packages requested by SHAs, medical experts and stakeholders.",
        "applies_to": "PM-JAY hospitals and healthcare administrators",
        "document_title": DOCUMENT_TITLE,
        "page_or_section": "Section 5, FAQ 1, Page 45",
        "source_url": SOURCE_URL
    },
    {
        "id": 17,
        "rule_topic": "FAQ",
        "rule_text": "HBP 2.1 contained 918 packages divided into 1,669 procedures, including six additional procedures under the Organ and Tissue Transplant specialty.",
        "applies_to": "PM-JAY healthcare administrators",
        "document_title": DOCUMENT_TITLE,
        "page_or_section": "Section 5, FAQ 2, Page 45",
        "source_url": SOURCE_URL
    },
    {
        "id": 18,
        "rule_topic": "FAQ",
        "rule_text": "HBP 2.1 covered 25 specialties, including Organ and Tissue Transplant. All specialties from HBP 2.0 were retained.",
        "applies_to": "PM-JAY hospitals and healthcare administrators",
        "document_title": DOCUMENT_TITLE,
        "page_or_section": "Section 5, FAQ 3, Page 45",
        "source_url": SOURCE_URL
    },
    {
        "id": 19,
        "rule_topic": "FAQ",
        "rule_text": "The prices of procedures in HBP 2.1 remained the same as those in HBP 2.0.",
        "applies_to": "Empanelled hospitals and claims processing teams",
        "document_title": DOCUMENT_TITLE,
        "page_or_section": "Section 5, FAQ 4, Page 45",
        "source_url": SOURCE_URL
    },
    {
        "id": 20,
        "rule_topic": "FAQ",
        "rule_text": "The unspecified package category was retained in HBP 2.1 because some state-specific or uncommon conditions might not be included in the listed packages.",
        "applies_to": "PM-JAY beneficiaries and empanelled hospitals",
        "document_title": DOCUMENT_TITLE,
        "page_or_section": "Section 5, FAQ 5, Page 45",
        "source_url": SOURCE_URL
    }
]
