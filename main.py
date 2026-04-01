import os
import ast
import sys

try:
    import git
except ImportError:
    git = None

class LoopDepthVisitor(ast.NodeVisitor):
    def __init__(self):
        self.max_depth = 0
        self.current_depth = 0

    def visit_For(self, node):
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

    def visit_While(self, node):
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1
        
    def visit_AsyncFor(self, node):
        self.current_depth += 1
        self.max_depth = max(self.max_depth, self.current_depth)
        self.generic_visit(node)
        self.current_depth -= 1

def create_gitignore():
    """1. .gitignore 자동 생성"""
    ignore_path = '.gitignore'
    ignore_content = """# PyCharm settings
.idea/

# Python cache
__pycache__/
*.py[cod]

# Virtual environments
venv/
.venv/

# macOS system files
.DS_Store

# Logs and temp files
*.log
tmp/
.temp/
"""
    if not os.path.exists(ignore_path):
        with open(ignore_path, 'w', encoding='utf-8') as f:
            f.write(ignore_content)
        print("[환경 설정] .gitignore 파일을 자동으로 생성했습니다.")
    else:
        print("[환경 설정] .gitignore 파일이 이미 존재합니다.")

def sync_with_git():
    """3. Git 자동화 (.py 및 .gitignore 파일만 커밋/푸시)"""
    if git is None:
        print("[Git 자동화] GitPython 모듈이 설치되지 않아 동기화를 건너뜁니다. (설치 요망: pip install gitpython)")
        return

    try:
        repo = git.Repo(os.getcwd())
    except git.exc.InvalidGitRepositoryError:
        print("[Git 자동화] 현재 디렉토리가 Git 저장소가 아닙니다. (git init 필요)")
        return

    try:
        # 변경된 파일 목록 조회 (untracked + modified)
        changed = [item.a_path for item in repo.index.diff(None)] + repo.untracked_files
        
        staged = [item.a_path for item in repo.index.diff("HEAD")] if repo.head.is_valid() else []
        all_changed = set(changed + staged)
        
        # 소스 코드(.py)와 .gitignore 파일만 필터링 (결과 로그 등 제외)
        files_to_commit = [f for f in all_changed if f.endswith('.py') or f == '.gitignore']
        
        if not files_to_commit:
            print("[Git 자동화] 변경된 소스 코드나 설정 파일이 없어 동기화를 생략합니다.")
            return
            
        for file in files_to_commit:
            repo.git.add(file)
            
        repo.index.commit("feat: update analyzer logic and sync source code")
        print(f"[Git 자동화] 변경사항 커밋 완료: {', '.join(files_to_commit)}")
        
        origin = repo.remote(name='origin')
        origin.push()
        print("[Git 자동화] GitHub로 소스 코드를 성공적으로 푸시했습니다.")
    except ValueError:
        print("[Git 자동화] 리모트 서버(origin)가 설정되지 않아 푸시를 건너뜁니다.")
    except Exception as e:
        print(f"[Git 자동화] Git 작업 중 오류 발생: {e}")

def select_python_file():
    """2. 파이썬 파일 선택"""
    py_files = [f for f in os.listdir('.') if f.endswith('.py') and os.path.isfile(f)]
    if not py_files:
        print("[오류] 분석할 파이썬(.py) 파일이 현재 디렉토리에 없습니다.")
        sys.exit(1)
        
    print("\n[현재 파일 목록]")
    for i, file_name in enumerate(py_files, start=1):
        print(f"{i}. {file_name}")
        
    while True:
        try:
            choice = int(input("\n분석할 파일 번호를 입력하세요: "))
            if 1 <= choice <= len(py_files):
                return py_files[choice - 1]
            else:
                print(f"1부터 {len(py_files)} 사이의 유효한 번호를 입력하세요.")
        except ValueError:
            print("숫자 형식으로 입력해주세요.")

def analyze_complexity(filepath):
    """2. AST 기반 시간 복잡도 추론 로직"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
    except Exception as e:
        print(f"[오류] 파일 읽기 실패: {e}")
        return

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        print(f"[오류] 파이썬 문법 오류로 파싱 불가능: {e}")
        return

    visitor = LoopDepthVisitor()
    visitor.visit(tree)
    
    depth = visitor.max_depth
    if depth == 0:
        complexity = "O(1)"
    elif depth == 1:
        complexity = "O(n)"
    else:
        complexity = f"O(n^{depth})"

    print("\n====== 시간 복잡도 분석 결과 ======")
    print(f"📄 파일명: {filepath}")
    print(f"🔄 최대 루프 중첩 깊이: {depth}")
    print(f"⏱ 추론된 복잡도: {complexity}")
    print("===================================\n")

if __name__ == "__main__":
    print(">>> 시스템 점검 시작")
    create_gitignore()
    sync_with_git()
    
    print("\n>>> 정적 코드 분석기 실행")
    target_file = select_python_file()
    analyze_complexity(target_file)
