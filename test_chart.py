import sys
import pathlib
sys.path.append(str(pathlib.Path(__file__).resolve().parents[1]))

from map_astral.chart import compute_chart
from map_astral.pdf import generate_pdf


def test_sun_sign():
    chart = compute_chart(2000, 1, 1, 12, 0, 0, 0, 0)
    sun_sign = chart["sun"][1]
    assert sun_sign == "Capricórnio"


def test_pdf_generation(tmp_path):
    file_path = tmp_path / "out.pdf"
    generate_pdf(["linha"], str(file_path))
    assert file_path.exists()
    with open(file_path, "rb") as f:
        header = f.read(4)
    assert header == b"%PDF"
