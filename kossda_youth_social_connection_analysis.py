# Extracted from Google Colab notebook: 청년의 하루에서 나타나는 사회적 연결 약화의 단서: 생활시간조사로 본 20대 생활패턴 변화
# Source file ID: 1wsY0UaKiYSiXkczEw7qnUd21g9r9BTOe

# %% Cell 1
# ============================================================
# 코드묶음 0. 패키지 설치 및 불러오기
# ------------------------------------------------------------
# 역할:
# - SAV 파일을 읽기 위해 pyreadstat을 설치한다.
# - pandas, numpy는 데이터 정리용이다.
# - re는 변수명(v1, v2, ...)을 찾을 때 사용한다.
# - matplotlib은 나중에 그래프를 그릴 때 사용한다.
# ============================================================

# !pip install pyreadstat

import pandas as pd
import numpy as np
import pyreadstat
import re
import matplotlib.pyplot as plt

# %% Cell 2
from google.colab import files

# 1990, 2010 sav data, 2024 csv data 선택
for _ in range(2):
    uploaded = files.upload()

# %% Cell 3
# ============================================================
# 코드묶음 1. 파일 경로 지정
# ------------------------------------------------------------
# 역할:
# - Colab에 업로드한 파일 이름을 변수로 저장한다.
# - 이후 코드에서 파일명을 반복해서 쓰지 않도록 한다.
#
# 주의:
# - Colab 왼쪽 파일창에 실제 파일명이 다르면 아래 경로를 수정해야 한다.
# - 예: "/content/1990_data.sav"
# ============================================================

path_1990 = "/content/1990_data.sav"
path_2010 = "/content/2010_data.sav"
path_2024 = "/content/2024_data.csv"

# %% Cell 4
# ============================================================
# 코드묶음 2. 1990·2010 SAV 파일 읽기
# ------------------------------------------------------------
# 역할:
# - SPSS 원자료(.sav)를 pandas DataFrame으로 불러온다.
# - meta1990, meta2010에는 변수 라벨, 값 라벨 같은 코드북 정보가 들어간다.
#
# 핵심:
# - encoding="cp949"를 넣어야 한글 라벨이 깨지지 않는다.
# - apply_value_formats=False는 값을 한글 라벨로 바꾸지 않고 숫자 코드로 유지한다.
#   예: 성별을 "남성"으로 바꾸지 않고 1, 2로 유지
#   이유: 행동코드를 숫자로 재분류해야 하기 때문이다.
# ============================================================

df1990, meta1990 = pyreadstat.read_sav(
    path_1990,
    encoding="cp949",
    apply_value_formats=False
)

df2010, meta2010 = pyreadstat.read_sav(
    path_2010,
    encoding="cp949",
    apply_value_formats=False
)

print("1990 데이터 크기:", df1990.shape)
print("2010 데이터 크기:", df2010.shape)

display(df1990.head())
display(df2010.head())

# %% Cell 5
# ============================================================
# 코드묶음 3. 변수 라벨 확인
# ------------------------------------------------------------
# 역할:
# - 각 변수명이 무슨 의미인지 확인한다.
# - 예: age = 응답자 연령, job = 응답자 직업, v1 = 1일 주행동
#
# 왜 필요한가?
# - 지금 분석에서 가장 중요한 것은 "주행동 변수"를 정확히 찾는 것이다.
# - 변수명을 추측하면 안 되고, 라벨을 보고 확인해야 한다.
# ============================================================

var_info_1990 = pd.DataFrame({
    "변수명": meta1990.column_names,
    "변수라벨": meta1990.column_labels
})

var_info_2010 = pd.DataFrame({
    "변수명": meta2010.column_names,
    "변수라벨": meta2010.column_labels
})

print("1990 변수 정보")
display(var_info_1990.head(20))

print("2010 변수 정보")
display(var_info_2010.head(20))

# %% Cell 6
# ============================================================
# 코드묶음 4. 20대 표본만 추출하기
# ------------------------------------------------------------
# 역할:
# - 이번 연구 대상은 20대 청년이다.
# - age가 20 이상 29 이하인 사람만 남긴다.
#
# 왜 필요한가?
# - 전체 국민이 아니라 "20대 청년의 하루"를 분석해야 하기 때문이다.
# ============================================================

df1990_20 = df1990[(df1990["age"] >= 20) & (df1990["age"] <= 29)].copy()
df2010_20 = df2010[(df2010["age"] >= 20) & (df2010["age"] <= 29)].copy()

print("1990년 20대 표본 수:", df1990_20.shape[0])
print("2010년 20대 표본 수:", df2010_20.shape[0])

