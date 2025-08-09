import logging
import glob
import pandas as pd
from tqdm import tqdm
from pathlib import Path

def _read_csv_with_fallback_encodings(file_path):
    """ CSV 파싱 에러에 더 안정적으로 대응하도록 수정된 함수."""
    try:
        # 1. 가장 빠른 C 엔진으로 시도
        return pd.read_csv(file_path, encoding='utf-8', low_memory=False)
    except UnicodeDecodeError:
        try:
            # 2. 인코딩 문제일 경우, 다른 인코딩으로 재시도
            logging.warning(f"UTF-8 디코딩 실패. ISO-8859-1로 재시도: {file_path}")
            return pd.read_csv(file_path, encoding='iso-8859-1', low_memory=False)
        except Exception as e:
            logging.error(f"파일 읽기 실패(ISO-8859-1): {file_path}. 오류: {e}")
            return None
    except pd.errors.ParserError as e:
        # 3. ✅ C 엔진 파싱 에러 발생 시, 느리지만 안정적인 파이썬 엔진으로 재시도
        logging.warning(f"C 파서 오류 발생. Python 엔진으로 재시도: {file_path}. 오류: {e}")
        try:
            return pd.read_csv(file_path, encoding='utf-8', engine='python')
        except Exception as py_e:
            logging.error(f"Python 엔진으로도 파일 읽기 최종 실패: {file_path}. 오류: {py_e}")
            return None
    except Exception as e:
        logging.error(f"예상치 못한 오류로 파일 읽기 실패: {file_path}. 오류: {e}")
        return None

def _find_device_files(device_id, config):
    base_path = config.PATHS["raw_bms_data"]
    pattern = f'**/*{device_id}*.csv'
    return list(base_path.glob(pattern))

def _preprocess_dataframe(df, device_id):
    """
    여러 시간 형식을 처리하도록 개선된 데이터프레임 전처리 함수
    """
    df.columns = df.columns.str.strip()
    required_cols = ['time', 'emobility_spd', 'pack_volt', 'pack_current']

    missing_cols = [col for col in required_cols if col not in df.columns]
    if missing_cols:
        logging.warning(f"[{device_id}] 필수 열이 누락되어 처리할 수 없습니다. (누락된 열: {missing_cols})")
        return None

    df['device_id'] = device_id

    possible_formats = ['%y-%m-%d %H:%M:%S', '%Y-%m-%d %H:%M:%S']
    
    temp_time_col = df['time'].copy()

    success = False
    for fmt in possible_formats:
        try:
            df['time'] = pd.to_datetime(temp_time_col, format=fmt, errors='raise')
            success = True
            break
        except ValueError:

            continue

    if not success:
        logging.warning(f"[{device_id}] 정의된 시간 형식으로 변환 실패. 'coerce' 옵션으로 마지막 시도.")
        df['time'] = pd.to_datetime(df['time'], errors='coerce')
    
    df = df.dropna(subset=['time'])
    if df.empty:
        logging.warning(f"[{device_id}] 유효한 시간 데이터를 찾을 수 없어 처리할 수 없습니다.")
        return None

    df = df.drop_duplicates(subset=['time', 'device_id']).sort_values('time').reset_index(drop=True)
    df['time_diff'] = df['time'].diff().dt.total_seconds()
    df['speed'] = df['emobility_spd'] * 0.27778
    df['acceleration'] = df['speed'].diff() / df['time_diff']
    df['acceleration'] = df['acceleration'].fillna(0)
    df['Power_data'] = df['pack_volt'] * df['pack_current']
    
    return df


def _merge_gps_data(bms_df, device_id, config):
    gps_path = config.PATHS["raw_gps_data"]
    pattern = str(gps_path / device_id / '**' / '*.csv')
    gps_files = glob.glob(pattern, recursive=True)
        
    if not gps_files:
        logging.warning(f"[{device_id}] 병합할 GPS 파일이 없습니다. BMS 데이터만 사용합니다.")
        if 'altitude' not in bms_df.columns:
             bms_df['altitude'] = pd.NA
        return bms_df.assign(lat=pd.NA, lng=pd.NA)

    gps_dfs = [_read_csv_with_fallback_encodings(f) for f in gps_files]
    full_gps_df = pd.concat([df for df in gps_dfs if df is not None], ignore_index=True)

    if full_gps_df.empty or 'time' not in full_gps_df.columns:
        logging.warning(f"[{device_id}] GPS 데이터가 비어있거나 유효하지 않습니다.")
        if 'altitude' not in bms_df.columns:
             bms_df['altitude'] = pd.NA
        return bms_df.assign(lat=pd.NA, lng=pd.NA)

    full_gps_df['time'] = pd.to_datetime(full_gps_df['time'], errors='coerce', format='%Y-%m-%d %H:%M:%S')
    full_gps_df = full_gps_df.dropna(subset=['time']).sort_values('time')

    cols_to_merge = ['time']
    if 'altitude' in full_gps_df.columns: cols_to_merge.append('altitude')
    if 'lat' in full_gps_df.columns: cols_to_merge.append('lat')
    if 'lng' in full_gps_df.columns: cols_to_merge.append('lng')

    merged_df = pd.merge_asof(
        bms_df.sort_values('time'), full_gps_df[cols_to_merge],
        on='time', direction='nearest', tolerance=pd.Timedelta(seconds=2),
        suffixes=('', '_gps')
    )

    if 'altitude_gps' in merged_df.columns:
        merged_df['altitude'] = merged_df['altitude_gps'].combine_first(merged_df.get('altitude'))
    if 'lat_gps' in merged_df.columns: merged_df['lat'] = merged_df['lat_gps']
    if 'lng_gps' in merged_df.columns: merged_df['lng'] = merged_df['lng_gps']

    if 'altitude' in merged_df.columns:
        merged_df['altitude'] = merged_df['altitude'].interpolate(method='linear').bfill().ffill()
    
    merged_df = merged_df.drop(columns=[col for col in merged_df.columns if '_gps' in str(col)], errors='ignore')
    return merged_df


def load_and_merge_device_data(device_id, config):
    """특정 단말기의 모든 데이터를 로드, 병합, 전처리하고 GPS 데이터를 결합합니다."""
    data_files = _find_device_files(device_id, config)
    if not data_files:
        return None

    df_list = [_read_csv_with_fallback_encodings(f) for f in tqdm(data_files, desc=f"[{device_id}] 파일 로딩", leave=False)]
    
    df_full = pd.concat([df for df in df_list if df is not None], ignore_index=True)
    
    if df_full.empty:
        logging.warning(f"[{device_id}] 파일들은 존재하지만, 읽을 수 있는 데이터가 없습니다.")
        return None

    df_processed = _preprocess_dataframe(df_full, device_id)

    if df_processed is None:
        return None

    has_altitude_file = any('altitude' in Path(f).name for f in data_files)
    
    if has_altitude_file:
        return _merge_gps_data(df_processed, device_id, config)
    else:
        return df_processed