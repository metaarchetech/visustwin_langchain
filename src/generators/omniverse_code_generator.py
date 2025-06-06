"""
Omniverse Python 代碼生成器
專門生成可執行的 Omniverse Python 腳本
"""

from langchain_groq import ChatGroq
from langchain.prompts import ChatPromptTemplate, PromptTemplate
from langchain.schema.runnable import Runnable
from langchain.schema.output_parser import StrOutputParser
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.config.groq_config import engine_config
import json
import traceback
import sys
import io
from contextlib import redirect_stdout, redirect_stderr

# 模擬 Omniverse 模組（若未安裝）
try:
    import omni.usd
    import omni.kit.commands
    OMNIVERSE_AVAILABLE = True
except ImportError:
    OMNIVERSE_AVAILABLE = False
    print("注意：Omniverse 模組未安裝，將運行在模擬模式")


class OmniverseCodeGenerator:
    """Omniverse Python 代碼生成與執行器"""
    
    def __init__(self):
        self.chain = self._create_code_generation_chain()
        self.execution_context = self._setup_execution_context()
    
    def _create_code_generation_chain(self) -> Runnable:
        """創建代碼生成鏈"""
        
        # 根據當前引擎選擇合適的提示模板
        if engine_config.get_current_engine() == "groq":
            # Groq 使用 ChatPromptTemplate
            prompt = ChatPromptTemplate.from_messages([
                ("system", """您是 Omniverse Python 代碼生成專家，專門撰寫高品質的 Omniverse Python 腳本。

請基於以下 Omniverse API 知識庫生成 Python 代碼：

## 核心 API 參考：

### USD 操作
```python
import omni.usd
from pxr import Usd, UsdGeom, Sdf, Gf

# 獲取當前 Stage
stage = omni.usd.get_context().get_stage()

# 創建原始物件
cube_prim = UsdGeom.Cube.Define(stage, "/World/MyCube")
sphere_prim = UsdGeom.Sphere.Define(stage, "/World/MySphere")

# 設置變換
xform = UsdGeom.Xformable(cube_prim)
xform.AddTranslateOp().Set(Gf.Vec3d(1.0, 2.0, 3.0))
xform.AddRotateXYZOp().Set(Gf.Vec3f(0, 45, 0))
xform.AddScaleOp().Set(Gf.Vec3f(2.0, 2.0, 2.0))
```

### Kit Commands
```python
import omni.kit.commands

# 創建物件
omni.kit.commands.execute('CreatePrimWithDefaultXform',
    prim_type='Cube',
    prim_path='/World/NewCube',
    attributes={'size': 2.0}
)

# 刪除物件
omni.kit.commands.execute('DeletePrims', paths=['/World/OldCube'])

# 移動物件
omni.kit.commands.execute('TransformPrimCommand',
    path='/World/MyCube',
    new_transform_matrix=[[2,0,0,5], [0,2,0,10], [0,0,2,15], [0,0,0,1]]
)
```

### 材質和渲染
```python
import omni.kit.commands
from pxr import UsdShade

# 創建材質
omni.kit.commands.execute('CreateAndBindMdlMaterialFromLibrary',
    mdl_name='OmniGlass.mdl',
    mtl_name='OmniGlass',
    mtl_path='/World/Looks/Glass'
)

# 綁定材質到物件
omni.kit.commands.execute('BindMaterial',
    prim_path='/World/MyCube',
    material_path='/World/Looks/Glass'
)
```

### 動畫和時間軸
```python
import omni.timeline
from pxr import Usd

# 設置動畫關鍵幀
stage = omni.usd.get_context().get_stage()
cube_prim = stage.GetPrimAtPath("/World/MyCube")
translate_attr = cube_prim.GetAttribute("xformOp:translate")

# 在第 0 幀設置位置
translate_attr.Set(Gf.Vec3d(0, 0, 0), Usd.TimeCode(0))
# 在第 60 幀設置位置
translate_attr.Set(Gf.Vec3d(10, 0, 0), Usd.TimeCode(60))
```

## 代碼生成要求：

1. **完整性**：包含所有必要的 import 語句
2. **錯誤處理**：添加適當的 try/except 包圍
3. **註釋說明**：為主要操作添加中文註釋
4. **可執行性**：確保代碼可以直接在 Omniverse 中執行
5. **最佳實踐**：遵循 Omniverse 開發規範

請生成完整的 Python 代碼，格式如下：

```python
# 您生成的代碼
```"""),
                ("human", "用戶需求：{request}")
            ])
        else:
            # Ollama 使用 PromptTemplate
            prompt = PromptTemplate.from_template(
                """您是 Omniverse Python 代碼生成專家，專門撰寫高品質的 Omniverse Python 腳本。

用戶需求：{request}

請基於以下 Omniverse API 知識庫生成 Python 代碼：

## 核心 API 參考：

### USD 操作
```python
import omni.usd
from pxr import Usd, UsdGeom, Sdf, Gf

# 獲取當前 Stage
stage = omni.usd.get_context().get_stage()

# 創建原始物件
cube_prim = UsdGeom.Cube.Define(stage, "/World/MyCube")
sphere_prim = UsdGeom.Sphere.Define(stage, "/World/MySphere")

# 設置變換
xform = UsdGeom.Xformable(cube_prim)
xform.AddTranslateOp().Set(Gf.Vec3d(1.0, 2.0, 3.0))
xform.AddRotateXYZOp().Set(Gf.Vec3f(0, 45, 0))
xform.AddScaleOp().Set(Gf.Vec3f(2.0, 2.0, 2.0))
```

### Kit Commands
```python
import omni.kit.commands

# 創建物件
omni.kit.commands.execute('CreatePrimWithDefaultXform',
    prim_type='Cube',
    prim_path='/World/NewCube',
    attributes={'size': 2.0}
)

# 刪除物件
omni.kit.commands.execute('DeletePrims', paths=['/World/OldCube'])

# 移動物件
omni.kit.commands.execute('TransformPrimCommand',
    path='/World/MyCube',
    new_transform_matrix=[[2,0,0,5], [0,2,0,10], [0,0,2,15], [0,0,0,1]]
)
```

### 材質和渲染
```python
import omni.kit.commands
from pxr import UsdShade

# 創建材質
omni.kit.commands.execute('CreateAndBindMdlMaterialFromLibrary',
    mdl_name='OmniGlass.mdl',
    mtl_name='OmniGlass',
    mtl_path='/World/Looks/Glass'
)

# 綁定材質到物件
omni.kit.commands.execute('BindMaterial',
    prim_path='/World/MyCube',
    material_path='/World/Looks/Glass'
)
```

### 動畫和時間軸
```python
import omni.timeline
from pxr import Usd

# 設置動畫關鍵幀
stage = omni.usd.get_context().get_stage()
cube_prim = stage.GetPrimAtPath("/World/MyCube")
translate_attr = cube_prim.GetAttribute("xformOp:translate")

# 在第 0 幀設置位置
translate_attr.Set(Gf.Vec3d(0, 0, 0), Usd.TimeCode(0))
# 在第 60 幀設置位置
translate_attr.Set(Gf.Vec3d(10, 0, 0), Usd.TimeCode(60))
```

## 代碼生成要求：

1. **完整性**：包含所有必要的 import 語句
2. **錯誤處理**：添加適當的 try/except 包圍
3. **註釋說明**：為主要操作添加中文註釋
4. **可執行性**：確保代碼可以直接在 Omniverse 中執行
5. **最佳實踐**：遵循 Omniverse 開發規範

請生成完整的 Python 代碼，格式如下：

```python
# 您生成的代碼
```

生成的代碼："""
            )
        
        # 使用統一引擎配置創建模型實例
        model = engine_config.create_model_instance(
            task_type="code",
            temperature=0.3,  # 較低溫度以提高代碼準確性
            max_tokens=2000   # 更長的輸出以支援複雜代碼
        )
        
        parser = StrOutputParser()
        
        return prompt | model | parser
    
    def _setup_execution_context(self):
        """設置代碼執行上下文"""
        return {
            'omni': None,
            'stage': None,
            'context': None,
            'imported_modules': set()
        }
    
    def generate_code(self, user_request: str) -> dict:
        """生成 Omniverse Python 代碼"""
        try:
            # 調用 AI 生成代碼
            raw_response = self.chain.invoke({"request": user_request})
            
            # 提取代碼塊
            code = self._extract_code_block(raw_response)
            
            return {
                "status": "success",
                "code": code,
                "raw_response": raw_response,
                "explanation": self._extract_explanation(raw_response)
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def execute_code(self, code: str, safe_mode: bool = True) -> dict:
        """執行生成的代碼"""
        try:
            # 準備執行環境
            execution_globals = self._prepare_execution_environment()
            
            # 捕獲輸出
            stdout_capture = io.StringIO()
            stderr_capture = io.StringIO()
            
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                if safe_mode:
                    # 安全模式：檢查危險操作
                    if self._check_code_safety(code):
                        exec(code, execution_globals)
                    else:
                        raise ValueError("代碼包含潛在危險操作")
                else:
                    # 直接執行
                    exec(code, execution_globals)
            
            return {
                "status": "success",
                "stdout": stdout_capture.getvalue(),
                "stderr": stderr_capture.getvalue(),
                "execution_globals": {k: str(v) for k, v in execution_globals.items() 
                                    if not k.startswith('_')}
            }
            
        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }
    
    def _extract_code_block(self, response: str) -> str:
        """從響應中提取代碼塊"""
        lines = response.split('\n')
        code_lines = []
        in_code_block = False
        
        for line in lines:
            if line.strip().startswith('```python'):
                in_code_block = True
                continue
            elif line.strip() == '```' and in_code_block:
                in_code_block = False
                break
            elif in_code_block:
                code_lines.append(line)
        
        return '\n'.join(code_lines) if code_lines else response
    
    def _extract_explanation(self, response: str) -> str:
        """提取代碼說明"""
        # 簡單的說明提取邏輯
        lines = response.split('\n')
        explanation_lines = []
        
        for line in lines:
            if not line.strip().startswith('```') and '```' not in line:
                explanation_lines.append(line)
            elif '```python' in line:
                break
        
        return '\n'.join(explanation_lines).strip()
    
    def _prepare_execution_environment(self) -> dict:
        """準備代碼執行環境"""
        try:
            import omni.usd
            import omni.kit.commands
            from pxr import Usd, UsdGeom, Sdf, Gf, UsdShade
            import omni.timeline
            
            return {
                'omni': omni,
                'Usd': Usd,
                'UsdGeom': UsdGeom,
                'Sdf': Sdf,
                'Gf': Gf,
                'UsdShade': UsdShade,
                'stage': omni.usd.get_context().get_stage() if hasattr(omni.usd, 'get_context') else None,
                'print': print,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict
            }
        except ImportError:
            # 在非 Omniverse 環境中的模擬環境
            return {
                'print': print,
                'len': len,
                'str': str,
                'int': int,
                'float': float,
                'list': list,
                'dict': dict
            }
    
    def _check_code_safety(self, code: str) -> bool:
        """檢查代碼安全性"""
        dangerous_patterns = [
            'import os',
            'import sys',
            'import subprocess',
            'exec(',
            'eval(',
            'open(',
            'file(',
            '__import__',
            'globals(',
            'locals(',
            'dir(',
            'delattr',
            'setattr',
            'getattr'
        ]
        
        code_lower = code.lower()
        for pattern in dangerous_patterns:
            if pattern in code_lower:
                return False
        
        return True


# 創建全局實例
omniverse_code_gen = OmniverseCodeGenerator() 