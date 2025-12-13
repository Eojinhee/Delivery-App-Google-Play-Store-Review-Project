# 파일명: crawl_coupang.py
import pandas as pd
from google_play_scraper import reviews, Sort
import time

print("--- Coupang Eats 리뷰 크롤링 시작 (패키지) ---")

app_id = 'com.coupang.mobile.eats'
app_name = 'Coupang Eats'
target_count = 10000
request_count = target_count + 5000  # 필터링 대비 넉넉하게

try:
    result, _ = reviews(
        app_id,
        lang='ko',
        sort=Sort.NEWEST,  # 쿠팡이츠는 '최신순'이 잘 작동합니다.
        count=request_count
    )

    print(f"총 {len(result)}건 리뷰 (필터링 전) 원본 수집 완료.")

    filtered_reviews = []
    for review in result:
        content = review['content']
        if content and len(content.strip()) >= 10:
            filtered_reviews.append({
                'app': app_name,
                'date': review['at'],
                'score': review['score'],
                'content': content
            })

    print(f"필터링 후 {len(filtered_reviews)}건 유효 리뷰 확보.")

    if filtered_reviews:
        df = pd.DataFrame(filtered_reviews)
        if len(df) > target_count:
            df = df.head(target_count)

        output_filename = "coupang_eats_reviews.csv"
        df.to_csv(output_filename, index=False, encoding='utf-8-sig')
        print(f"✅ {app_name} 리뷰 {len(df)}건 CSV 저장 완료: {output_filename}")
    else:
        print("⚠️ 10글자 이상 리뷰가 없습니다.")

except Exception as e:
    print(f"❌ 크롤링 중 오류 발생: {e}")