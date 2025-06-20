
from flask import Flask, request, send_file
import matplotlib.pyplot as plt
import numpy as np
import io, datetime, math, calendar, requests

app = Flask(__name__)

# ---------------------------------------------------------------------------
# Aide : fonction commune pour composer la figure à 3 vues
# ---------------------------------------------------------------------------
def compose_triple_view(dates, T, title_prefix):
    jour_heures  = 24
    mois_heures  = 31 * 24  # janvier
    fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharey=True)

    # Annuel
    axes[0].plot(dates, T)
    axes[0].set_title(f"{title_prefix} — vue annuelle")
    axes[0].grid(True)

    # Mensuel (janvier)
    axes[1].plot(dates[:mois_heures], T[:mois_heures], color='tab:orange')
    axes[1].set_title("Température – janvier")
    axes[1].grid(True)

    # Journalier (1er janvier)
    axes[2].plot(dates[:jour_heures], T[:jour_heures], color='tab:green')
    axes[2].set_title("Température – 1ᵉʳ janvier")
    axes[2].set_xlabel("Heure")
    axes[2].grid(True)

    fig.tight_layout(rect=[0, 0.03, 1, 0.97])
    return fig

# ---------------------------------------------------------------------------
# Modèle 1 (déjà simple)
# ---------------------------------------------------------------------------
def run_model1(zoomX):
    fig, ax = plt.subplots()
    time_max = 24 / zoomX
    x = np.linspace(0, time_max, 1000)
    y = 273 + 10 * np.exp(-x / 5)
    ax.plot(x, y)
    ax.set_title("Modèle 1 : Refroidissement simple")
    ax.set_xlabel("Temps (h)")
    ax.set_ylabel("T (K)")
    ax.grid(True)
    return fig

# ---------------------------------------------------------------------------
# Modèle 2  (issu de Code_complet_V2.py)
# ---------------------------------------------------------------------------
def puissance_recue_par_heure_m2(latitude_deg, longitude_deg, jour_de_l_annee):
    S0 = 1361
    lat = np.radians(latitude_deg)
    lon = np.radians(longitude_deg)
    inclinaison = np.radians(23.5)
    declinaison = np.arcsin(np.sin(inclinaison) * np.sin(2 * np.pi * (jour_de_l_annee - 81) / 365))
    soleil = np.array([np.cos(declinaison), 0, np.sin(declinaison)])
    soleil /= np.linalg.norm(soleil)
    puissances = []
    for h in range(24):
        angle = np.radians(15 * (h - 12))
        x = np.cos(lat) * np.cos(lon + angle)
        y = np.cos(lat) * np.sin(lon + angle)
        z = np.sin(lat)
        normale = np.array([x, y, z])
        puissances.append(max(0, S0 * np.dot(normale, soleil)))
    return puissances

def chaque_jour_m2(lat, lon):
    return [puissance_recue_par_heure_m2(lat, lon, j) for j in range(1, 366)]

def annee_m2(P_tout):
    return [val for jour in P_tout for val in jour]

def temp_m2(P_recu):
    c = 2.25e5
    alpha = 0
    S = 1
    T0 = 273
    sigma = 5.67e-8
    dt = 3600
    A = 0.3
    T = [T0]
    for i in range(len(P_recu)-1):
        flux_sortant = 0.5 * sigma * S * (T[i])**4
        T.append(T[i] + dt * ((1-A)*P_recu[i]*S - flux_sortant) / c)
    return T

def run_model2(lat, lon):
    P = annee_m2(chaque_jour_m2(lat, lon))
    T = temp_m2(P)
    dates = [datetime.datetime(2024,1,1)+datetime.timedelta(hours=i) for i in range(len(T))]
    return compose_triple_view(dates, T, "Modèle 2")

