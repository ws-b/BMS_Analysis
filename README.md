# 🚗 EV Data Processing Pipeline

This project is a pipeline for efficiently processing and analyzing large-scale data collected from electric vehicles (EVs). Based on the data collected for each terminal, the power is calculated using physical formulas, and the data is divided into individual trips to facilitate storage and analysis.

## ✨ Key Features

- **Vehicle Selection**: Select a specific vehicle model or all vehicle models for processing.
- **Data Merging**: Integrates log and GPS data distributed by terminal.
- **Physics-based Power Calculation**: Calculates power consumption by applying the vehicle's physical parameters.
- **Trip Data Splitting**: Automatically splits and saves the entire driving data into individual trips based on stopping time.
- **Parallel Processing**: Reduces processing time by processing data in parallel using multiple CPU cores.
- **Result Report Generation**: Automatically generates an Excel report summarizing the status of the processed trip data.

## ⚙️ Requirements

- Python 3.x
- `tqdm` library

You can install the library with the following command:
```bash
pip install tqdm
```

## 🚀 How to Use

1. Clone or download the project.
2. In the `Source/config.py` file, check and, if necessary, modify the path where the data is stored and other settings.
3. In the `Source/vehicle_config.py` file, define the vehicle models and terminal ID list to be processed.
4. Run `main.py` in the terminal.

```bash
python main.py
```

5. Follow the on-screen instructions to select the task to execute.
    - **1: Run the entire pipeline**: Executes data loading, power calculation, and trip splitting in parallel.
    - **2: Generate a trip creation result report**: Creates an Excel file containing statistical information of the processed trips.
    - **0: Exit the program**

## 📂 Project Structure

```
BMS_Analysis/
│
├── .git/
├── Source/                 # Source code directory
│   ├── __pycache__/
│   ├── config.py           # Main configuration file for paths, DB info, etc.
│   ├── data_loader.py      # Data loading and merging module
│   ├── physics_power.py    # Physics-based power calculation module
│   ├── report_car.py
│   ├── report_generator.py # Result report generation module
│   ├── trip_parser.py      # Trip data splitting and saving module
│   ├── vehicle_config.py   # Vehicle model and terminal ID configuration file
│   ├── vehicle_data.example.json
│   └── vehicle_data.json
│
├── .gitignore
├── main.py                 # Main program execution file
└── README.md               # Project description file
```

---

# 🚗 EV 데이터 처리 파이프라인

본 프로젝트는 전기차(EV)에서 수집된 대용량 데이터를 효율적으로 처리하고 분석하기 위한 파이프라인입니다. 
단말기별로 수집된 데이터를 바탕으로 물리식을 이용해 전력을 계산하고, 개별 주행(Trip) 단위로 데이터를 분할하여 저장 및 분석을 용이하게 합니다.

## ✨ 주요 기능

- **차종 선택**: 분석을 원하는 특정 차종 또는 전체 차종을 선택하여 처리 가능
- **데이터 병합**: 단말기별로 분산된 로그 및 GPS 데이터를 통합
- **물리식 기반 전력 계산**: 차량의 물리적 파라미터를 적용하여 전력 소모량 계산
- **주행(Trip) 데이터 분할**: 정차 시간을 기준으로 전체 주행 데이터를 개별 Trip으로 자동 분할 및 저장
- **병렬 처리**: 다수의 CPU 코어를 활용한 데이터 병렬 처리로 작업 시간 단축
- **결과 리포트 생성**: 처리된 Trip 데이터 현황을 요약한 Excel 리포트 자동 생성

## ⚙️ 요구 사항

- Python 3.x
- `tqdm` 라이브러리

라이브러리는 다음 명령어로 설치할 수 있습니다.
```bash
pip install tqdm
```

## 🚀 사용 방법

1. 프로젝트를 클론하거나 다운로드합니다.
2. `Source/config.py` 파일에서 데이터가 저장된 경로 및 기타 설정을 확인하고 필요시 수정합니다.
3. `Source/vehicle_config.py` 파일에 처리할 차량 모델과 단말기 ID 목록을 정의합니다.
4. 터미널에서 `main.py`를 실행합니다.

```bash
python main.py
```

5. 화면의 안내에 따라 실행할 작업을 선택합니다.
    - **1: 전체 파이프라인 실행**: 데이터 로딩, 전력 계산, Trip 분할을 병렬로 실행합니다.
    - **2: Trip 생성 결과 리포트 생성**: 처리된 Trip들의 통계 정보를 담은 Excel 파일을 생성합니다.
    - **0: 프로그램 종료**

## 📂 프로젝트 구조

```
BMS_Analysis/
│
├── .git/
├── Source/                 # 소스 코드 디렉토리
│   ├── __pycache__/
│   ├── config.py           # 경로, DB 정보 등 주요 설정 파일
│   ├── data_loader.py      # 데이터 로딩 및 병합 모듈
│   ├── physics_power.py    # 물리식 기반 전력 계산 모듈
│   ├── report_car.py
│   ├── report_generator.py # 결과 리포트 생성 모듈
│   ├── trip_parser.py      # 주행(Trip) 데이터 분할 및 저장 모듈
│   ├── vehicle_config.py   # 차량 모델 및 단말기 ID 설정 파일
│   ├── vehicle_data.example.json
│   └── vehicle_data.json
│
├── .gitignore
├── main.py                 # 프로그램 메인 실행 파일
└── README.md               # 프로젝트 설명 파일
```
