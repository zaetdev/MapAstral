from typing import List


def generate_pdf(lines: List[str], filename: str) -> None:
    objects = []
    objects.append("<< /Type /Catalog /Pages 2 0 R >>")
    objects.append("<< /Type /Pages /Kids [3 0 R] /Count 1 >>")
    objects.append(
        "<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>"
    )
    content_lines = ["BT", "/F1 12 Tf"]
    y = 800
    for line in lines:
        safe = line.replace("(", r"\(").replace(")", r"\)")
        content_lines.append(f"50 {y} Td ({safe}) Tj")
        y -= 14
    content_lines.append("ET")
    content_stream = "\n".join(content_lines)
    objects.append(f"<< /Length {len(content_stream)} >>\nstream\n{content_stream}\nendstream")
    objects.append("<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")

    xref = [0]
    pdf = "%PDF-1.4\n"
    for i, obj in enumerate(objects, start=1):
        xref.append(len(pdf.encode('latin-1')))
        pdf += f"{i} 0 obj\n{obj}\nendobj\n"
    xref_pos = len(pdf.encode('latin-1'))
    pdf += f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n"
    for offset in xref[1:]:
        pdf += f"{offset:010} 00000 n \n"
    pdf += f"trailer << /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref_pos}\n%%EOF"
    with open(filename, "wb") as f:
        f.write(pdf.encode('latin-1'))
