# Data Preparation

이 폴더는 원자료 배치 방법을 설명하기 위한 자리입니다. 실제 원자료는 데이터 이용 조건과 재배포 가능 범위를 확인한 뒤 직접 준비하세요.

분석 코드는 다음 파일명을 사용합니다.

```text
1990_data.sav
2010_data.sav
2024_data.csv
```

Google Colab에서 실행할 경우 파일은 다음 경로에 있어야 합니다.

```text
/content/1990_data.sav
/content/2010_data.sav
/content/2024_data.csv
```

로컬 Jupyter 환경에서 실행한다면 `kossda_youth_social_connection_analysis.py` 안의 `path_1990`, `path_2010`, `path_2024` 값을 로컬 경로에 맞게 바꾸면 됩니다.

## Notes

- `1990_data.sav`와 `2010_data.sav`는 SPSS SAV 원자료입니다.
- `2024_data.csv`는 2024년 생활시간 집계 CSV입니다.
- 원자료 파일은 GitHub에 올리지 않는 것을 권장합니다.