# %% Cell 7
# ============================================================
# 코드묶음 5. 생활일지 변수 묶기
# ------------------------------------------------------------
# 역할:
# - v1, v2, v3 ... 형태의 생활일지 변수만 뽑는다.
# - 3일치 생활일지를 1일, 2일, 3일로 나눈다.
# - 각 날짜 안에서 주행동, 부행동, 재택여부를 분리한다.
#
# 매우 중요:
# - 1990·2010 자료에는 v34가 없다.
# - 따라서 v1, v4, v7처럼 숫자 규칙만 믿으면 위험하다.
# - 실제 컬럼 순서를 기준으로 3개씩 끊어야 한다.
#
# 구조:
# - 하루는 15분 단위 96칸이다.
# - 한 칸마다 주행동, 부행동, 재택여부 3개 변수가 있다.
# - 하루 변수 수 = 96칸 × 3개 = 288개
# - 3일 변수 수 = 288개 × 3일 = 864개
# ============================================================

def get_diary_vars(meta):
    # v1, v2, v3 ... 처럼 생긴 변수만 가져온다.
    vcols = [c for c in meta.column_names if re.fullmatch(r"v\d+", c)]

    print("생활일지 변수 개수:", len(vcols))

    # 생활일지 변수는 총 864개여야 정상이다.
    if len(vcols) != 864:
        print("경고: 생활일지 변수 개수가 예상과 다릅니다. 변수 구조를 다시 확인해야 합니다.")

    # 컬럼 순서 기준으로 1일, 2일, 3일을 나눈다.
    day1 = vcols[0:288]
    day2 = vcols[288:576]
    day3 = vcols[576:864]

    diary = {}

    for day_num, day_cols in zip([1, 2, 3], [day1, day2, day3]):
        diary[day_num] = {
            "main": day_cols[0::3],  # 주행동
            "sub": day_cols[1::3],   # 부행동
            "home": day_cols[2::3],  # 재택여부
        }

    return diary

diary1990 = get_diary_vars(meta1990)
diary2010 = get_diary_vars(meta2010)

print("1990년 1일 주행동 변수 수:", len(diary1990[1]["main"]))
print("2010년 1일 주행동 변수 수:", len(diary2010[1]["main"]))

print("1990년 1일 주행동 앞 5개:", diary1990[1]["main"][:5])
print("1990년 1일 주행동 뒤 5개:", diary1990[1]["main"][-5:])

# %% Cell 8
# ============================================================
# 코드묶음 6. 행동코드 → 분석용 대분류 변환 규칙 만들기
# ------------------------------------------------------------
# 역할:
# - 원자료의 세부 행동코드를 2024 CSV와 비교 가능한 대분류로 묶는다.
#
# 예:
# - 1 수면, 2 식사, 3 신변잡일 → 개인유지
# - 4 일 → 일
# - 11 수업, 13 학교외 학습 → 학습
# - 31 개인적 만남, 32 사회적 만남 → 교제 및 참여활동
# - TV, 라디오, 게임, PC통신, 책, 신문 → 문화 및 여가활동
#
# 주의:
# - 이것은 "해석"이 아니라 "분류 기준"이다.
# - 발표자료에는 이 재분류 기준을 반드시 설명해야 한다.
# ============================================================

CATEGORY_ORDER = [
    "개인유지",
    "일",
    "학습",
    "가정관리",
    "돌보기",
    "교제 및 참여활동",
    "문화 및 여가활동",
    "이동",
    "기타"
]

def classify_activity_code(code):
    # 결측값은 기타로 처리한다.
    if pd.isna(code):
        return "기타"

    code = int(code)

    # 개인유지: 수면, 식사, 신변잡일, 휴식, 병/정양
    if code in [1, 2, 3, 41, 42]:
        return "개인유지"

    # 일
    elif code in [4]:
        return "일"

    # 학습: 수업, 과외활동, 학교외 학습, 기능/기술공부
    elif code in [11, 12, 13, 56]:
        return "학습"

    # 가정관리: 취사, 청소, 세탁, 일용품 구입, 가정잡일 등
    elif code in [21, 22, 23, 24, 25, 27]:
        return "가정관리"

    # 돌보기: 자녀돌보기, 아이돌보기, 아이들의 놀이
    elif code in [26, 57]:
        return "돌보기"

    # 교제 및 참여활동: 개인적 만남, 사회적 만남
    elif code in [31, 32]:
        return "교제 및 참여활동"

    # 문화 및 여가활동:
    # 라디오, TV, 관람, 스포츠, 승부놀이, 산책, 취미,
    # PC통신, 컴퓨터게임, 음악, 동영상, 영화,
    # 신문, 잡지, 책, 케이블방송, IPTV, 정보검색, 오락, 스마트폰 등
    elif code in [
        5, 6,
        51, 52, 53, 54, 55,
        58, 59, 60, 61, 62, 63, 64,
        81, 82, 83, 84, 85, 86, 87,
        91, 92, 93, 94, 95
    ]:
        return "문화 및 여가활동"

    # 이동: 통근, 통학, 그 외 이동
    elif code in [71, 72, 73]:
        return "이동"

    # 무응답, 분류불능 등
    else:
        return "기타"

