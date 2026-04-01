import ast

class ComplexityVisitor(ast.NodeVisitor):
    def __init__(self):
        self.max_depth = 0
        self.current_depth = 0
        self.has_recursion = False

    def visit_FunctionDef(self, node):
        func_name = node.name
        
        # 함수 바디 안에서 자기 자신을 호출(Call)하는지 검사
        for child in ast.walk(node):
            if isinstance(child, ast.Call) and isinstance(child.func, ast.Name):
                if child.func.id == func_name:
                    self.has_recursion = True
                    break
        
        # 내부 구조(루프 등)도 계속 방문
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
    """
    파일의 코드를 AST로 파싱하여 재귀 및 루프 중첩 결과를 반환합니다.
    """
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
    
    depth = visitor.max_depth
    has_recursion = visitor.has_recursion
    
    # 복잡도 판별 로직
    if has_recursion:
        complexity = "O(2^n) (재귀 호출)"
    elif depth == 0:
        complexity = "O(1)"
    elif depth == 1:
        complexity = "O(n)"
    else:
        complexity = f"O(n^{depth})"
        
    return {
        "depth": depth,
        "has_recursion": has_recursion,
        "complexity": complexity
    }
