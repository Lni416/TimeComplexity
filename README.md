# Python Complexity Analyzer

정적 분석을 통해 파이썬 코드의 시간 복잡도를 추론하는 도구입니다.

## 주요 기능
- **AST 분석**: `ast` 모듈 기반 루프 중첩도 계산 및 Big-O 표기.
- **자동 Git 연동**: 코드 수정 시 GitHub 자동 커밋 및 푸시.
- **파일 탐색**: CLI를 통한 분석 대상 파일 선택.

## 개발 노트
이 프로그램은 **antigravity**를 활용하여 개발되었습니다. 

## 실행 방법
1. `pip install gitpython`
2. `python main.py` 실행 후 파일 번호 선택.
