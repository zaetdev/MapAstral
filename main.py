import argparse
from map_astral.chart import compute_chart
from map_astral.pdf import generate_pdf


def main():
    parser = argparse.ArgumentParser(description="Gerador de mapa astral simples")
    parser.add_argument("name", help="Nome do cliente")
    parser.add_argument("date", help="Data no formato YYYY-MM-DD")
    parser.add_argument("time", help="Hora no formato HH:MM:SS")
    parser.add_argument("latitude", type=float, help="Latitude em graus")
    parser.add_argument("longitude", type=float, help="Longitude em graus")
    parser.add_argument("--output", default="mapa.pdf", help="Arquivo PDF de saída")
    args = parser.parse_args()

    year, month, day = map(int, args.date.split("-"))
    hour, minute, second = map(int, args.time.split(":"))
    chart = compute_chart(year, month, day, hour, minute, second, args.latitude, args.longitude)
    lines = [f"Mapa astral de {args.name}", ""]
    for body, (lon, sign) in chart.items():
        lines.append(f"{body.title()}: {sign} {lon:.2f}°")
    generate_pdf(lines, args.output)
    print(f"Mapa gerado em {args.output}")


if __name__ == "__main__":
    main()
