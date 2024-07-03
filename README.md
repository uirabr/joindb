# VERAZ DATABASE MERGE

## Overview

The Veraz Database Merge is a project of data analytics to help an educational institute called Veraz to merge and clean two databases: one from WhatsApp contacts and another from enrolled students. The primary goal is to ensure data consistency, correct formatting issues, and eliminate duplicates. The script performs various checks and adjustments, and outputs a single, cleaned database in CSV format.

The context of the databases is the following: (1) Whatsapp contacts registered for the events updates and (2) Enrolled contacts: students who have enrolled and paid for at least one course.

The purpose of this project is to identify WhatsApp contacts who are also enrolled students (flagging 'XX' in their names) and add any enrolled students who are missing from the WhatsApp database.

## Legal Warning

Important to note that the databases contain private information from clients of the company, and it must not be copied or sold by any individual or company. This data follows the LGPD law for Data Protection in Brazil.

## Requirements

•	Python 3.x

•	Required Python packages (notably, csv, re and io)

## Usage

1.	Ensure you have Python installed on your system.
2.	Place the WhatsApp and enrolled databases in the designated folders (files/Contatos Google WP.csv and files/Contatos Alunos Matriculados Original.csv).
3.	Run the script by executing the main() function.

## Phone formats
Most of the phone numbers are from Brazil, so there are some phone standards to identify whether some number is a Brazilian number, and then if it is a mobile or landline number. Using REGEX, this is the summary for a Brazilian phone number:

###	Regex = "^((?:55)?[1-9]{2})?(9)?([0-9]{8})$"

#### EXPLANATION OF REGEX

    55 = Country Code (DDI)

    11 to 99 = Regional Code (DDD)

    9 = Leading 9, that means the number is a mobile number

    8888-8888 = 8 last digits that are the core of the number; the first digit is important to characterize if it is a landline or mobile number


For a landline number, the leading 9 must not be present and the first digit of the last group must be between 2 and 5.

For a mobile number, the leading 9 is mandatory, even though Whatsapp does not enforce it on users, so for this code we consider that the number should have the leading 9 or the first digit of the last group should be between 6 and 9.

You may find further references for Brazilian telephones in those links:

#### Mobile Phones: https://pt.stackoverflow.com/questions/46672/como-fazer-uma-express%C3%A3o-regular-para-telefone-celular

#### Fix Phones: https://pt.stackoverflow.com/questions/14343/como-diferenciar-tipos-de-telefone


## Segmentation choice

The whatsapp database has some segmentations: based on the number of the "Transmission list" to students and based on either the student lives near São Paulo or far away (to determine it's interest in presencial courses).

The criteria we chosed is to consider a student who lives near São Paulo as any student from the State of São Paulo, or that has a cellphone with a DDD (regional code) of all the regions that are bounded by São Paulo DDD 11.

#### Reference for segmentation: http://www.geomapas.com.br/nossos-produtos/ref.-573-estado-de-sao-paulo-divisao-por-ddd-painel-120x90cm-ou-160x120cm-573.html


## Functionality

### Database Import

•	Reads WhatsApp and enrolled databases from CSV files into memory.

•	Filters contacts based on specified criteria.

### Database Cleaning

•	Applies corrections to both databases before the merge.

•	Checks and formats Brazilian phone numbers

•	Identifies and handles contacts with a plus sign in the number.

•	Identifies and handles contacts with empty numbers or names.

### Database Merging

•	Merges the enrolled database into the WhatsApp database.

•	Adjusts contact names based on specified rules.

•	Checks and handles duplicate contacts.

### Output

•	Outputs the final merged database to a CSV file.

•	Generates reports on found and new contacts.

•	Produces log files for various checks and adjustments.

## File Structure

•	files/: Contains input databases and change logs.

•	output0/ or output1/: Output folder based on the changes variable.

## Results

•	The final merged database is saved in output0/ or output1/ as "8. Final Database.csv".

•	Detailed reports and logs are saved for various checks and adjustments.

## Additional Notes

•	The script uses external CSV files (changes.csv) for specific corrections.

•	The script supports customization through global variables, allowing for easy adjustments.
.

## Conclusion

The Veraz Database Merge script provides a comprehensive solution for merging and cleaning WhatsApp and enrolled databases.

The Instituto Veraz used this project to merge and clean the databases, in order to make its biggest launch: an online courses platform.
