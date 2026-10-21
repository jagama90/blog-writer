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

## 기존 관리화면 연결 (이번 개발 브랜치)

개발 브랜치에서 `dashboard/start.bat`를 재실행하면 프론트엔드를 다시 빌드하고, 상단에 **나는 SOLO** 메뉴가 표시됩니다. 이 메뉴는 입력된 JSON으로 **검수용 원고만** 생성합니다.

`GET /api/diagnostics`는 OpenClaw 실행 파일이 없는 경우 `missing_cli`를 반환하며, 관리화면 상태 표시를 경고로 변경합니다. **기존 OpenClaw 글쓰기 자체를 대체하지는 않습니다.**

개발 브랜치가 아닌 기본 브랜치를 유지하려면 PR 검수 후 병합해야 합니다. PC에 로컬 수정이 있으면 브랜치 전환 전에 반드시 백업/커밋하세요.

## 검증 명령

```powershell
.\venv\Scripts\python.exe -m unittest discover -s nassol_review -p "test_*.py"
```

테스트가 통과하는지 로컬에서 확인해야 합니다. 이 개발 환경에서는 GitHub 저장소를 직접 클론해 테스트를 실행하지 못했습니다.
