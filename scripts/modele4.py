import matplotlib.pyplot as plt
import numpy as np
import sys
import os

def generate_temp_data(t, lat, lon, amplitude=10, base=15):
    variation = np.sin(np.radians(lat)) * np.cos(np.radians(lon))
    return base + amplitude * variation * np.sin(2 * np.pi * t / max(t))

def save_graph(lat, lon, zoom, output_dir="static", model_name="modele4"):
    os.makedirs(output_dir, exist_ok=True)
    if zoom == "annuel":
        t = np.linspace(0, 365, 365)
    elif zoom == "mensuel":
        t = np.linspace(0, 30, 30)
    elif zoom == "journalier":
        t = np.linspace(0, 1, 24)
    else:
        raise ValueError("Zoom inconnu")

    y = generate_temp_data(t, float(lat), float(lon))
    fig, ax = plt.subplots()
    ax.plot(t, y)
    ax.set_title(f"modele4 - Température - Zoom {{zoom}}")
    ax.set_xlabel("Temps (jours)" if zoom != "journalier" else "Heure")
    ax.set_ylabel("Température (°C)")
    fig.savefig(os.path.join(output_dir, f"modele4_graph_{{zoom}}.png"))
    plt.close(fig)

if __name__ == "__main__":
    lat = float(sys.argv[1])
    lon = float(sys.argv[2])
    zoom = sys.argv[3]
    save_graph(lat, lon, zoom)