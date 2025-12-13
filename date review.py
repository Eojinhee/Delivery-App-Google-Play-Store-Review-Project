#핵심 그래 실제로 그려주는 아주 중요한 분석 코드
# 사용한 코드 negative_keywords = ['최악', '오류', '렉', '업데이트', '불편', '짜증', '안됨', '안돼', '연결', '상담', '문의', '삭제', '망해', '쓰레기', '버그', '개판', '화면', '로딩', '제발', '고치', '장난', '아깝', '돈날', '시간낭비']

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import re
import os
import matplotlib.font_manager as fm

# ---------------------------------------------------------
# 1. 폰트 설정 (Windows 환경: 맑은 고딕)
# ---------------------------------------------------------
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False # 마이너스 기호 깨짐 방지

# ---------------------------------------------------------
# 2. 데이터 로드 및 전처리 (이 부분이 빠져서 에러가 났었습니다)
# ---------------------------------------------------------
# CSV 파일들이 파이썬 파일과 같은 폴더에 있어야 합니다.
try:
    df_baemin = pd.read_csv('data/baemin_reviews_final_10len.csv')
    df_coupang = pd.read_csv('data/coupang_eats_reviews.csv')
    print(" 데이터 파일 로드 성공!")
except FileNotFoundError:
    print(" 오류: CSV 파일을 찾을 수 없습니다.")
    print("'baemin_reviews_final_10len.csv'와 'coupang_eats_reviews.csv'가 같은 폴더에 있는지 확인해주세요.")
    exit()

# 앱 구분 컬럼 추가
df_baemin['app'] = 'Baemin'
df_coupang['app'] = 'Coupang Eats'

# 날짜 변환 함수
def convert_date(d):
    try:
        m = re.search(r'(\d+)년 (\d+)월 (\d+)일', str(d))
        if m:
            return f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"
        return d
    except: return d

# 전처리 적용
df_baemin['date'] = df_baemin['date'].apply(convert_date)
df_baemin['date'] = pd.to_datetime(df_baemin['date'], errors='coerce') # 날짜 형식으로 변환

df_coupang['date'] = pd.to_datetime(df_coupang['date']).dt.strftime('%Y-%m-%d')
df_coupang['date'] = pd.to_datetime(df_coupang['date'], errors='coerce')

# 데이터 합치기
cols = ['app', 'score', 'content', 'date']
df = pd.concat([df_baemin[cols], df_coupang[cols]], ignore_index=True)

# ---------------------------------------------------------
# 3. 분석 함수 정의
# ---------------------------------------------------------
negative_keywords = ['최악', '오류', '렉', '업데이트', '불편', '짜증', '안됨', '안돼', '연결', '상담', '문의', '삭제', '망해', '쓰레기', '버그', '개판', '화면', '로딩', '제발', '고치', '장난', '아깝', '돈날', '시간낭비']
def is_negative(text):
    return any(kw in str(text) for kw in negative_keywords)

# ---------------------------------------------------------
# 4. [추가 분석 1] 리뷰 길이 분석 그래프 생성
# ---------------------------------------------------------
print(" 그래프 1 생성 중... (리뷰 길이 분석)")
df_baemin_5 = df[(df['app'] == 'Baemin') & (df['score'] == 5)].copy()
df_baemin_5['type'] = df_baemin_5['content'].apply(lambda x: 'Fake 5-Star (불만)' if is_negative(x) else 'Real 5-Star (만족)')
df_baemin_5['length'] = df_baemin_5['content'].apply(len)

plt.figure(figsize=(10, 6))
sns.boxplot(data=df_baemin_5, x='type', y='length', palette=['#ff6b6b', '#51cf66'])
plt.title('리뷰 성향에 따른 글자 수 차이 (Review Length)', fontsize=16, fontweight='bold')
plt.ylabel('글자 수')
plt.xlabel('리뷰 유형')
plt.ylim(0, 300)
plt.tight_layout()
plt.savefig('review_length_analysis_ko.png')
print("   -> 저장 완료: review_length_analysis_ko.png")
plt.close()

# ---------------------------------------------------------
# 5. [추가 분석 2] 월별 부정 리뷰 추이 그래프 생성
# ---------------------------------------------------------
print(" 그래프 2 생성 중 (월별 추이)")
# '년-월' 형식으로 변환 (PeriodIndex 사용)
df_baemin_5['year_month'] = df_baemin_5['date'].dt.to_period('M')

# 월별 개수 세기
monthly_trend = df_baemin_5[df_baemin_5['type'] == 'Fake 5-Star (불만)'].groupby('year_month').size()

plt.figure(figsize=(12, 6))
monthly_trend.plot(kind='line', marker='o', color='#ff6b6b', linewidth=2)
plt.title('배달의민족 부정 리뷰(가짜 5점) 월별 추이', fontsize=16, fontweight='bold')
plt.ylabel('부정 리뷰 수')
plt.xlabel('기간')
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig('monthly_negative_trend_ko.png')
print("   -> 저장 완료: monthly_negative_trend_ko.png")
plt.close()

print("\n 모든 작업 완료!")