# %% Cell 9
# ============================================================
# 코드묶음 7. 개인-일자별 생활시간표 만들기
# ------------------------------------------------------------
# 역할:
# - 20대 응답자만 대상으로 한다.
# - 하루 96개의 주행동 변수를 긴 형태로 변환한다.
# - 행동코드를 대분류로 바꾼다.
# - 대분류별 시간을 분 단위로 합산한다.
#
# 결과:
# - 한 행 = 한 사람의 하루
# - 예: id 6번 응답자의 1일차 생활시간, 2일차 생활시간, 3일차 생활시간
#
# 왜 15를 곱하는가?
# - 각 주행동 변수는 15분을 의미한다.
# - 예: 수면 코드가 30칸이면 30 × 15 = 450분 수면
# ============================================================

def make_person_day_table(df, meta, year):
    diary = get_diary_vars(meta)

    # 20대만 추출
    df20 = df[(df["age"] >= 20) & (df["age"] <= 29)].copy()

    rows = []

    # 분석에 같이 가져갈 기본 변수
    base_cols = ["id", "sex", "age", "job"]

    for day_num in [1, 2, 3]:
        main_cols = diary[day_num]["main"]

        # 기본 변수 + 해당 날짜의 주행동 변수만 가져온다.
        temp = df20[base_cols + main_cols].copy()

        # wide 형태를 long 형태로 바꾼다.
        # wide: 한 사람의 96개 시간대가 옆으로 펼쳐져 있음
        # long: 한 사람-시간대가 한 행으로 쌓임
        temp_long = temp.melt(
            id_vars=base_cols,
            value_vars=main_cols,
            var_name="time_slot",
            value_name="activity_code"
        )

        # 행동코드를 분석용 대분류로 변환한다.
        temp_long["category"] = temp_long["activity_code"].apply(classify_activity_code)

        # 각 시간대는 15분이다.
        temp_long["minutes"] = 15

        # 사람별, 행동분류별로 시간을 합산한다.
        day_summary = (
            temp_long
            .groupby(base_cols + ["category"], as_index=False)["minutes"]
            .sum()
            .pivot_table(
                index=base_cols,
                columns="category",
                values="minutes",
                fill_value=0
            )
            .reset_index()
        )

        # 어떤 분류가 특정 날짜에 없더라도 컬럼은 유지한다.
        for cat in CATEGORY_ORDER:
            if cat not in day_summary.columns:
                day_summary[cat] = 0

        # 컬럼 순서를 고정한다.
        day_summary = day_summary[base_cols + CATEGORY_ORDER]

        # 연도와 일차 정보를 추가한다.
        day_summary["year"] = year
        day_summary["day"] = day_num

        rows.append(day_summary)

    result = pd.concat(rows, ignore_index=True)

    # 검증용: 하루 총합이 1440분인지 확인한다.
    result["total_minutes"] = result[CATEGORY_ORDER].sum(axis=1)

    return result

time1990 = make_person_day_table(df1990, meta1990, 1990)
time2010 = make_person_day_table(df2010, meta2010, 2010)

print("1990 개인-일자별 데이터 크기:", time1990.shape)
print("2010 개인-일자별 데이터 크기:", time2010.shape)

display(time1990.head())
display(time2010.head())

# %% Cell 10
# ============================================================
# 코드묶음 8. 하루 총합 검증
# ------------------------------------------------------------
# 역할:
# - 생활시간 계산이 제대로 되었는지 확인한다.
# - 한 사람의 하루는 반드시 1440분이어야 한다.
#
# 매우 중요:
# - total_minutes가 1440이 아니면 주행동 변수를 잘못 뽑았을 가능성이 크다.
# - 이 검증을 통과해야 다음 분석으로 넘어갈 수 있다.
# ============================================================

print("1990 하루 총합 검증")
display(time1990["total_minutes"].describe())

print("2010 하루 총합 검증")
display(time2010["total_minutes"].describe())

print("1990 총합 이상치")
display(time1990[time1990["total_minutes"] != 1440].head())

print("2010 총합 이상치")
display(time2010[time2010["total_minutes"] != 1440].head())

# %% Cell 11
# ============================================================
# 코드묶음 9. 1990·2010 연도별 평균 생활시간표 만들기
# ------------------------------------------------------------
# 역할:
# - 개인-일자별 데이터를 연도별 평균으로 요약한다.
# - 결과는 "20대의 평균 하루"가 된다.
#
# 예:
# - 1990년 20대는 평균적으로 개인유지 몇 분, 일 몇 분, 학습 몇 분인지 계산
# - 2010년 20대도 같은 방식으로 계산
# ============================================================

time_1990_2010 = pd.concat([time1990, time2010], ignore_index=True)

summary_1990_2010 = (
    time_1990_2010
    .groupby("year")[CATEGORY_ORDER]
    .mean()
    .round(1)
    .reset_index()
)

display(summary_1990_2010)

# 검증: 각 연도별 합계가 1440분에 가까운지 확인
summary_1990_2010["합계"] = summary_1990_2010[CATEGORY_ORDER].sum(axis=1).round(1)
display(summary_1990_2010)