# ---------------------------------------------------------------------------
# Modèle 3  (issu de code_c_constant.py)
# ---------------------------------------------------------------------------
sigma_m3 = 5.67e-8
c_m3     = 551500
h_m3     = 10
S0_m3    = 1361
T_air_m3 = 283
T0_m3    = 283
dt_m3    = 3600
data_albedo_m3 = {
    "Amérique du Nord": 0.25, "Amérique du Sud": 0.18, "Europe de l'Ouest": 0.25,
    "Europe de l'Est": 0.3, "Asie du Sud": 0.15, "Asie de l'Est": 0.2,
    "Asie du Sud-Est": 0.2, "Afrique du Nord": 0.25,"Afrique Sub-saharienne":0.18,
    "Afrique_Désertique":0.45,"Océans":0.12,"Pole Nord":0.75,"Pole Sud":0.8
}
def determiner_partie_terre(lat, lon):
    if lat >= 60: return "Pole Nord"
    if lat <= -60: return "Pole Sud"
    if 30 <= lat <= 60 and -130 <= lon <= -60: return "Amérique du Nord"
    if -60 <= lat <= 15 and -90 <= lon <= -30: return "Amérique du Sud"
    if 45 <= lat <= 70 and -10 <= lon <= 40:
        return "Europe de l'Ouest" if lon <= 20 else "Europe de l'Est"
    if -10 <= lat <= 40 and 60 <= lon <= 160:
        if 5 <= lat <= 30 and 60 <= lon <= 120: return "Asie du Sud"
        if 30 <= lat <= 50 and 100 <= lon <= 140: return "Asie de l'Est"
        return "Asie du Sud-Est"
    if 15 <= lat <= 30 and -20 <= lon <= 40: return "Afrique_Désertique"
    if -35 <= lat <= 15 and -20 <= lon <= 50:
        return "Afrique du Nord" if lat > 0 else "Afrique Sub-saharienne"
    return "Océans"

def albedo_m3(lat, lon):
    return data_albedo_m3[determiner_partie_terre(lat, lon)]

def puissance_recue_par_heure_m3(latitude_deg, longitude_deg, jour):
    lat = np.radians(latitude_deg)
    lon = np.radians(longitude_deg)
    inclinaison = np.radians(23.5)
    declinaison = np.arcsin(np.sin(inclinaison) * np.sin(2*np.pi*(jour-81)/365))
    soleil = np.array([np.cos(declinaison),0,np.sin(declinaison)])
    soleil /= np.linalg.norm(soleil)
    puissances=[]
    for h in range(24):
        angle = np.radians(15*(h-12))
        x=np.cos(lat)*np.cos(lon+angle)
        y=np.cos(lat)*np.sin(lon+angle)
        z=np.sin(lat)
        normale=np.array([x,y,z])
        puissances.append(max(0,S0_m3*np.dot(normale,soleil)))
    return puissances

def run_model3(lat, lon):
    P = [val for jour in range(1,366) for val in puissance_recue_par_heure_m3(lat,lon,jour)]
    A = albedo_m3(lat, lon)
    T = [T0_m3]
    for i in range(len(P)):
        flux_in = (1-A)*P[i]
        flux_out = 0.5*sigma_m3*T[i]**4 + h_m3*(T[i]-T_air_m3)
        T.append(T[i] + dt_m3*(flux_in - flux_out)/c_m3)
    T = T[1:]
    dates = [datetime.datetime(2024,1,1)+datetime.timedelta(hours=i) for i in range(len(T))]
    return compose_triple_view(dates, T, "Modèle 3")

# ---------------------------------------------------------------------------
# Modèle 4  (issu de modele 4 version api nasa.py)
# ---------------------------------------------------------------------------
def coefficient_convection_m4(v):
    rho=1.2; mu=1.8e-5; L=1.0; Pr=0.71; lambda_air=0.026
    Re = rho*v*L/mu
    if Re<5e5: C,m,n = 0.664,0.5,1/3
    else: C,m,n = 0.037,0.8,1/3
    Nu = C*Re**m*Pr**n
    return Nu*lambda_air/L

def get_daily_wind_speed_m4(lat, lon):
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {"parameters":"WS2M","community":"AG","longitude":lon,"latitude":lat,
              "start":"20240101","end":"20241231","format":"JSON"}
    try:
        data = requests.get(url, params=params, timeout=5).json()
        arr  = data["properties"]["parameter"]["WS2M"]
        return [arr[d] for d in sorted(arr)]
    except Exception:
        return [2.5]*365

