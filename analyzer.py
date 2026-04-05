import ast

class Complexity:
    def __init__(self, n_power=0, has_log=False, is_exp=False):
        self.n_power = n_power
        self.has_log = has_log
        self.is_exp = is_exp

    def __repr__(self):
        if self.is_exp:
            return "O(2^n)"
        if self.n_power == 0:
            return "O(log n)" if self.has_log else "O(1)"
        
        n_str = "n" if self.n_power == 1 else f"n^{self.n_power}"
        log_str = " log n" if self.has_log else ""
        return f"O({n_str}{log_str})"

    def __str__(self):
        return repr(self)

    def copy(self):
        return Complexity(self.n_power, self.has_log, self.is_exp)

    def __lt__(self, other):
        return (self.is_exp, self.n_power, self.has_log) < (other.is_exp, other.n_power, other.has_log)
    
    def __eq__(self, other):
        return (self.is_exp, self.n_power, self.has_log) == (other.is_exp, other.n_power, other.has_log)

    def __mul__(self, other):
        return Complexity(self.n_power + other.n_power, self.has_log or other.has_log, self.is_exp or other.is_exp)

O_1_METHODS = {'append', 'pop', 'add', 'discard', 'get', 'keys', 'values', 'items'}
O_1_FUNCS = {'len'}

O_N_METHODS = {'index', 'insert', 'remove', 'copy', 'clear', 'count', 'replace', 'split', 'join', 'find', 'startswith', 'endswith'}
O_N_FUNCS = {'min', 'max', 'sum'}

O_N_LOG_N_METHODS = {'sort'}
O_N_LOG_N_FUNCS = {'sorted'}



class ScopeAnalyzer(ast.NodeVisitor):
    def __init__(self, func_complexities, current_func_name):
        self.func_complexities = func_complexities
        self.current_func_name = current_func_name
        self.reasons = []
        self.comp = Complexity()

    def add_reason(self, reason):
        if reason not in self.reasons:
            self.reasons.append(reason)

    def visit_sequence(self, visitor, seq):
        if not seq: return
        for st in seq:
            visitor.visit(st)

    def visit_For(self, node):
        inner_visitor = ScopeAnalyzer(self.func_complexities, self.current_func_name)
        self.visit_sequence(inner_visitor, node.body)
        
        loop_multiplier = Complexity(n_power=1)
        self.comp = max(self.comp, inner_visitor.comp * loop_multiplier)
        self.add_reason("루프(For/While/Comprehension) 선형 계층 감지 -> 내용물에 O(n) 곱셈")
        for r in inner_visitor.reasons:
            self.add_reason(r)
        
        self.visit_sequence(inner_visitor, node.orelse)


    visit_While = visit_For
    visit_AsyncFor = visit_For

    # Comprehensions don't have .body, they have .elt and .generators.
    def visit_ListComp(self, node):
        inner_visitor = ScopeAnalyzer(self.func_complexities, self.current_func_name)
        inner_visitor.visit(node.elt)
        
        # Each generator adds an O(n)
        for gen in node.generators:
            self.comp = max(self.comp, inner_visitor.comp * Complexity(n_power=1))
            self.add_reason("Comprehension 계층 감지 -> 단일 O(n) 곱셈")
            inner_visitor.visit(gen.iter)
            inner_visitor.visit(gen.ifs)
            
        for r in inner_visitor.reasons:
            self.add_reason(r)

    visit_SetComp = visit_ListComp
    visit_DictComp = visit_ListComp
    visit_GeneratorExp = visit_ListComp

    def visit_Call(self, node):
        func = node.func
        called_name = None
        if isinstance(func, ast.Name):
            called_name = func.id
        elif isinstance(func, ast.Attribute):
            called_name = func.attr
            
        if called_name in O_N_FUNCS or called_name in O_N_METHODS:
            self.comp = max(self.comp, Complexity(n_power=1))
            self.add_reason(f"'{called_name}()' 내장 함수/메소드 사용 (O(n))")
        elif called_name in O_N_LOG_N_FUNCS or called_name in O_N_LOG_N_METHODS:
            self.comp = max(self.comp, Complexity(n_power=1, has_log=True))
            self.add_reason(f"'{called_name}()' 정렬 내장 함수/메소드 사용 (O(n log n))")
        elif called_name in O_1_FUNCS or called_name in O_1_METHODS:
            self.comp = max(self.comp, Complexity())
            self.add_reason(f"'{called_name}()' 내장 함수/메소드 사용 (O(1))")
        elif called_name == self.current_func_name and self.current_func_name is not None:
             self.comp = max(self.comp, Complexity(is_exp=True))
             self.add_reason(f"자기 자신('{self.current_func_name}')의 재귀 호출 감지 -> 재귀(최악의 경우 O(2^n) 가정)")
        elif called_name in self.func_complexities:
             target_comp = self.func_complexities[called_name]
             self.comp = max(self.comp, target_comp)
             self.add_reason(f"파일 내 커스텀 함수 '{called_name}()' 호출 (목표: {target_comp})")
             
        self.generic_visit(node)

    def visit_Compare(self, node):
        if any(isinstance(op, ast.In) for op in node.ops):
             self.comp = max(self.comp, Complexity(n_power=1))
             self.add_reason("'in' 연산자(탐색) 사용 (리스트 탐색 가정 O(n))")
             
        self.generic_visit(node)


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

    functions = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            functions[node.name] = node

    func_complexities = {name: Complexity() for name in functions}
    func_reasons = {name: [] for name in functions}
    
    for _ in range(3):
        updated = False
        for name, node in functions.items():
            analyzer = ScopeAnalyzer(func_complexities, name)
            # Visit body contents directly to prevent generic_visit from double processing if we redefined things
            for n in node.body:
                analyzer.visit(n)
                
            if analyzer.comp > func_complexities[name]:
                func_complexities[name] = analyzer.comp
                func_reasons[name] = analyzer.reasons
                updated = True
        if not updated:
            break
            
    final_analyzer = ScopeAnalyzer(func_complexities, None)
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            final_analyzer.visit(node)
            
    final_comp = final_analyzer.comp
    final_reasons = final_analyzer.reasons
    
    if final_comp == Complexity() and functions:
        max_func_comp = Complexity()
        for name, comp in func_complexities.items():
             max_func_comp = max(max_func_comp, comp)
             for r in func_reasons[name]:
                 if r not in final_reasons:
                     final_reasons.append(f"[{name}] " + r)
        final_comp = max_func_comp

    if final_comp == Complexity() and not final_reasons:
        final_reasons.append("단순 상수 시간 O(1) 구조 (루프, 정렬, 무거운 내장함수 없음)")

    return {
        "complexity": str(final_comp),
        "reasons": final_reasons
    }
