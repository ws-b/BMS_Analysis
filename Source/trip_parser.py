import pandas as pd
import numpy as np
import logging
import os

def _check_trip_conditions(trip_df, config):
    """
    Trip이 유효한지 검증하는 함수.
    config 파일의 TRIP_THRESHOLDS를 사용하여 조건을 확인합니다.
    """
    thresholds = config.TRIP_THRESHOLDS
    
    # 'chrg_cable_conn' 열이 존재하고, 그 값이 1(충전 중)인 데이터가 하나라도 있으면 유효하지 않은 Trip으로 판단
    if 'chrg_cable_conn' in trip_df.columns and (trip_df['chrg_cable_conn'] == 1).any():
        return False

    # 1. 최소 운행 시간 검증
    duration_seconds = (trip_df['time'].iloc[-1] - trip_df['time'].iloc[0]).total_seconds()
    if duration_seconds < thresholds["min_duration_seconds"]:
        return False

    # 2. 최소 주행 거리 검증
    time_diff = trip_df['time'].diff().dt.total_seconds().fillna(0)
    distance_meters = (trip_df['speed'] * time_diff).sum()
    if distance_meters < thresholds["min_distance_meters"]:
        return False
        
    # 3. 최소 소모 에너지 검증
    total_energy_kwh = (trip_df['Power_data'] * time_diff).sum() / 3600 / 1000
    if total_energy_kwh < thresholds["min_energy_kwh"]:
        return False
        
    # 4. 최대 허용 가속도 검증
    if (trip_df['acceleration'].abs() > thresholds["max_abs_acceleration"]).any():
        return False
        
    # 5. 최대 연속 정지 시간 검증
    is_stopped = trip_df['speed'] < 0.1
    stopped_time = 0
    # iloc을 사용하여 time_diff에 안전하게 접근
    time_diff_vals = time_diff.to_numpy()
    for i, stopped in enumerate(is_stopped):
        if stopped:
            stopped_time += time_diff_vals[i]
            if stopped_time >= thresholds["max_idle_duration_seconds"]:
                return False
        else:
            stopped_time = 0

    return True


def parse_and_save_trips(df, car_model, device_id, config):
    """
    전체 데이터프레임을 받아 Trip으로 분할하고,
    유효한 Trip을 차종별 폴더에 지정된 파일명으로 저장합니다.
    """
    if df.empty:
        return

    # 1. 시간 간격이 600초(10분) 이상 벌어질 때
    time_gaps = df['time'].diff().dt.total_seconds() > 600
    
    # 2. 충전 케이블 상태가 변경될 때 (0->1 또는 1->0)
    charge_status_changes = df['chrg_cable_conn'].diff().ne(0)
    
    # 두 조건을 만족하는 모든 지점의 인덱스를 찾음
    cut_indices = df.index[time_gaps | charge_status_changes].tolist()
    trip_boundaries = sorted(list(set([0] + cut_indices + [len(df)])))

    trip_counter = 1
    for i in range(len(trip_boundaries) - 1):
        start_idx = trip_boundaries[i]
        end_idx = trip_boundaries[i+1]
        
        current_trip = df.iloc[start_idx:end_idx].copy().reset_index(drop=True)

        if current_trip.empty:
            continue
            
        # Trip의 첫 번째 데이터 포인트의 충전 상태를 확인
        if current_trip['chrg_cable_conn'].iloc[0] == 1:
            continue
        
        if _check_trip_conditions(current_trip, config):
            year_month = current_trip['time'].iloc[0].strftime('%Y-%m')
            
            output_folder_for_car = config.PATHS["output_trip"] / car_model
            output_folder_for_car.mkdir(parents=True, exist_ok=True)

            columns_to_save = [
                'time', 'speed', 'acceleration', 
                'ext_temp', 'int_temp',
                'soc', 'soh', 
                'pack_volt', 'pack_current', 
                'Power_data', 'Power_phys'
            ]

            file_prefix = "Trip_"

            if 'altitude' in current_trip.columns and current_trip['altitude'].notna().any():
                file_prefix = "Trip_altitude_"
                columns_to_save = [
                'time', 'speed', 'acceleration', 
                'ext_temp', 'int_temp',
                'soc', 'soh', 'altitude',
                'pack_volt', 'pack_current', 
                'Power_data', 'Power_phys'
                ]
                
            file_name = f"{file_prefix}{device_id}_{year_month}_trip_{trip_counter}.csv"

            output_path = output_folder_for_car / file_name
            
            final_columns = [col for col in columns_to_save if col in current_trip.columns]
            
            current_trip_to_save = current_trip[final_columns]
            current_trip_to_save.to_csv(output_path, index=False, encoding='utf-8-sig')

            logging.info(f"✅ Trip 저장 성공: {output_path}")
            
            trip_counter += 1