# %% Cell 12
# ============================================================
# 코드묶음 10. 2024 CSV 정리
# ------------------------------------------------------------
# 역할:
# - 2024 자료는 원자료가 아니라 이미 집계된 CSV이다.
# - 시간값이 "11:34"처럼 시:분 형태로 들어 있다.
# - 이를 분 단위 숫자로 바꾼다.
#
# 주의:
# - 2024는 개인별 데이터가 아니므로 1990·2010처럼 개인별 재계산을 할 수 없다.
# - 이미 계산된 20대 평균값을 가져와 비교에 사용한다.
# ============================================================

df2024_raw = pd.read_csv(path_2024, encoding="utf-8-sig")

display(df2024_raw.head(15))

# 2024 CSV는 앞 2행이 헤더 설명처럼 들어가 있으므로,
# 실제 데이터는 2행부터 사용한다.
df2024 = df2024_raw.iloc[2:].copy()

# 컬럼명을 이해하기 쉽게 바꾼다.
df2024 = df2024.rename(columns={
    "연령대별": "age_group",
    "행동분류별": "category_2024",
    "2024": "요일평균_계",
    "2024.1": "요일평균_남자",
    "2024.2": "요일평균_여자",
    "2024.3": "평일_계",
    "2024.4": "평일_남자",
    "2024.5": "평일_여자",
    "2024.6": "토요일_계",
    "2024.7": "토요일_남자",
    "2024.8": "토요일_여자",
    "2024.9": "일요일_계",
    "2024.10": "일요일_남자",
    "2024.11": "일요일_여자"
})

# "11:34" 형태의 시간을 분으로 바꾸는 함수
def time_to_minutes(x):
    if pd.isna(x) or x == "-":
        return 0

    hour, minute = str(x).split(":")
    return int(hour) * 60 + int(minute)

# 2024 행동분류를 우리가 만든 분석용 분류에 맞춘다.
mapping_2024 = {
    "계": None,
    "개인유지": "개인유지",
    "일": "일",
    "학습": "학습",
    "가정관리": "가정관리",
    "가족 및 가구원 돌보기": "돌보기",
    "자원봉사 및 무급연수": "기타",
    "교제 및 참여활동": "교제 및 참여활동",
    "문화 및 여가활동": "문화 및 여가활동",
    "이동": "이동",
    "기타": "기타"
}

df2024["category"] = df2024["category_2024"].map(mapping_2024)
df2024["minutes"] = df2024["요일평균_계"].apply(time_to_minutes)

display(df2024[["category_2024", "category", "요일평균_계", "minutes"]])

# %% Cell 13
# ============================================================
# 코드묶음 11. 2024 평균표 형태 맞추기
# ------------------------------------------------------------
# 역할:
# - 2024 자료를 1990·2010 summary와 같은 형태로 만든다.
# - 그래야 세 연도를 하나의 표로 합칠 수 있다.
# ============================================================

summary2024 = (
    df2024
    .dropna(subset=["category"])
    .groupby("category", as_index=False)["minutes"]
    .sum()
)

summary2024["year"] = 2024

summary2024_wide = (
    summary2024
    .pivot_table(
        index="year",
        columns="category",
        values="minutes",
        fill_value=0
    )
    .reset_index()
)

# 빠진 컬럼이 있으면 0으로 추가한다.
for cat in CATEGORY_ORDER:
    if cat not in summary2024_wide.columns:
        summary2024_wide[cat] = 0

summary2024_wide = summary2024_wide[["year"] + CATEGORY_ORDER]

display(summary2024_wide)

# 검증: 2024도 합계가 1440분이어야 한다.
summary2024_wide["합계"] = summary2024_wide[CATEGORY_ORDER].sum(axis=1)
display(summary2024_wide)

# %% Cell 14
# ============================================================
# 코드묶음 12. 최종 비교표 만들기
# ------------------------------------------------------------
# 역할:
# - 1990, 2010, 2024를 하나의 표로 합친다.
# - 이 표가 앞으로 그래프와 PPT의 핵심 자료가 된다.
#
# 산출물:
# - final_summary
# ============================================================

# 코드묶음 9에서 summary_1990_2010에 "합계" 컬럼을 추가했으므로,
# 합치기 전에 합계 컬럼은 제거한다.
summary_1990_2010_clean = summary_1990_2010.drop(columns=["합계"], errors="ignore")
summary2024_clean = summary2024_wide.drop(columns=["합계"], errors="ignore")

final_summary = pd.concat(
    [summary_1990_2010_clean, summary2024_clean],
    ignore_index=True
)

final_summary["합계"] = final_summary[CATEGORY_ORDER].sum(axis=1).round(1)

display(final_summary)

