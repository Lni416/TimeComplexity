import ast

class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.max_depth = 0
        self.current_depth = 0
        self.func_recur_info = {} # func_name -> {'count': 0, 'halves': False}
        self.has_log_n_loop = False
        self.has_n_log_n_sort = False
        self.reasons = []

    def visit_FunctionDef(self, node):
        func_name = node.name
        self.func_recur_info[func_name] = {'count': 0, 'halves': False}

        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name) and child.func.id == 'sorted':
                    self.has_n_log_n_sort = True
                    if "정렬 함수(sorted()) 사용" not in self.reasons:
                        self.reasons.append("정렬 함수(sorted()) 사용")
                elif isinstance(child.func, ast.Attribute) and child.func.attr == 'sort':
                    self.has_n_log_n_sort = True
                    if "정렬 함수(.sort()) 사용" not in self.reasons:
                        self.reasons.append("정렬 함수(.sort()) 사용")

                if isinstance(child.func, ast.Name) and child.func.id == func_name:
                    self.func_recur_info[func_name]['count'] += 1
                    for arg in child.args:
                        if isinstance(arg, ast.BinOp) and isinstance(arg.op, (ast.Div, ast.FloorDiv)):
                            if isinstance(arg.right, ast.Constant) and arg.right.value == 2:
                                self.func_recur_info[func_name]['halves'] = True
                        elif isinstance(arg, ast.Constant) and isinstance(arg.value, int):
                            pass

            elif isinstance(child, ast.AugAssign):
                if isinstance(child.op, (ast.Mult, ast.Div, ast.FloorDiv)):
                    if isinstance(child.value, ast.Constant) and child.value.value == 2:
                        self.has_log_n_loop = True
                        if "루프 변수의 기하급수적 증감(i *= 2 등) 감지" not in self.reasons:
                            self.reasons.append("루프 변수의 기하급수적 증감(i *= 2 등) 감지")
                            
        self.generic_visit(node)

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

def analyze_code(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
    except Exception as e:
        return {"error": f"파일을 읽는 도중 오류가 발생했습니다:\n{e}", "type": "IOError"}

    try:
        tree = ast.parse(source)
    except SyntaxError as e:
        return {"error": f"선택한 파일에 파이썬 문법 오류(Syntax Error)가 있습니다:\n{e}", "type": "SyntaxError"}

    visitor = ComplexityVisitor()
    visitor.visit(tree)
    
    reasons = visitor.reasons.copy()
    depth = visitor.max_depth
    
    is_exp = False
    for info in visitor.func_recur_info.values():
        if info['count'] >= 2 and not info['halves']:
            is_exp = True
            if "동일 함수 2번 이상 재귀 호출 (O(2^n) 패턴)" not in reasons:
                reasons.append("동일 함수 2번 이상 재귀 호출 (O(2^n) 패턴)")
            break

    is_n_log_n = visitor.has_n_log_n_sort
    for info in visitor.func_recur_info.values():
        if info['count'] >= 2 and info['halves']:
            is_n_log_n = True
            if "데이터가 절반으로 나뉘는 분할 정복 형태 (O(n log n) 패턴)" not in reasons:
                reasons.append("데이터가 절반으로 나뉘는 분할 정복 형태 (O(n log n) 패턴)")

    is_log_n = visitor.has_log_n_loop
    for info in visitor.func_recur_info.values():
        if info['count'] == 1 and info['halves']:
            is_log_n = True
            if "이진 탐색 형태의 단일 재귀 호출 (O(log n) 패턴)" not in reasons:
                reasons.append("이진 탐색 형태의 단일 재귀 호출 (O(log n) 패턴)")

    # 최종 복잡도 판단 (내림차순)
    if is_exp:
        complexity = "O(2^n)"
    elif depth >= 2:
        complexity = f"O(n^{depth})"
        reasons.append(f"{depth}중 루프 감지")
    elif is_n_log_n:
        complexity = "O(n log n)"
    elif depth == 1:
        complexity = "O(n)"
        reasons.append("단일 루프 감지")
    elif is_log_n:
        complexity = "O(log n)"
    else:
        # 단일 호출이고 데이터를 반으로 쪼개지 않는다면 O(n) 취급
        if any((info['count'] >= 1 and not info['halves']) for info in visitor.func_recur_info.values()):
            complexity = "O(n)"
            reasons.append("단일 선형 재귀 호출 감지")
        else:
            complexity = "O(1)"
            reasons.append("지연 로직 없이 단순 상수 시간 연산")

    return {
        "complexity": complexity,
        "reasons": reasons
    }
