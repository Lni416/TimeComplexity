import os
import ast
import tkinter as tk
from tkinter import filedialog, messagebox

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

class ComplexityAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("파이썬 시간 복잡도 분석기")
        self.root.geometry("450x350")
        
        # macOS 창 띄움 안정화: 초기 실행 시 최상단 고정 후 해제
        self.root.call('wm', 'attributes', '.', '-topmost', True)
        self.root.after(500, lambda: self.root.call('wm', 'attributes', '.', '-topmost', False))

        self.selected_file_path = None
        
        # UI 구성요소
        self.title_label = tk.Label(root, text="정적 분석 기반 시간 복잡도 측정", font=("Helvetica", 16, "bold"))
        self.title_label.pack(pady=20)
        
        self.select_btn = tk.Button(root, text="파이썬 파일(.py) 선택", command=self.select_file, width=20, height=2)
        self.select_btn.pack(pady=10)
        
        self.file_label = tk.Label(root, text="선택된 파일: 없음", fg="gray", font=("Helvetica", 12))
        self.file_label.pack(pady=5)
        
        self.analyze_btn = tk.Button(root, text="분석하기", command=self.analyze_complexity, width=20, height=2, state=tk.DISABLED)
        self.analyze_btn.pack(pady=10)
        
        self.result_label = tk.Label(root, text="", font=("Helvetica", 14), fg="blue")
        self.result_label.pack(pady=20)
        
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="분석할 파이썬 파일 선택",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")],
            initialdir=os.getcwd()
        )
        
        if file_path:
            self.selected_file_path = file_path
            short_name = os.path.basename(file_path)
            self.file_label.config(text=f"선택된 파일: {short_name}", fg="black")
            
            # 파일이 선택되면 분석 버튼 활성화
            self.analyze_btn.config(state=tk.NORMAL)
            self.result_label.config(text="") # 이전 결과 초기화
            
    def analyze_complexity(self):
        if not self.selected_file_path:
            return
            
        try:
            with open(self.selected_file_path, 'r', encoding='utf-8') as f:
                source = f.read()
        except Exception as e:
            messagebox.showerror("오류", f"파일을 읽는 도중 오류가 발생했습니다:\n{e}")
            return

        try:
            tree = ast.parse(source)
        except SyntaxError as e:
            messagebox.showerror("구문 오류", f"선택한 파일에 파이썬 문법 오류(Syntax Error)가 있습니다:\n{e}")
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
            
        result_text = f"🔄 최대 루프 중첩 깊이: {depth}\n⏱ 시간 복잡도: {complexity}"
        self.result_label.config(text=result_text)

if __name__ == "__main__":
    create_gitignore()
    
    # GUI 앱 실행
    root = tk.Tk()
    app = ComplexityAnalyzerApp(root)
    root.mainloop()
