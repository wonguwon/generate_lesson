---
name: monthly-report
description: 새 달 주문 CSV로 월간 주문 정리와 Claude Docs 월간 주문 보고서를 만들 때 쓴다.
argument-hint: [YYYY-MM]
---

# 월간 주문 보고 ($ARGUMENTS)

1. '원본/월별주문'에서 $ARGUMENTS 달의 주문 CSV를 찾아 'scripts/주문정리.py'로 정리한다. 새로 짜지 않는다.
2. Claude Docs로 'YYYY년 M월 월간 주문 보고서'를 만든다.
   1) 요약: 주문 건수, 판매 합계, 전월 대비 금액·%
   2) 7월부터 월별 추이 표
   3) 거래처 상위 3곳 표(거래처/담당자/판매 금액/그 달 합계 대비 비중)와 3곳 합 비중 한 줄
   4) 그 달 수량이 비어 빠진 주문번호
3. 끝나면 주문 건수, 판매 합계, 전월 대비와 Docs 링크를 채팅에 보여 준다.

- 발표자료(Claude Slides)는 따로 요청할 때만 만든다.