# %% Cell 15
# ============================================================
# 코드묶음 13. 그래프용 데이터 만들기
# ------------------------------------------------------------
# 역할:
# - final_summary는 wide 형태이다.
# - 그래프를 그리기 편하도록 long 형태로 바꾼다.
#
# wide 예:
# year | 개인유지 | 일 | 학습 ...
#
# long 예:
# year | category | minutes
# 1990 | 개인유지 | 694.8
# 1990 | 일 | 202.0
# ============================================================

plot_data = final_summary.drop(columns=["합계"], errors="ignore").melt(
    id_vars="year",
    value_vars=CATEGORY_ORDER,
    var_name="category",
    value_name="minutes"
)

display(plot_data.head(20))

# %% Cell 16
# ============================================================
# 코드묶음 14. 연도별 하루 구성 누적 막대그래프
# ------------------------------------------------------------
# 역할:
# - 1990, 2010, 2024년 20대의 하루 24시간 구성이 어떻게 다른지 보여준다.
# - PPT에서 가장 핵심적인 전체 그림으로 사용할 수 있다.
#
# 해석 주의:
# - 이 그래프만 보고 "고립이 증가했다"고 말하면 안 된다.
# - 생활시간 구성 변화가 나타난다고 해석해야 한다.
# ============================================================
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"

fm.fontManager.addfont(font_path)
plt.rcParams["font.family"] = "NanumGothic"
plt.rcParams["axes.unicode_minus"] = False

print(plt.rcParams["font.family"])
plot_wide = final_summary.set_index("year")[CATEGORY_ORDER]

ax = plot_wide.plot(
    kind="bar",
    stacked=True,
    figsize=(12, 6)
)

plt.title("20대의 하루 생활시간 구성 변화: 1990·2010·2024")
plt.xlabel("연도")
plt.ylabel("분")
plt.xticks(rotation=0)
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.show()

# %% Cell 17
# ============================================================
# 코드묶음 15. 교제 및 참여활동 변화 그래프
# ------------------------------------------------------------
# 역할:
# - 이번 주제의 핵심 지표 중 하나인 "사회적 연결 시간"을 본다.
# - 교제 및 참여활동 시간이 연도별로 어떻게 달라졌는지 확인한다.
#
# 해석 주의:
# - 교제 시간이 줄었다고 해서 바로 고립이라고 단정하면 안 된다.
# - "사회적 연결과 관련된 생활시간의 변화"라고 표현해야 한다.
# ============================================================

social_data = final_summary[["year", "교제 및 참여활동"]]

plt.figure(figsize=(8, 5))
plt.plot(social_data["year"], social_data["교제 및 참여활동"], marker="o")
plt.title("20대 교제 및 참여활동 시간 변화")
plt.xlabel("연도")
plt.ylabel("분")
plt.xticks(social_data["year"])
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

display(social_data)

# %% Cell 18
# ============================================================
# 코드묶음 16. 문화 및 여가활동 변화 그래프
# ------------------------------------------------------------
# 역할:
# - 여가 시간이 어떻게 변했는지 확인한다.
# - 특히 2010 이후 미디어, 스마트폰, 온라인 활동과 연결해서 해석할 수 있다.
#
# 해석 주의:
# - 문화 및 여가활동 증가는 무조건 부정적인 현상이 아니다.
# - "여가 방식의 개인화 가능성" 정도로 조심스럽게 해석한다.
# ============================================================

leisure_data = final_summary[["year", "문화 및 여가활동"]]

plt.figure(figsize=(8, 5))
plt.plot(leisure_data["year"], leisure_data["문화 및 여가활동"], marker="o")
plt.title("20대 문화 및 여가활동 시간 변화")
plt.xlabel("연도")
plt.ylabel("분")
plt.xticks(leisure_data["year"])
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

display(leisure_data)

# %% Cell 19
# ============================================================
# 코드묶음 17. 일+학습 시간 변화 그래프
# ------------------------------------------------------------
# 역할:
# - 20대의 의무활동 시간을 확인한다.
# - 일과 학습은 청년의 사회적 역할, 경제활동, 교육활동과 관련된다.
#
# 왜 필요한가?
# - 교제나 여가만 보면 해석이 약하다.
# - 일+학습 시간이 함께 어떻게 변했는지 봐야 하루 구조를 더 균형 있게 해석할 수 있다.
# ============================================================

final_summary["일+학습"] = final_summary["일"] + final_summary["학습"]

work_study_data = final_summary[["year", "일", "학습", "일+학습"]]

plt.figure(figsize=(8, 5))
plt.plot(work_study_data["year"], work_study_data["일+학습"], marker="o")
plt.title("20대 일+학습 시간 변화")
plt.xlabel("연도")
plt.ylabel("분")
plt.xticks(work_study_data["year"])
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()

display(work_study_data)

# %% Cell 20
# ============================================================
# 코드묶음 18. 최종 결과 저장
# ------------------------------------------------------------
# 역할:
# - 분석 결과표를 CSV 파일로 저장한다.
# - PPT 만들 때 표를 다시 확인하거나 그래프를 재사용하기 쉽다.
# ============================================================

