# 🚀 Python Complexity Analyzer (with Antigravity)

**Python Complexity Analyzer**는 정적 분석을 통해 파이썬 코드의 구조를 파악하고, 최악의 경우 시간 복잡도를 Big-O 표기법으로 추론하는 지능형 도구입니다.

이 프로젝트는 사용자의 기획 아이디어를 바탕으로, AI 자동화 도구인 **antigravity**를 활용하여 설계 및 구현되었습니다.

---

## 🛠️ Key Features

* **Interactive File Selection:** 현재 디렉토리의 `.py` 파일을 탐색하고 숫자로 간편하게 선택하여 분석합니다.
* **AST Static Analysis:** 파이썬 내장 `ast` (Abstract Syntax Tree) 모듈을 사용하여 코드의 루프 중첩 깊이와 구조를 정밀하게 분석합니다.
* **Complexity Estimation:** 분석된 구조를 기반으로 $O(1)$, $O(n)$, $O(n^2)$ 등의 **Big-O Notation**을 도출합니다.
* **Auto-Git Sync:** 개발 과정에서 소스 코드의 변경 사항이 발생하면 GitHub에 자동으로 커밋 및 푸시하여 버전을 관리합니다.
* **Smart Filtering:** `.gitignore` 자동 생성을 통해 `.idea`, `__pycache__`, `.DS_Store` 등 불필요한 설정 파일의 업로드를 방지합니다.

---

## 🤖 Collaboration Note

> **"이 프로그램은 사용자의 아이디어와 설계를 바탕으로 antigravity와의 협업을 통해 개발되었습니다."**

본 프로젝트는 전통적인 코딩 방식 대신, **프롬프트 엔지니어링과 AI 기반 코드 생성 기술**을 결합하여 개발 효율을 극대화한 결과물입니다. 아이디어 제공 및 환경 설계는 사용자가 담당하였으며, 실제 코드 구현 및 최적화는 **antigravity**에 의해 수행되었습니다.

---

## 📋 Requirements

* **Language:** Python 3.x
* **Libraries:** * `gitpython` (GitHub 자동 연동을 위해 필요: `pip install gitpython`)
    * `ast`, `os` (내장 모듈)
* **Environment:** macOS (Recommended)

---

## 🚀 How to Run

1.  **Repository Clone & Library Install**
    ```bash
    git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
    pip install gitpython
    ```
2.  **Run Program**
    ```bash
    python main.py
    ```
3.  **Select File:** 터미널에 표시되는 목록에서 분석할 파일의 번호를 입력하세요.

---

## 📂 Project Structure

* `main.py`: 분석 및 Git 자동화 핵심 로직
* `.gitignore`: 불필요한 메타데이터 및 캐시 파일 업로드 방지
* `README.md`: 프로젝트 명세서 (현재 파일)

---

### 📝 Future Roadmap
* 재귀 함수 감지 알고리즘 고도화
* 파이썬 내장 함수(예: `sort()`)의 시간 복잡도 데이터베이스 연결
* 분석 결과를 시각화된 리포트로 생성하는 기능 추가
