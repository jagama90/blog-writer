# 나솔 원고 검수 워크플로 (개발 브랜치)

이 폴더는 기존 IT 블로그 생성기와 분리되어 있습니다. 외부 유료 API 호출, 자동 게시, 예약 실행을 하지 않습니다.

## 사용 방법

```powershell
cd C:\blog-writer
git fetch origin
git switch feature/nassol-review-workflow
.\venv\Scripts\python.exe .\nassol_review\editorial.py --input .\nassol_review\sample.json
```

실행 결과: `nassol_review/outputs/<실행시각>/` 안에 `final_title.txt` **1개**, `blog_review_draft.md`, `source_audit.json`이 생성됩니다.

## 주의

- 입력 JSON의 기사 주장과 SNS 주소는 자동 검증되지 않습니다. 기사 원문을 직접 확인한 후 입력하세요.
- `editorial.take`와 `editorial.ending`은 필자의 실제 관점을 입력해야 합니다. 없는 의견을 AI가 지어내지 않습니다.
- 사진은 삽입 위치만 생성합니다. 저작권 확인 없이 기사 사진을 내려받지 않습니다.
- **이번 PR은 원고 엔진의 GitHub 배포를 위한 첫 단계**입니다. 카드뉴스·쇼츠·대시보드와의 통합 및 기사 자동 검증은 아직 포함되지 않았습니다.
- `master`에 병합하기 전까지는 `git pull`만으로 기본 브랜치에 반영되지 않습니다.
