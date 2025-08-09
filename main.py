import logging
import multiprocessing
import os
from tqdm import tqdm
from Source import config, data_loader, physics_power, trip_parser, report_generator
from Source.vehicle_config import vehicle_dict

# 로깅 기본 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(processName)s - %(levelname)s - %(message)s')

def select_vehicles():
    """사용자로부터 처리할 차종을 선택받습니다."""
    print("처리할 차종을 선택하세요 (여러 개 선택 시 쉼표(,)로 구분).")
    car_options = {i + 1: car for i, car in enumerate(vehicle_dict.keys())}
    for i, car in car_options.items():
        print(f"{i}: {car}")
    print("0: 전체 선택")
    
    while True:
        try:
            choice_str = input("번호 선택: ")
            choices = [int(c.strip()) for c in choice_str.split(',')]
            
            if 0 in choices:
                return list(vehicle_dict.keys())

            selected_cars = [car_options[c] for c in choices if c in car_options]
            if selected_cars:
                return selected_cars
            else:
                logging.warning("유효한 번호를 입력하세요.")
        except (ValueError, KeyError):
            logging.error("잘못된 입력입니다. 숫자를 쉼표로 구분하여 입력해주세요.")

def process_device(args):
    """
    단일 단말기에 대한 전체 데이터 처리 파이프라인.
    멀티프로세싱의 각 워커(worker) 프로세스가 이 함수를 실행합니다.
    """
    car_model, device_id = args  # 인자 언패킹
    try:
        # 1. 데이터 로딩 (단말기 단위)
        # tqdm 진행바와의 출력이 겹치지 않도록 로깅 메시지는 간소화할 수 있습니다.
        # logging.info(f"--- [{car_model} - {device_id}] 파이프라인 시작 ---")
        df = data_loader.load_and_merge_device_data(device_id, config)
        if df is None or df.empty:
            logging.warning(f"[{device_id}] 처리할 데이터가 없어 건너뜁니다.")
            return f"SKIPPED: {device_id} (No data)"

        # 2. 물리식 전력 계산
        params = config.VEHICLE_PARAMS.get(car_model)
        if not params:
            logging.warning(f"[{car_model}] 차량 파라미터가 없어 물리식 계산을 건너뜁니다.")
            df_power = df
        else:
            df_power = physics_power.add_physics_power(df, params)

        # 3. Trip 분할 및 저장
        trip_parser.parse_and_save_trips(df_power, car_model, device_id, config)
        
        return f"SUCCESS: {device_id}"

    except Exception as e:
        # 에러가 발생해도 다른 프로세스에 영향을 주지 않고 계속 진행됩니다.
        logging.error(f"❌ [{car_model} - {device_id}] 처리 중 오류 발생: {e}", exc_info=False)
        return f"FAILED: {device_id} ({e})"


def run_pipeline(selected_cars):
    """선택된 차량에 대해 단말기 단위로 전체 데이터 처리 파이프라인을 병렬 실행합니다."""
    logging.info(f"선택된 차종: {', '.join(selected_cars)}")

    devices_to_process = []
    for car in selected_cars:
        devices_to_process.extend([(car, dev_id) for dev_id in vehicle_dict.get(car, [])])
    
    if not devices_to_process:
        logging.warning("처리할 단말기가 없습니다.")
        return

    # 사용할 CPU 코어 수 설정 
    num_processes = max(1, os.cpu_count() - 2)
    logging.info(f"총 {len(devices_to_process)}개의 단말기를 {num_processes}개의 프로세스로 병렬 처리합니다.")

    # with 문을 사용하여 Pool 객체를 안전하게 관리합니다.
    with multiprocessing.Pool(processes=num_processes) as pool:
        # imap_unordered: 작업을 분배하고 완료되는 순서대로 결과를 반환 (효율적)
        # tqdm: 진행 상황을 시각적으로 보여주는 라이브러리
        results = list(tqdm(pool.imap_unordered(process_device, devices_to_process), total=len(devices_to_process), desc="단말기 처리 중"))

    logging.info("모든 병렬 처리가 완료되었습니다.")
    # 처리 결과 요약
    success_count = sum(1 for r in results if r.startswith("SUCCESS"))
    skipped_count = sum(1 for r in results if r.startswith("SKIPPED"))
    failed_count = sum(1 for r in results if r.startswith("FAILED"))
    logging.info(f"처리 결과: 성공 {success_count}건, 건너뜀 {skipped_count}건, 실패 {failed_count}건")


def main_menu():
    """메인 메뉴를 표시하고 사용자 입력을 처리합니다."""
    while True:
        print("\n" + "="*50)
        print("⚡️ EV 데이터 처리 파이프라인 (v2.1 - Multiprocessing) ⚡️")
        print("="*50)
        print("1: 전체 파이프라인 실행 (병렬 처리)")
        print("2: Trip 생성 결과 리포트 생성 (Excel)")
        print("0: 프로그램 종료")
        print("="*50)
        
        choice = input("실행할 작업 번호를 입력하세요: ")

        if choice == '1':
            selected = select_vehicles()
            if selected:
                # Trip 저장 폴더 미리 생성
                for car_name in selected:
                    (config.PATHS["output_trip"] / car_name).mkdir(parents=True, exist_ok=True)
                run_pipeline(selected)
        elif choice == '2':
            logging.info("Trip 생성 결과 리포트를 생성합니다...")
            report_generator.generate_trip_report(config)
        elif choice == '0':
            logging.info("프로그램을 종료합니다.")
            break
        else:
            logging.warning("잘못된 번호입니다. 다시 입력해주세요.")

if __name__ == "__main__":
    multiprocessing.freeze_support() 
    main_menu()