final_summary.to_csv("kossda_20s_timeuse_summary.csv", index=False, encoding="utf-8-sig")
time1990.to_csv("kossda_1990_20s_person_day.csv", index=False, encoding="utf-8-sig")
time2010.to_csv("kossda_2010_20s_person_day.csv", index=False, encoding="utf-8-sig")

print("저장 완료")

# %% Cell 21
# ============================================================
# 코드묶음 19. 최종 요약표 다시 불러오기
# ------------------------------------------------------------
# 역할:
# - 앞에서 저장한 final_summary CSV를 다시 불러온다.
# - Colab 런타임이 끊기거나 중간부터 다시 시작할 때 사용한다.
#
# 왜 필요한가?
# - 지금부터는 정제보다 분석·시각화 단계다.
# - 따라서 원자료를 다시 읽지 않고 최종 요약표부터 작업할 수 있다.
# ============================================================

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

final_summary = pd.read_csv("/content/kossda_20s_timeuse_summary.csv")

CATEGORY_ORDER = [
    "개인유지",
    "일",
    "학습",
    "가정관리",
    "돌보기",
    "교제 및 참여활동",
    "문화 및 여가활동",
    "이동",
    "기타"
]

display(final_summary)

# 합계 검증
final_summary["합계_재계산"] = final_summary[CATEGORY_ORDER].sum(axis=1).round(1)
display(final_summary[["year", "합계", "합계_재계산"]])

# %% Cell 22
# ============================================================
# 코드묶음 20. 그래프 저장 폴더와 한글 폰트 설정
# ------------------------------------------------------------
# 역할:
# - PPT에 넣을 그래프 이미지를 저장할 폴더를 만든다.
# - matplotlib에서 한글이 깨지지 않도록 폰트를 설정한다.
#
# 주의:
# - Colab에서 한글이 깨지면 이 코드묶음을 먼저 실행한다.
# - 런타임 재시작 없이 작동하는 경우가 많다.
# ============================================================

# 그래프 저장 폴더 생성
output_dir = "/content/kossda_figures"
os.makedirs(output_dir, exist_ok=True)

# 한글 폰트 설치 및 설정
# !apt-get -qq install fonts-nanum

import matplotlib as mpl
import matplotlib.font_manager as fm

font_path = "/usr/share/fonts/truetype/nanum/NanumGothic.ttf"
fm.fontManager.addfont(font_path)

plt.rcParams["font.family"] = "NanumGothic"
plt.rcParams["axes.unicode_minus"] = False

print("그래프 저장 폴더:", output_dir)
print("현재 폰트:", plt.rcParams["font.family"])

# %% Cell 23
# ============================================================
# 코드묶음 21. 분 단위를 시:분과 비중으로 변환
# ------------------------------------------------------------
# 역할:
# - 발표자료에서 이해하기 쉽도록 분 단위를 "시간:분" 형태로 바꾼다.
# - 각 행동이 하루 1440분 중 몇 %인지 계산한다.
#
# 왜 필요한가?
# - PPT에서는 87.9분보다 "약 1시간 28분"이 직관적이다.
# - 비중을 같이 보면 하루 구조 변화가 더 잘 보인다.
# ============================================================

def minutes_to_hm(x):
    total = int(round(x))
    h = total // 60
    m = total % 60
    return f"{h}시간 {m}분"

# 시:분 변환표
summary_hm = final_summary[["year"] + CATEGORY_ORDER].copy()

for col in CATEGORY_ORDER:
    summary_hm[col] = summary_hm[col].apply(minutes_to_hm)

display(summary_hm)

# 비중표
summary_share = final_summary[["year"] + CATEGORY_ORDER].copy()

for col in CATEGORY_ORDER:
    summary_share[col] = (summary_share[col] / 1440 * 100).round(1)

display(summary_share)

# %% Cell 24
# ============================================================
# 코드묶음 22. 변화량 분석
# ------------------------------------------------------------
# 역할:
# - 1990년과 2024년 사이 어떤 생활시간 항목이 가장 크게 변했는지 계산한다.
# - 단순히 "교제 시간이 줄었다"가 아니라,
#   "전체 생활시간 구성 중 무엇이 가장 크게 바뀌었는가"를 보여준다.
#
# 해석 주의:
# - 1990년 기타 항목은 무응답·분류불능 가능성이 있으므로 해석에서 제외하거나 보조적으로만 본다.
# ============================================================

summary_indexed = final_summary.set_index("year")

change_1990_2024 = pd.DataFrame({
    "category": CATEGORY_ORDER,
    "1990": summary_indexed.loc[1990, CATEGORY_ORDER].values,
    "2024": summary_indexed.loc[2024, CATEGORY_ORDER].values
})

change_1990_2024["변화량_분"] = (change_1990_2024["2024"] - change_1990_2024["1990"]).round(1)
change_1990_2024["변화량_시간"] = change_1990_2024["변화량_분"].apply(
    lambda x: f"{'+' if x > 0 else ''}{x}분"
)
change_1990_2024["절대변화량"] = change_1990_2024["변화량_분"].abs()

