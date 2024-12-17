from docx import Document

def fill_clearance_template(template_path, output_path, data):
    """
    Fill the Barangay Clearance Word template with provided data.
    :param template_path: Path to the Word template.
    :param output_path: Path to save the filled document.
    :param data: Dictionary containing placeholders and their values.
    """
    try:
        # Load the Word template
        doc = Document(template_path)

        # Replace placeholders in all paragraphs
        for paragraph in doc.paragraphs:
            replace_placeholders_in_paragraph(paragraph, data)

        # Replace placeholders in table cells
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for paragraph in cell.paragraphs:
                        replace_placeholders_in_paragraph(paragraph, data)

        # Save the filled document
        doc.save(output_path)
    except Exception as e:
        print(f"Error filling template: {e}")
        raise

def replace_placeholders_in_paragraph(paragraph, data):
    """
    Replace placeholders in a paragraph, accounting for multi-run issues.
    :param paragraph: Paragraph object.
    :param data: Dictionary containing placeholders and their values.
    """
    # Combine all runs into a single string
    full_text = ''.join(run.text for run in paragraph.runs)

    # Replace placeholders in the combined text
    for placeholder, value in data.items():
        if placeholder in full_text:
            full_text = full_text.replace(placeholder, value)

    # Clear existing runs
    for run in paragraph.runs:
        run.text = ""

    # Write the updated text back into the paragraph
    if paragraph.runs:
        paragraph.runs[0].text = full_text