def get_mean_albedo_m4(lat, lon):
    url = "https://power.larc.nasa.gov/api/temporal/daily/point"
    params = {"parameters":"ALLSKY_SFC_SW_DWN,ALLSKY_SFC_SW_UP","community":"AG",
              "longitude":lon,"latitude":lat,"start":"20240101","end":"20241231","format":"JSON"}
    try:
        data=requests.get(url,params=params,timeout=5).json()
        down=data['properties']['parameter']['ALLSKY_SFC_SW_DWN']
        up=data['properties']['parameter']['ALLSKY_SFC_SW_UP']
        vals=[up[d]/down[d] for d in down if down[d]>0 and up[d] is not None]
        return sum(vals)/len(vals) if vals else 0.3
    except Exception:
        return 0.3

def puissance_recue_par_heure_m4(lat, lon, jour):
    S0=1361
    lat=np.radians(lat); lon=np.radians(lon)
    inclinaison=np.radians(23.5)
    declinaison=np.arcsin(np.sin(inclinaison)*np.sin(2*np.pi*(jour-81)/365))
    soleil=np.array([np.cos(declinaison),0,np.sin(declinaison)]); soleil/=np.linalg.norm(soleil)
    puissances=[]
    for h in range(24):
        angle=np.radians(15*(h-12))
        x=np.cos(lat)*np.cos(lon+angle); y=np.cos(lat)*np.sin(lon+angle); z=np.sin(lat)
        puissances.append(max(0,S0*np.dot(np.array([x,y,z]),soleil)))
    return puissances

def run_model4(lat, lon):
    P = [val for jour in range(1,366) for val in puissance_recue_par_heure_m4(lat,lon,jour)]
    wind = get_daily_wind_speed_m4(lat, lon)
    A = get_mean_albedo_m4(lat, lon)
    c=2.25e5; S=1; T0=283; sigma=5.67e-8; dt=3600; alpha=0.77; T_air=283
    T=[T0]
    for i in range(len(P)):
        jour=i//24
        v=wind[jour]; h=coefficient_convection_m4(v)
        flux_in=(1-A)*0.8*P[i]*S
        flux_rad=(1-alpha/2)*sigma*S*T[i]**4
        flux_conv=h*S*(T[i]-T_air)
        T.append(T[i]+dt*(flux_in-flux_rad-flux_conv)/c)
    T=T[1:]
    dates=[datetime.datetime(2024,1,1)+datetime.timedelta(hours=i) for i in range(len(T))]
    return compose_triple_view(dates,T,"Modèle 4")

# ---------------------------------------------------------------------------
# Modèle 5  (import fonction temp du module fourni)
# ---------------------------------------------------------------------------
try:
    from modele_5_cmv2 import temp as temp_m5
except ImportError:
    temp_m5 = None

def run_model5(lat, lon):
    if temp_m5 is None:
        fig,ax=plt.subplots(); ax.text(0.5,0.5,"modele_5_cmv2 introuvable",ha='center',va='center'); ax.axis('off'); return fig
    T=temp_m5(lat,lon)
    if len(T)==24*365+1: T=T[1:]
    dates=[datetime.datetime(2024,1,1)+datetime.timedelta(hours=i) for i in range(len(T))]
    return compose_triple_view(dates,T,"Modèle 5")

# ---------------------------------------------------------------------------
# API route
# ---------------------------------------------------------------------------
@app.route("/run")
def run():
    model=int(request.args.get("model",1))
    zoomX=float(request.args.get("zoomX",1.0))
    lat=float(request.args.get("lat",48.85))
    lon=float(request.args.get("lon",2.35))
    if model==1:
        fig=run_model1(zoomX)
    elif model==2:
        fig=run_model2(lat,lon)
    elif model==3:
        fig=run_model3(lat,lon)
    elif model==4:
        fig=run_model4(lat,lon)
    elif model==5:
        fig=run_model5(lat,lon)
    else:
        return "Modèle inconnu",400
    buf=io.BytesIO()
    fig.savefig(buf,format='png')
    buf.seek(0)
    plt.close(fig)
    return send_file(buf,mimetype='image/png')

if __name__=="__main__":
    app.run(host="0.0.0.0",port=10000)
