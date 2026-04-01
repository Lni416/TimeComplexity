import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from analyzer import analyze_code

class ComplexityAnalyzerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("파이썬 시간 복잡도 분석기")
        self.root.geometry("500x440")
        self.root.configure(bg="#F8F9FA")
        self.root.resizable(False, False)
        
        # macOS 창 띄움 안정화
        self.root.call('wm', 'attributes', '.', '-topmost', True)
        self.root.after(500, lambda: self.root.call('wm', 'attributes', '.', '-topmost', False))

        self.selected_file_path = None
        
        # 스타일 설정 (ttk)
        style = ttk.Style()
        style.theme_use('aqua' if root.tk.call('tk', 'windowingsystem') == 'aqua' else 'clam')
        style.configure("TButton", font=("Helvetica", 14), padding=8)
        
        # 메인 컨테이너
        container = tk.Frame(root, bg="#F8F9FA")
        container.pack(fill=tk.BOTH, expand=True, padx=30, pady=25)
        
        # 제목
        self.title_label = tk.Label(container, text="정적 분석 기반\n시간 복잡도 측정", font=("Helvetica", 20, "bold"), bg="#F8F9FA", fg="#212529", justify="center")
        self.title_label.pack(pady=(0, 20))
        
        # 카드 프레임 (파일 선택 영역)
        card = tk.Frame(container, bg="white", highlightbackground="#E9ECEF", highlightthickness=1, bd=0)
        card.pack(fill=tk.X, pady=10)
        
        self.file_label = tk.Label(card, text="선택된 파일이 없습니다.", fg="#6C757D", bg="white", font=("Helvetica", 13))
        self.file_label.pack(pady=20, padx=10)
        
        # 버튼 영역
        self.select_btn = ttk.Button(container, text="📂 파이썬 파일(.py) 찾기", command=self.select_file)
        self.select_btn.pack(fill=tk.X, pady=(10, 5))
        
        self.analyze_btn = ttk.Button(container, text="🧠 분석 시작", command=self.analyze_complexity, state=tk.DISABLED)
        self.analyze_btn.pack(fill=tk.X, pady=5)
        
        # 결과 표시 프레임
        self.result_frame = tk.Frame(container, bg="#E8F4F8", highlightbackground="#B6EFFB", highlightthickness=1, bd=0)
        self.result_frame.pack(fill=tk.X, pady=15)
        self.result_frame.pack_forget() # 처음엔 숨김
        
        self.result_label = tk.Label(self.result_frame, text="", font=("Helvetica", 14, "bold"), bg="#E8F4F8", fg="#055160", justify="center")
        self.result_label.pack(pady=15)
        
    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="분석할 파이썬 파일 선택",
            filetypes=[("Python Files", "*.py"), ("All Files", "*.*")],
            initialdir=os.getcwd()
        )
        
        if file_path:
            self.selected_file_path = file_path
            short_name = os.path.basename(file_path)
            self.file_label.config(text=f"📄 {short_name}", fg="#212529", font=("Helvetica", 14, "bold"))
            
            # 버튼 활성화 및 결과 숨김
            self.analyze_btn.config(state=tk.NORMAL)
            self.result_frame.pack_forget()
            
    def analyze_complexity(self):
        if not self.selected_file_path:
            return
            
        # 별도 모듈로 분리된 분석 로직 실행
        result = analyze_code(self.selected_file_path)
        
        # 에러 핸들링
        if "error" in result:
            title = "구문 오류" if result.get("type") == "SyntaxError" else "오류"
            messagebox.showerror(title, result["error"])
            return
            
        depth = result.get("depth", 0)
        has_recursion = result.get("has_recursion", False)
        complexity = result.get("complexity", "O(1)")
            
        result_text = f"루프 중첩 깊이: {depth}\n재귀 스택 감지: {'예' if has_recursion else '아니오'}\n\n⏱ 분석된 복잡도: {complexity}"
        self.result_label.config(text=result_text)
        self.result_frame.pack(fill=tk.X, pady=15)

if __name__ == "__main__":
    # GUI 앱 실행
    root = tk.Tk()
    app = ComplexityAnalyzerApp(root)
    root.mainloop()
