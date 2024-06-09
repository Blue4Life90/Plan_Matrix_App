import tkinter as tk
from tkinter import messagebox
import os
import unittest
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from PyPDF2 import PdfReader

"""Here's a breakdown of the code:

The generate_schedule_pdf function takes the schedule data and filename as 
input and generates a PDF file with the schedule data formatted as a table. 
It uses the reportlab library to create the PDF canvas, define the table 
data and styles, and draw the table on the PDF.

The export_to_pdf function is associated with the "Export to PDF" button. 
When the button is clicked, it prepares the schedule data, calls the 
generate_schedule_pdf function to generate the PDF file, and displays a 
message box to inform the user that the export was successful.
The TestPDFExport class contains two test methods:

test_generate_schedule_pdf tests the generate_schedule_pdf function by 
invoking it with the schedule data and filename, and then asserting that 
the PDF file is successfully generated and exists.

test_pdf_content tests the content of the generated PDF file. It generates
the PDF using the generate_schedule_pdf function, reads the content of the 
PDF file, and asserts that the expected data (such as column headers and 
employee names) is present in the PDF content.

The setUp method in the test case sets up the necessary data for testing, 
including the schedule data and the filename for the generated PDF.
The tearDown method in the test case cleans up the generated PDF file 
after each test to avoid leaving unnecessary files.

The if __name__ == '__main__': block at the end of the code runs the test 
case when the script is executed.

To use this code in your application, you can integrate the 
generate_schedule_pdf function and the export_to_pdf function into your 
existing codebase. Make sure to have the reportlab library installed and 
imported correctly.

When you run the script, it will execute the test case, and the test 
results will be displayed in the console. If all the tests pass, it 
indicates that the PDF export functionality is working as expected.

You can customize the schedule data, table styles, and layout in the 
generate_schedule_pdf function to match your specific requirements.

Remember to handle any exceptions or errors that may occur during the PDF 
generation process and provide appropriate error messages or feedback to 
the user if needed.

Overall, the code you provided should work as a starting point for adding 
the PDF export functionality to your application.
"""

def generate_schedule_pdf(schedule_data, filename):
    # Create a new PDF document
    pdf_file = SimpleDocTemplate(filename)

    # Define the table data and styles
    table_data = [['Date', 'Shift', 'Employee']]
    table_data.extend(schedule_data)
    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])

    # Create the table and apply the styles
    table = Table(table_data)
    table.setStyle(table_style)

    # Build the PDF document
    elements = [table]
    pdf_file.build(elements)

def export_to_pdf():
    schedule_data = [
        ['2023-06-01', 'Morning', 'John Doe'],
        ['2023-06-01', 'Afternoon', 'Jane Smith'],
        ['2023-06-02', 'Morning', 'Mike Johnson'],
        # Add more schedule data as needed
    ]
    filename = 'schedule.pdf'
    generate_schedule_pdf(schedule_data, filename)
    messagebox.showinfo('Export', 'Schedule exported to PDF successfully!')

# Create the main window
root = tk.Tk()
root.title("Schedule App")

# Create the export button
export_button = tk.Button(root, text='Export to PDF', command=export_to_pdf)
export_button.pack()

class TestPDFExport(unittest.TestCase):
    def setUp(self):
        self.schedule_data = [
            ['2023-06-01', 'Morning', 'John Doe'],
            ['2023-06-01', 'Afternoon', 'Jane Smith'],
            ['2023-06-02', 'Morning', 'Mike Johnson'],
        ]
        self.filename = 'test_schedule.pdf'

    def tearDown(self):
        # Clean up the generated PDF file after each test
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def test_generate_schedule_pdf(self):
        # Test the generate_schedule_pdf function
        generate_schedule_pdf(self.schedule_data, self.filename)
        self.assertTrue(os.path.exists(self.filename))

    def test_pdf_content(self):
        # Test the content of the generated PDF
        generate_schedule_pdf(self.schedule_data, self.filename)

        # Read the PDF content using PyPDF2
        with open(self.filename, 'rb') as file:
            reader = PdfReader(file)
            page = reader.pages[0]
            pdf_text = page.extract_text()

            self.assertIn('Date', pdf_text)
            self.assertIn('Shift', pdf_text)
            self.assertIn('Employee', pdf_text)
            self.assertIn('John Doe', pdf_text)
            self.assertIn('Jane Smith', pdf_text)
            self.assertIn('Mike Johnson', pdf_text)

if __name__ == '__main__':
    # Run the test case
    unittest.main(exit=False)

    # Run the main event loop
    root.mainloop()