# 변화량 큰 순서
change_rank = change_1990_2024.sort_values("절대변화량", ascending=False)

display(change_rank)

# %% Cell 25
# ============================================================
# 코드묶음 23. 구간별 변화 분석
# ------------------------------------------------------------
# 역할:
# - 변화가 어느 시기에 집중되었는지 확인한다.
# - 1990→2010 변화와 2010→2024 변화를 나누어 본다.
#
# 왜 필요한가?
# - "1990년에서 2024년까지 변했다"보다
#   "어느 구간에서 더 많이 변했는가"를 보여주면 분석성이 올라간다.
#
# 한계:
# - 시점이 3개뿐이므로 엄밀한 변화점 분석은 어렵다.
# - 대신 탐색적 구간 비교로 제시한다.
# ============================================================

period_change = pd.DataFrame({
    "category": CATEGORY_ORDER,
    "1990→2010": (summary_indexed.loc[2010, CATEGORY_ORDER] - summary_indexed.loc[1990, CATEGORY_ORDER]).values,
    "2010→2024": (summary_indexed.loc[2024, CATEGORY_ORDER] - summary_indexed.loc[2010, CATEGORY_ORDER]).values,
    "1990→2024": (summary_indexed.loc[2024, CATEGORY_ORDER] - summary_indexed.loc[1990, CATEGORY_ORDER]).values,
})

period_change[["1990→2010", "2010→2024", "1990→2024"]] = period_change[
    ["1990→2010", "2010→2024", "1990→2024"]
].round(1)

# 어느 구간 변화가 더 컸는지 표시
def bigger_period(row):
    if abs(row["1990→2010"]) > abs(row["2010→2024"]):
        return "1990→2010 변화가 큼"
    elif abs(row["1990→2010"]) < abs(row["2010→2024"]):
        return "2010→2024 변화가 큼"
    else:
        return "두 구간 비슷"

period_change["변화 집중 구간"] = period_change.apply(bigger_period, axis=1)

display(period_change)

# %% Cell 26
# ============================================================
# 코드묶음 24. 하루 구성 누적 막대그래프
# ------------------------------------------------------------
# 역할:
# - 1990, 2010, 2024년 20대의 평균 하루 구성을 한눈에 보여준다.
# - PPT에서 "전체 결과" 슬라이드에 사용한다.
#
# 해석:
# - 하루 전체 구조가 어떻게 바뀌었는지 보여주는 그래프다.
# - 특정 항목 하나보다 전체 구성 변화를 설명할 때 사용한다.
# ============================================================

plot_wide = final_summary.set_index("year")[CATEGORY_ORDER]

ax = plot_wide.plot(
    kind="bar",
    stacked=True,
    figsize=(12, 6)
)

plt.title("20대의 하루 생활시간 구성 변화: 1990·2010·2024", fontsize=15)
plt.xlabel("연도")
plt.ylabel("분")
plt.xticks(rotation=0)
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()

save_path = f"{output_dir}/fig1_하루구성_누적막대.png"
plt.savefig(save_path, dpi=300, bbox_inches="tight")
plt.show()

print("저장 완료:", save_path)

# %% Cell 27
# ============================================================
# 코드묶음 25. 1990→2024 항목별 변화량 그래프
# ------------------------------------------------------------
# 역할:
# - 어떤 생활시간 항목이 가장 크게 증가하거나 감소했는지 보여준다.
# - "교제 감소"만 보여주는 것이 아니라 전체 변화 속에서 위치를 보여준다.
#
# 해석:
# - 변화량이 양수면 증가, 음수면 감소이다.
# - 기타는 자료상 한계로 별도 설명해야 한다.
# ============================================================

change_plot = change_1990_2024.copy()
change_plot = change_plot.sort_values("변화량_분")

plt.figure(figsize=(10, 6))
plt.barh(change_plot["category"], change_plot["변화량_분"])
plt.axvline(0, linewidth=1)
plt.title("1990년 대비 2024년 20대 생활시간 변화량")
plt.xlabel("변화량(분)")
plt.ylabel("행동분류")
plt.tight_layout()

save_path = f"{output_dir}/fig2_1990_2024_변화량.png"
plt.savefig(save_path, dpi=300, bbox_inches="tight")
plt.show()

print("저장 완료:", save_path)

# %% Cell 28
# ============================================================
# 코드묶음 26. 핵심 지표 변화 선그래프
# ------------------------------------------------------------
# 역할:
# - 이번 연구의 핵심 지표를 한 그래프에 보여준다.
# - 교제 및 참여활동, 문화 및 여가활동, 일+학습, 이동을 비교한다.
#
# 왜 필요한가?
# - 교제 시간만 따로 보면 단순 감소 그래프가 된다.
# - 다른 생활시간과 함께 보면 하루 구조 변화로 해석할 수 있다.
# ============================================================

