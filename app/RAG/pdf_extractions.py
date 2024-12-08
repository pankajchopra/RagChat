import re

from PyPDF2 import PdfReader

from utils import clean_text


class PdfExtractions:

    def __init__(self):
        pass

    def extract_text_by_sections(self, pdf_path):
        reader = PdfReader(pdf_path)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text()
        # Define common resume section headers
        section_headers = [
            "Job Objective", "Special Skills", "Professional Summary", "Work Experience", "Professional Experience",
            "Education", "Volunteer Experience", "Awards", "Publications", "Languages", "Interests", "hobbies", "Mentorship",
            "Technical Skills", "Skills", "Certifications", "Projects", "References", "Memberships"
        ]

        # Split text by sections using regex
        section_pattern = "|".join([re.escape(header) for header in section_headers])
        sections = re.split(f"({section_pattern})", full_text)

        structured_resume = {}
        current_section = None
        for part in sections:
            if part.strip() in section_headers:
                current_section = part.strip()
                structured_resume[current_section] = ""
            elif current_section:
                """Removes non-printable characters from a string."""
                clean_part = clean_text(part)
                structured_resume[current_section] += clean_part

        contact_info = self.extract_contact_info(full_text)
        structured_resume["Name"] = contact_info["Name"]
        structured_resume["Email"] = contact_info["Email"]
        structured_resume["Phone"] = contact_info["Phone"]
        structured_resume["Address"] = contact_info["Address"]  # Add address
        experience = structured_resume.get("Professional Experience") or structured_resume.get("Work Experience")
        if experience:
            structured_resume["Professional Experience"] = self.parse_professional_experience(experience)

        return structured_resume

    def parse_professional_experience(self, professional_experience_text):
        """Split the 'Professional Experience' section into individual job experiences."""
        # Assuming each job starts with a date or company name, adapt the regex as needed
        job_pattern = re.compile(r"(?:[\w+,\s])+\s+\d{4}\sto(?:\sCurrent|\s\w+\s?\s\d{4})+", re.IGNORECASE)
        matches = list(job_pattern.finditer(professional_experience_text))

        jobs = []
        for i, match in enumerate(matches):
            start_idx = match.start()
            end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(professional_experience_text)
            jobs.append(professional_experience_text[start_idx:end_idx].strip())

        return jobs

    # Function to extract text from PDF
    def extract_text_from_pdf(self, pdf_path):
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        """Removes non-printable characters from a string."""
        text = clean_text(text)
        return text

    def extract_contact_info(self, resume_text):
        # Split text into lines
        lines = resume_text.split("\n")

        # Initialize storage
        name = ""
        address_lines = []
        email = ""
        phone = ""

        # Define regex patterns
        email_pattern = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
        phone_pattern = r"(\+?[\d\-\(\)\.]{7,})"  # Matches various phone formats
        zip_pattern = r"\b\d{5}(?:-\d{4})?\b"  # US ZIP codes

        # Extract name (usually first non-empty line)
        for line in lines:
            if line.strip():
                name = line.strip()
                break

        # Extract contact details (email, phone, address)
        for line in lines:
            if not email:
                email_match = re.search(email_pattern, line)
                if email_match:
                    email = email_match.group(0)

            if not phone:
                phone_match = re.search(phone_pattern, line)
                if phone_match:
                    phone = phone_match.group(0)

            if re.search(zip_pattern, line):  # If line contains ZIP code, assume it's part of the address
                address_lines.append(line.strip())

        # Combine address lines
        address = " ".join(address_lines) if address_lines else ""

        # Return extracted information
        return {
            "Name": name,
            "Email": email,
            "Phone": phone,
            "Address": address
        }
