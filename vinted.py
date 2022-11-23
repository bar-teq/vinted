# from encodings.utf_8_sig import decode
# from fileinput import filename
# from hashlib import new
import imaplib
import os
import email
from dotenv import load_dotenv
from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import time
import mailparser
from email import policy
from time import strftime

pdf_count = 0
printed_count = 0
now = strftime("%d %b %Y %H:%M:%S")

load_dotenv()
LOGIN = os.getenv('LOGIN')
PASSWORD = os.getenv('PASSWORD')
IMAP_URL = os.getenv('IMAP_URL')
attachment_dir = os.getenv('ATTACHMENT_DIR')
labels_dir = os.getenv('LABEL_DIR')
mail = imaplib.IMAP4_SSL(IMAP_URL)
mail.login(LOGIN, PASSWORD)
mail.select('ETYKIETY')

typ, data = mail.search(None, 'UNSEEN')
mail_ids = data[0]

id_list = mail_ids.split()

for f in os.listdir(attachment_dir):
    try:
        os.remove(os.path.join(attachment_dir, f))
    except PermissionError:
        pass

for f in os.listdir(labels_dir):
    try:
        os.remove(os.path.join(labels_dir, f))
    except PermissionError:
        pass

if len(id_list) == 0:
    print('Brak nowych etykiet')
    with open('d:/python/vinted/log/log.txt', 'a') as file:
        file.write(f"{now} Brak nowych etykiet \n")
    input("Naciśnij ENTER żeby wyjść")
    quit()


def get_attachments(msg):
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue
        fileName = part.get_filename()

        if bool(fileName):
            filePath = os.path.join(attachment_dir, fileName)
            with open(filePath, 'wb') as f:
                f.write(part.get_payload(decode=True))
    return fileName


def change_pdf(title, fileName):
    filePath_lab = os.path.join(labels_dir, fileName)
    filePath_att = os.path.join(attachment_dir, fileName)
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter, encrypt=None)
    can.setFont("Times-Roman", 12)
    can.drawString(0, 100, f"{title}")
    can.save()

    packet.seek(0)
    new_pdf = PdfFileReader(packet)
    with open(filePath_att, "rb") as f:
        existing_pdf = PdfFileReader(f)
        output = PdfFileWriter()
        page = existing_pdf.getPage(0)
        page.mergePage(new_pdf.getPage(0))
        output.addPage(page)
        outputStream = open(filePath_lab, "wb")
        output.write(outputStream)
        outputStream.close()


for i in range(int(id_list[-1]), int(id_list[0])-1, -1):
    _, data = mail.fetch(str(i), '(RFC822)')
    raw = email.message_from_bytes(data[0][1])
    mailp = mailparser.parse_from_bytes(data[0][1])
    get_attachments(raw)
    for response_part in data:
        if isinstance(response_part, tuple):
            msg = email.message_from_bytes(
                response_part[1], policy=policy.default)
            temat = mailp.subject
            fileName = get_attachments(msg)
            change_pdf(f"{temat}", f"{fileName}")
            pdf_count += 1
            with open('d:/python/vinted/log/log.txt', 'a') as file:
                file.write(f"{now} {temat} \n")
    mail.store(str(i), '+X-GM-LABELS', '\\Trash')
    mail.expunge()

print()
print("-------------------------------------------")
print(f"Nowych Etykiet: {pdf_count}")
print("-------------------------------------------")
print()

dir_old = 'D:/python/vinted/tt'
dir = 'D:/python/vinted/zrobione'
printed = 0
for f in os.listdir(labels_dir):
    filePath = os.path.join(labels_dir, f)
    filePath2 = os.path.join(attachment_dir, f)
    os.startfile(filePath, "print")
    time.sleep(4)
    # os.remove(os.path.join(attachment_dir, f))
    # os.remove(os.path.join(labels_dir, f))
    printed += 1

print()
print("-------------------------------------------")
print(f"Wydykowano Etykiet: {printed}")
print("-------------------------------------------")
print()
with open('d:/python/vinted/log/log.txt', 'a') as file:
    file.write(
        f"----------------------\n{now} Wydrukowano {printed} \n----------------------\n")
input("Naciśnij ENTER żeby wyjść")