trend_data = final_summary.copy()
trend_data["일+학습"] = trend_data["일"] + trend_data["학습"]

key_cols = ["교제 및 참여활동", "문화 및 여가활동", "일+학습", "이동"]

plt.figure(figsize=(10, 6))

for col in key_cols:
    plt.plot(trend_data["year"], trend_data[col], marker="o", label=col)

plt.title("20대 주요 생활시간 변화")
plt.xlabel("연도")
plt.ylabel("분")
plt.xticks(trend_data["year"])
plt.grid(True, alpha=0.3)
plt.legend()
plt.tight_layout()

save_path = f"{output_dir}/fig3_핵심지표_변화.png"
plt.savefig(save_path, dpi=300, bbox_inches="tight")
plt.show()

print("저장 완료:", save_path)

# %% Cell 29
# ============================================================
# 코드묶음 27. 교제·참여 대비 문화·여가 비율
# ------------------------------------------------------------
# 역할:
# - 단순히 교제 시간이 줄었다고만 보지 않고,
#   문화·여가 시간과의 상대적 관계를 본다.
#
# 지표:
# - 문화 및 여가활동 시간 / 교제 및 참여활동 시간
#
# 해석:
# - 값이 커질수록 교제·참여 시간에 비해 문화·여가 시간이 상대적으로 크다는 뜻이다.
#
# 주의:
# - 이것은 "고립지수"가 아니다.
# - 발표에서는 "생활시간상 여가-교제 균형 지표" 정도로 조심스럽게 표현한다.
# ============================================================

ratio_data = final_summary[["year", "교제 및 참여활동", "문화 및 여가활동"]].copy()

ratio_data["여가_대비_교제비"] = (
    ratio_data["문화 및 여가활동"] / ratio_data["교제 및 참여활동"]
).round(2)

display(ratio_data)

plt.figure(figsize=(8, 5))
plt.plot(ratio_data["year"], ratio_data["여가_대비_교제비"], marker="o")
plt.title("교제·참여 대비 문화·여가 시간 비율")
plt.xlabel("연도")
plt.ylabel("문화·여가 / 교제·참여")
plt.xticks(ratio_data["year"])
plt.grid(True, alpha=0.3)
plt.tight_layout()

save_path = f"{output_dir}/fig4_여가대비교제비.png"
plt.savefig(save_path, dpi=300, bbox_inches="tight")
plt.show()

print("저장 완료:", save_path)

# %% Cell 30
# ============================================================
# 코드묶음 28. PPT용 핵심 수치 정리
# ------------------------------------------------------------
# 역할:
# - 발표자료에 바로 넣을 수 있는 핵심 수치를 자동으로 계산한다.
# - 수작업으로 계산하다가 틀리는 것을 방지한다.
# ============================================================

social_1990 = summary_indexed.loc[1990, "교제 및 참여활동"]
social_2024 = summary_indexed.loc[2024, "교제 및 참여활동"]
social_change = social_2024 - social_1990

leisure_1990 = summary_indexed.loc[1990, "문화 및 여가활동"]
leisure_2024 = summary_indexed.loc[2024, "문화 및 여가활동"]
leisure_change = leisure_2024 - leisure_1990

move_1990 = summary_indexed.loc[1990, "이동"]
move_2024 = summary_indexed.loc[2024, "이동"]
move_change = move_2024 - move_1990

workstudy_1990 = summary_indexed.loc[1990, "일"] + summary_indexed.loc[1990, "학습"]
workstudy_2024 = summary_indexed.loc[2024, "일"] + summary_indexed.loc[2024, "학습"]
workstudy_change = workstudy_2024 - workstudy_1990

print("===== PPT 핵심 수치 =====")
print(f"교제 및 참여활동: {social_1990:.1f}분 → {social_2024:.1f}분 ({social_change:.1f}분)")
print(f"문화 및 여가활동: {leisure_1990:.1f}분 → {leisure_2024:.1f}분 ({leisure_change:.1f}분)")
print(f"이동: {move_1990:.1f}분 → {move_2024:.1f}분 ({move_change:.1f}분)")
print(f"일+학습: {workstudy_1990:.1f}분 → {workstudy_2024:.1f}분 ({workstudy_change:.1f}분)")

# %% Cell 31
# ============================================================
# 코드묶음 29. 그래프 파일 목록 확인
# ------------------------------------------------------------
# 역할:
# - PPT에 넣을 그래프 이미지가 제대로 저장되었는지 확인한다.
# ============================================================

import os

for file in os.listdir(output_dir):
    print(file)

# %% Cell 32
import pandas as pd
sample = pd.DataFrame({
    "id": [1, 2],
    "sex": [1, 2],
    "v1": [1, 2],
    "v4": [1, 31],
    "v7": [2, 6]
})

sample_long = sample.melt(
    id_vars=["id", "sex"],
    value_vars=["v1", "v4", "v7"],
    var_name="time_slot",
    value_name="activity_code"
)

display(sample)
display(sample_long)
