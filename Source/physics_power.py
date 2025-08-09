import pandas as pd
import numpy as np
from Source import config

def add_physics_power(df, params):
    """데이터프레임에 물리식 기반 전력(Power_phys)을 계산하여 추가합니다."""
    v = df['speed'].to_numpy()
    a = df['acceleration'].to_numpy()
    ext_temp = df['ext_temp'].to_numpy()
    
    # 항력, 구름저항 등
    A = params["Ca"] * v / params["eff"]
    B = params["Cb"] * v**2 / params["eff"]
    C = params["Cc"] * v**3 / params["eff"]

    # 가속/감속 저항
    exp_term = np.exp(0.0411 / np.maximum(np.abs(a), 0.001))
    total_mass = params["mass"] + params["load"]
    D_positive = ((1 + config.INERTIA_FACTOR) * total_mass * a * v) / params["eff"]
    D_negative = (((1 + config.INERTIA_FACTOR) * total_mass * a * v) / exp_term) * params["eff"]
    D = np.where(a >= 0, D_positive, np.where(params["re_brake"] == 1, D_negative, 0))

    # 공조 및 보조 전력
    target_temp = 22
    E_hvac = np.abs(target_temp - ext_temp) * params["hvac_power"] * params["hvac_eff"]
    E = np.where(v <= 0.5, params["aux_power"] + params["idle_power"] + E_hvac, params["aux_power"] + E_hvac)
    
    # 경사 저항
    # if 'altitude' in df.columns and df['altitude'].notna().any():
    #     altitude_diff = df['altitude'].diff().fillna(0).to_numpy()
    #     time_diff = df['time_diff'].replace(0, 1).to_numpy()
    #     distance_diff = v * time_diff
    #     with np.errstate(divide='ignore', invalid='ignore'):
    #         slope = np.nan_to_num(np.arctan2(altitude_diff, distance_diff))
    #     F = total_mass * config.GRAVITY * np.sin(slope) * v / params["eff"]
    # else:
    #     F = 0
    
    # df['Power_phys'] = A + B + C + D + E + F
    df['Power_phys'] = A + B + C + D + E
    return df