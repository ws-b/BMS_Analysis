from pathlib import Path
import platform

# --- 1. 경로 설정 (Path Configuration) ---
# OS에 따라 기본 경로 설정
BASE_DIR = Path(r"D:\SamsungSTF") if platform.system() == "Windows" else Path("/mnt/d/SamsungSTF")

# 데이터 경로
PATHS = {
    "raw_bms_data": BASE_DIR / "Data/GSmbiz/BMS_Data",
    "raw_gps_data": BASE_DIR / "Data/GSmbiz/gps_altitude",
    "output_trip": BASE_DIR / "Processed_Data/Trips",
    "output_report": BASE_DIR / "Processed_Data",
}

# --- 2. 물리 모델 상수 (Physics Constants) ---
GRAVITY = 9.81  # 중력 가속도 (m/s^2)
INERTIA_FACTOR = 0.05  # 회전 관성 계수

# --- 3. Trip 검증 조건 (Trip Validation Thresholds) ---
TRIP_THRESHOLDS = {
    "min_duration_seconds": 300,     # 최소 Trip 시간 (5분)
    "min_distance_meters": 3000,     # 최소 Trip 거리 (3km)
    "min_energy_kwh": 1.0,           # 최소 소모 에너지 (kWh)
    "max_abs_acceleration": 9.0,     # 최대 허용 가속도 (m/s^2)
    "max_idle_duration_seconds": 300 # 최대 연속 정지 시간 (5분)
}

# --- 4. 차량별 물리 파라미터 (Vehicle Parameters) ---
# 단위: mass(kg), load(kg), Ca(N), Cb(N/(m/s)), Cc(N/(m/s)^2), power(W), eff(0-1)
VEHICLE_PARAMS = {
    'NiroEV': {
        "mass": 1928, "load": 100, "eff": 0.9, "re_brake": 1,
        "Ca": 32.717 * 4.44822, "Cb": -0.19110 * 4.44822 * 2.237, "Cc": 0.023073 * 4.44822 * (2.237**2),
        "aux_power": 250, "hvac_power": 350, "idle_power": 0, "hvac_eff": 0.81
    },
    'Ioniq5': {
        "mass": 2268, "load": 100, "eff": 0.9, "re_brake": 1,
        "Ca": 34.342 * 4.44822, "Cb": 0.21928 * 4.44822 * 2.237, "Cc": 0.022718 * 4.44822 * (2.237**2),
        "aux_power": 250, "hvac_power": 350, "idle_power": 0, "hvac_eff": 0.81
    },
    'Ioniq6': {
        "mass": 2041.168, "load": 100, "eff": 0.9, "re_brake": 1,
        "Ca": 23.958 * 4.44822, "Cb": 0.15007 * 4.44822 * 2.237, "Cc": 0.015929 * 4.44822 * (2.237**2),
        "aux_power": 250, "hvac_power": 350, "idle_power": 0, "hvac_eff": 0.81
    },
    'KonaEV': {
        "mass": 1814, "load": 100, "eff": 0.9, "re_brake": 1,
        "Ca": 24.859 * 4.44822, "Cb": -0.20036 * 4.44822 * 2.237, "Cc": 0.023656 * 4.44822 * (2.237**2),
        "aux_power": 250, "hvac_power": 350, "idle_power": 0, "hvac_eff": 0.81
    },
    'EV6': {
        "mass": 2154.564, "load": 100, "eff": 0.9, "re_brake": 1,
        "Ca": 36.158 * 4.44822, "Cb": 0.29099 * 4.44822 * 2.237, "Cc": 0.019825 * 4.44822 * (2.237**2),
        "aux_power": 250, "hvac_power": 350, "idle_power": 0, "hvac_eff": 0.81
    },
    'GV60': {
        "mass": 2154.564, "load": 100, "eff": 0.9, "re_brake": 1,
        "Ca": 23.290 * 4.44822, "Cb": 0.23788 * 4.44822 * 2.237, "Cc": 0.019822 * 4.44822 * (2.237**2),
        "aux_power": 250, "hvac_power": 350, "idle_power": 0, "hvac_eff": 0.81
    },
}