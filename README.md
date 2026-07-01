# KOSSDA 데이터분석 공모전: 20대 생활시간 분석

이 저장소는 KOSSDA 데이터분석 공모전 제출 준비를 위해 작성한 생활시간 분석 코드와 실행 안내를 정리한 프로젝트입니다.

분석 주제는 **청년의 하루에서 나타나는 사회적 연결 약화의 단서: 생활시간조사로 본 20대 생활패턴 변화**입니다. 1990년, 2010년, 2024년 20대의 생활시간 구성을 비교하고, 특히 `교제 및 참여활동`, `문화 및 여가활동`, `일+학습`, `이동` 시간의 변화를 탐색합니다.

## Repository Contents

- `kossda_youth_social_connection_analysis.py`: Google Colab 노트북에서 추출한 전체 분석 코드입니다.
- `requirements.txt`: 분석 실행에 필요한 주요 Python 패키지 목록입니다.
- `data/README.md`: 원자료 파일명과 배치 방법 안내입니다.
- `outputs/README.md`: 코드 실행 후 생성되는 결과물 안내입니다.

## Required Data

원자료는 저장소에 포함하지 않았습니다. 데이터 이용 조건과 재배포 가능 범위를 확인한 뒤, 실행 환경에 직접 준비해야 합니다.

분석 코드는 다음 파일명을 기준으로 작성되어 있습니다.

- `1990_data.sav`
- `2010_data.sav`
- `2024_data.csv`

Google Colab에서 실행할 경우 각 파일은 `/content/` 아래에 업로드되어야 합니다.

```text
/content/1990_data.sav
/content/2010_data.sav
/content/2024_data.csv
```

## Setup

Google Colab 실행을 권장합니다. Colab이 아닌 로컬 Jupyter 환경에서 실행하려면 데이터 경로와 Colab 전용 업로드 코드를 일부 수정해야 합니다.

기본 패키지는 다음 명령으로 설치할 수 있습니다.

```bash
pip install -r requirements.txt
```

Colab에서는 `pyreadstat`과 한글 폰트 설치가 필요할 수 있습니다. `.py` 파일에서는 파이썬 문법 오류를 피하기 위해 Colab 셸 명령을 주석 처리해 두었습니다.

```python
# !pip install pyreadstat
# !apt-get -qq install fonts-nanum
```

Colab 노트북 셀로 실행할 때는 위 명령을 별도 셀에서 실행하거나 주석을 해제해 사용하면 됩니다.

## Run Order

1. `1990_data.sav`, `2010_data.sav`, `2024_data.csv`를 Colab에 업로드합니다.
2. `kossda_youth_social_connection_analysis.py`의 셀 구분(`# %% Cell ...`) 순서대로 실행합니다.
3. 1990년과 2010년 SAV 파일을 읽고 20대 표본을 추출합니다.
4. 생활일지 변수를 15분 단위 주행동으로 재구성합니다.
5. 행동코드를 분석용 대분류로 변환합니다.
6. 2024년 집계 CSV를 같은 분류 체계에 맞춥니다.
7. 최종 비교표와 그래프를 생성합니다.

## Outputs

코드 실행 후 다음 결과물이 생성됩니다.

- `kossda_20s_timeuse_summary.csv`: 1990, 2010, 2024년 20대 평균 생활시간 요약표
- `kossda_1990_20s_person_day.csv`: 1990년 20대 개인-일자별 생활시간표
- `kossda_2010_20s_person_day.csv`: 2010년 20대 개인-일자별 생활시간표
- `fig1_하루구성_누적막대.png`
- `fig2_1990_2024_변화량.png`
- `fig3_핵심지표_변화.png`
- `fig4_여가대비교제비.png`

Colab 기준 그래프는 `/content/kossda_figures/`에 저장됩니다.

## Analysis Notes

- 1990년과 2010년 자료는 개인 단위 생활일지 원자료를 재분류해 계산합니다.
- 2024년 자료는 이미 집계된 CSV를 사용하므로 개인 단위 재계산은 하지 않습니다.
- `교제 및 참여활동` 감소를 곧바로 고립 증가로 단정하지 않고, 생활시간 구성 변화의 단서로 조심스럽게 해석합니다.
- 행동코드 대분류 기준은 분석 결과 해석에 영향을 주므로 발표자료에서 반드시 설명해야 합니다.
