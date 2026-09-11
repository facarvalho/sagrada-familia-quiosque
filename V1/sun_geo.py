"""
Geolocalização real do terreno (extraída de V1/cordenadas.kml, pontos
levantados no local) e cálculo de posição solar real, para uso nos renders
de "prova de sol".

--- Referência geográfica -------------------------------------------------
LAT / LON = centroide dos 10 pontos do KML (cantos do piso da piscina,
cantos da piscina e os pilares P1/P9 do quiosque). Terreno pequeno (<20 m),
a variação de posição do sol dentro dele é desprezível.

TZ_OFFSET = -3 (horário de Brasília, sem horário de verão desde 2019).

--- Alinhamento com o norte verdadeiro -------------------------------------
O eixo +Y do projeto (`projeto.py`, direção P1 -> P9, rotulada
informalmente de "norte" nos comentários/roof_frame) NÃO aponta para o
norte geográfico real. Comparando os pontos do KML:
  - eixo do piso da piscina (retângulo "canto pisco piscina 1-4"): 134,5°
  - eixo da piscina (retângulo "canto piscina 1-4"):                134,8°
  - P1->P9 (os próprios pilares do quiosque, medidos no KML):        133,7°
  - conferência independente por imagem de satélite (Google, medição
    de pixels do contorno da piscina):                               133,9°
Os 4 métodos convergem em ~134°. Usamos o valor de P1->P9 (133,7°) por ser
a correspondência direta entre coordenada real e coordenada do projeto.

ROTATION_OFFSET_DEG = bearing REAL (graus, sentido horário a partir do
norte verdadeiro) do eixo +Y do projeto. Ou seja:
    bearing_real = bearing_projeto + ROTATION_OFFSET_DEG   (mod 360)
onde bearing_projeto é medido do mesmo jeito (sentido horário) mas usando
+Y do projeto como referência "0°" (em vez do norte verdadeiro).
"""
import math

LAT = -21.353064729197495
LON = -45.9900583949398
TZ_OFFSET = -3  # America/Sao_Paulo (BRT), sem DST desde 2019

ROTATION_OFFSET_DEG = 133.7


def solar_position(year, month, day, hour, minute, lat=LAT, lon=LON, tz_offset=TZ_OFFSET):
    """Azimute (graus, 0=norte, sentido horário) e elevação (graus acima do
    horizonte) do sol, para hora LOCAL (padrão, sem DST). Algoritmo NOAA
    Solar Calculator simplificado (precisão ~0.01 graus, mais que
    suficiente para estudo de sombra)."""
    ut_hour = (hour - tz_offset) + minute / 60.0
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    jdn = day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    jd = jdn + (ut_hour - 12) / 24.0

    T = (jd - 2451545.0) / 36525.0
    L0 = (280.46646 + T * (36000.76983 + T * 0.0003032)) % 360
    M = 357.52911 + T * (35999.05029 - 0.0001537 * T)
    e = 0.016708634 - T * (0.000042037 + 0.0000001267 * T)
    Mrad = math.radians(M)
    C = (1.914602 - T * (0.004817 + 0.000014 * T)) * math.sin(Mrad) \
        + (0.019993 - 0.000101 * T) * math.sin(2 * Mrad) \
        + 0.000289 * math.sin(3 * Mrad)
    true_long = L0 + C
    omega = 125.04 - 1934.136 * T
    app_long = true_long - 0.00569 - 0.00478 * math.sin(math.radians(omega))

    eps0 = 23 + (26 + (21.448 - T * (46.815 + T * (0.00059 - T * 0.001813))) / 60) / 60
    eps = eps0 + 0.00256 * math.cos(math.radians(omega))

    decl = math.degrees(math.asin(math.sin(math.radians(eps)) * math.sin(math.radians(app_long))))

    y_ = math.tan(math.radians(eps / 2)) ** 2
    eq_time = 4 * math.degrees(
        y_ * math.sin(2 * math.radians(L0))
        - 2 * e * math.sin(Mrad)
        + 4 * e * y_ * math.sin(Mrad) * math.cos(2 * math.radians(L0))
        - 0.5 * y_ * y_ * math.sin(4 * math.radians(L0))
        - 1.25 * e * e * math.sin(2 * Mrad)
    )

    time_offset = eq_time + 4 * lon - 60 * tz_offset
    tst = hour * 60 + minute + time_offset
    hour_angle = (tst / 4.0) - 180.0
    if hour_angle < -180:
        hour_angle += 360
    if hour_angle > 180:
        hour_angle -= 360

    lat_r, decl_r, ha_r = math.radians(lat), math.radians(decl), math.radians(hour_angle)
    cos_zenith = math.sin(lat_r) * math.sin(decl_r) + math.cos(lat_r) * math.cos(decl_r) * math.cos(ha_r)
    cos_zenith = max(-1.0, min(1.0, cos_zenith))
    zenith = math.degrees(math.acos(cos_zenith))
    elevation = 90 - zenith

    zen_r = math.radians(zenith)
    denom = math.cos(lat_r) * math.sin(zen_r)
    if abs(denom) < 1e-6:
        azimuth = 180.0
    else:
        cos_az = (math.sin(lat_r) * math.cos(zen_r) - math.sin(decl_r)) / denom
        cos_az = max(-1.0, min(1.0, cos_az))
        az = math.degrees(math.acos(cos_az))
        azimuth = (az + 180) % 360 if hour_angle > 0 else (540 - az) % 360

    return azimuth, elevation


def azimuth_real_to_project(azimuth_real_deg):
    """Converte azimute real (graus, norte verdadeiro) para o azimute
    equivalente no referencial próprio do projeto (0° = +Y do projeto,
    sentido horário)."""
    return (azimuth_real_deg - ROTATION_OFFSET_DEG) % 360


def sun_direction_project_xyz(azimuth_real_deg, elevation_deg):
    """Vetor unitário (dx,dy,dz), no referencial (X,Y,Z) do projeto,
    apontando DO solo PARA o sol. Útil para mathutils Vector(...).to_track_quat."""
    az_proj = math.radians(azimuth_real_to_project(azimuth_real_deg))
    el = math.radians(elevation_deg)
    dx = math.sin(az_proj) * math.cos(el)
    dy = math.cos(az_proj) * math.cos(el)
    dz = math.sin(el)
    return (dx, dy, dz)


def true_north_vector_project_xy():
    """Vetor unitário (dx,dy) no plano XY do projeto apontando para o
    norte verdadeiro (para desenhar uma seta de referência na cena)."""
    az_proj = math.radians(azimuth_real_to_project(0.0))
    return (math.sin(az_proj), math.cos(az_proj))
