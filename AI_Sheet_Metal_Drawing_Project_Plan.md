# AI 辅助钣金拆图与加工图自动生成系统项目计划书

## 当前本地服务地址

当前 Streamlit 本地访问地址：

```text
http://localhost:8506
```

当前推荐启动命令：

```bash
.venv/bin/streamlit run src/streamlit_app.py --server.port 8506
```

端口维护规则：

- 每次修改 Streamlit 本地端口后，必须同步更新本节地址和启动命令。
- 每次端口变更或确认后，应在 `## 当前进度` 中记录变更日期、端口号和验证情况。
- 如果端口被占用导致临时改用其他端口，应优先更新本节，避免后续开发和演示时不清楚实际访问地址。

---

## 1. 项目概述

### 1.1 项目名称

AI 辅助钣金拆图与加工图自动生成系统

### 1.2 项目定位

本项目旨在开发一个面向钣金加工场景的 AI 辅助系统，用于帮助工程师从客户提供的 PDF 工程图、复杂三维工程图或三维设计图中提取尺寸、结构、孔位、折弯线、视图关系和工艺信息，并生成可审核、可修改、可导出的钣金 CAD 拆图初稿。

本项目不以第一阶段实现完全无人化为目标，而是采用以下路线：

```text
AI 辅助 + CAD 自动化 + 工程师审核
```

项目强调工程可控性。AI 负责辅助识别、整理、生成结构化 JSON 和提出候选拆图方案；CAD/几何程序负责可验证的尺寸计算、展开计算、制造约束校验和图纸输出；工程师负责最终审核、修改和确认。

本项目当前交付重点是“可编辑 CAD 拆图初稿”，不是直接生成可上机切割的最终生产文件。激光切割、设备参数、排版套料和上机工艺属于用户或工厂既有生产流程，当前阶段只需要保证输出 CAD/DXF 便于工程师继续检查和修改。

### 1.3 核心原则

第一阶段目标不是直接从 PDF 自动生成完美加工图，而是先完成以下技术闭环：

```text
JSON 参数 -> Python 计算 -> DXF 输出
```

该闭环跑通后，再逐步扩展到 PDF / 三维工程图解析、Web 界面、多类型板件、折弯与开孔组合模板、箱体和电缆盒类产品、多零件拆分优化、Windows 工业软件兼容和真实工厂工作流。

---

## 2. 项目背景与痛点

### 2.1 项目背景

在钣金代加工流程中，客户通常会提供 PDF 格式的产品工程图。图纸中可能包含多个 3D 工程图视角、局部截面图、尺寸标注、孔位标注、焊接说明、表面处理说明和材料要求。

传统流程通常包括：

1. 工程师阅读客户 PDF 图纸。
2. 人工理解产品结构和加工要求。
3. 使用 AutoCAD 等工具手绘拆分后的板件图。
4. 根据经验预留折弯、焊接、打磨、喷漆等加工尺寸。
5. 输出 CAD 加工图并提交给生产人员。
6. 工人进行激光切割、折弯、焊接、打磨和喷漆。

该流程对工程师经验依赖强，重复劳动多，且容易在尺寸转录、展开计算和图纸绘制过程中产生错误。

### 2.2 主要痛点

| 痛点 | 说明 | 对项目的启发 |
| --- | --- | --- |
| PDF / 三维工程图信息分散 | 尺寸、视图、截面、结构和备注分布在不同区域 | 需要图纸解析、视图关系理解和结构化数据抽取 |
| 人工拆图耗时 | 工程师需要从零绘制加工图 | 需要 CAD 自动生成初稿 |
| 大型钣金产品无法一体加工 | 例如电缆盒展开尺寸可能超过板材或设备加工范围 | 需要自动拆件、生产约束校验和候选方案评分 |
| 展开计算依赖经验 | 折弯展开与材料、厚度、设备参数有关 | 需要参数化计算和可配置公式 |
| 工艺预留难标准化 | 焊接、打磨、喷漆预留受工厂经验影响 | 需要工程师审核和规则库迭代 |
| 图层标准影响生产 | 激光切割、折弯线、文字说明需要清晰分层 | DXF 输出必须包含标准图层 |
| 软件环境不统一 | 研发可在 Mac，工厂多为 Windows | 需要跨平台设计和 Windows 验证 |

---

## 3. 项目目标

### 3.1 总体目标

开发一个可以辅助工程师完成钣金拆图、加工图生成和拆件方案评估的系统，使工程师从“从零手动画图和凭经验拆件”转变为“审核、比较、修改和确认 AI/CAD 生成的候选方案与图纸初稿”。

### 3.2 阶段目标

| 阶段 | 目标 | 重点 |
| --- | --- | --- |
| 第一阶段 | 跑通 JSON 参数到 DXF 输出 | U 型钣金件、折弯展开计算、ezdxf 图层输出 |
| 第二阶段 | 扩展简单 Web MVP | Streamlit 参数输入、DXF 下载、支持多种基础件 |
| 第三阶段 | CAD 可编辑性与模板扩展 | AutoCAD/FreeCAD 可编辑性、折弯+开孔模板、审核图增强 |
| 第四阶段 | 箱体/电缆盒类产品模板 | 多面结构、焊接边、装配关系、初步拆件方案 |
| 长期阶段 | 复杂图纸到推荐拆图方案 | AI 识别、结构化 JSON、制造约束校验、候选方案评分、DXF/DWG/PDF 输出 |

---

## 4. 项目范围

### 4.1 第一阶段范围

第一阶段只做最小可行产品 MVP，范围明确限定为：

```text
读取 JSON 参数
计算 U 型钣金件展开尺寸
使用 bend allowance 公式
使用 ezdxf 生成 DXF
DXF 包含 CUT / BEND / TEXT 图层
输出 U_BRACKET_001.dxf
可以用 FreeCAD 或 AutoCAD 打开检查
```

### 4.2 后续扩展范围

后续可逐步加入：

- L 型钣金件展开。
- 平板开孔件生成。
- 多孔位、多折弯线支持。
- 同一零件内同时支持折弯线和孔位。
- 箱体、电缆盒等多面钣金结构模板。
- 根据板材尺寸、设备范围、折弯能力和焊接成本生成候选拆分方案。
- Streamlit Web 参数输入界面。
- PDF 文本和尺寸辅助提取。
- 三维工程图 / 三维设计图辅助识别。
- AI 辅助生成结构化 JSON。
- FreeCAD 参数化建模探索。
- Windows AutoCAD / FreeCAD 可编辑性检查。
- DWG 导出或转换流程探索。

### 4.3 暂不纳入第一阶段的内容

- 完全自动理解复杂 PDF 图纸。
- 自动推断完整 3D 结构。
- 自动给出无需工程师审核的“绝对最优”拆图方案。
- 直接输出可生产或可上机切割的最终文件。
- 自动决定所有焊接、打磨、喷漆预留。
- 替代工程师最终判断。

---

## 5. 用户与使用场景

### 5.1 目标用户

| 用户类型 | 需求 |
| --- | --- |
| 钣金工程师 | 快速生成拆图初稿，减少重复绘图 |
| 加工厂技术人员 | 检查 DXF 图层、尺寸和工艺说明 |
| 项目开发者 | 构建个人项目、毕业设计、作品集或创业原型 |
| 工厂管理者 | 降低拆图时间，提高报价和生产准备效率 |

### 5.2 典型使用场景

1. 工程师收到客户 PDF 工程图、复杂三维工程图或三维设计图。
2. 系统辅助识别尺寸、孔位、视图、结构关系和工艺备注。
3. 系统生成结构化产品 JSON 参数。
4. CAD/几何引擎根据参数生成单件或多件展开候选方案。
5. 系统根据生产条件检查是否能一体加工，必要时生成拆分加工方案。
6. 工程师检查折弯线、切割线、孔位、焊接边、装配关系和文字说明。
7. 工程师修改或确认后导出 DXF/DWG/PDF 工艺单。
8. 工程师在自己的 CAD 和生产准备流程中继续修改、确认和下发。

---

## 6. 系统最终形态

### 6.1 推荐形态

最终系统更适合做成：

```text
Web App + CAD 后端 / CAD 插件
```

不建议以手机 App 作为主要形态。钣金拆图涉及 PDF、CAD 图纸、DXF/DWG 文件、图层检查、尺寸审核和工艺确认，更适合在电脑端完成。

### 6.2 最终用户流程

```text
上传客户 PDF 工程图 / 复杂三维工程图 / 三维设计图
↓
AI 识别尺寸、孔位、视图、结构、折弯关系和工艺备注
↓
生成结构化产品 JSON
↓
CAD/几何引擎生成钣金展开候选方案
↓
制造约束校验和拆图方案评分
↓
工程师审核和修改
↓
导出 DXF/DWG/PDF 工艺单
↓
提交给激光切割、折弯和焊接工序
```

### 6.3 人机协作边界

| 环节 | AI/程序负责 | 工程师负责 |
| --- | --- | --- |
| PDF 初步识别 | 提取文字、尺寸、孔位候选 | 判断识别结果是否正确 |
| 三维/多视图理解 | 提取视图关系、面关系和结构候选 | 判断结构推断是否符合真实产品 |
| 参数结构化 | 生成产品 JSON 初稿 | 修正缺失和错误参数 |
| 展开计算 | 根据公式计算展开尺寸、折弯线和孔位 | 确认材料、设备和工艺参数 |
| 拆图方案推荐 | 生成满足约束的候选拆分方案并评分 | 选择、修改或否决推荐方案 |
| DXF 输出 | 自动生成图层和几何线条 | 检查图纸可编辑性、尺寸和工艺含义 |
| 工艺说明 | 生成说明草稿 | 确认焊接、打磨、喷漆要求 |

---

## 7. 技术路线

### 7.1 总体技术路线

```text
PDF / 三维工程图 / 手动参数输入
↓
结构化产品 JSON
↓
Python 几何与折弯展开计算
↓
制造约束校验与候选拆图方案评分
↓
单零件或多零件 DXF 图纸生成
↓
CAD / FreeCAD / AutoCAD 检查与编辑
↓
工程师审核
↓
可编辑 CAD 拆图初稿输出
```

### 7.2 第一阶段技术闭环

第一阶段优先建立可运行、可检查、可扩展的技术闭环：

```text
JSON 参数 -> Python 计算 -> ezdxf 生成 DXF -> FreeCAD/AutoCAD 打开检查
```

### 7.3 中期制造约束与拆件优化闭环

当基础件、折弯线、孔位和非规则外轮廓能力稳定后，中期需要建立制造约束与拆件优化闭环：

```text
产品 JSON
↓
面 / 折弯 / 孔 / 焊接边结构化表示
↓
生成一体展开和多件拆分候选方案
↓
检查板材尺寸、设备加工范围、最大折弯长度、最小孔到折弯线距离等约束
↓
按材料利用率、零件数量、折弯次数、焊接长度和加工难度评分
↓
输出推荐拆图方案和备选方案
```

该模块不应宣称能给出所有场景的绝对最优解，而应先实现“满足生产约束的可解释推荐方案”。

### 7.4 折弯展开公式

U 型钣金件的折弯展开可先采用 bend allowance 公式：

```text
BA = angle_rad × (inside_bend_radius + k_factor × thickness)
angle_rad = bend_angle × π / 180
```

其中：

| 参数 | 含义 |
| --- | --- |
| BA | Bend Allowance，折弯补偿长度 |
| angle_rad | 折弯角度对应的弧度 |
| inside_bend_radius | 内折弯半径 |
| k_factor | K 因子，表示中性层位置 |
| thickness | 板材厚度 |

### 7.5 示例 JSON

```json
{
  "part_name": "U_BRACKET_001",
  "material": "Aluminium 5052",
  "thickness": 2.0,
  "inside_bend_radius": 2.0,
  "k_factor": 0.38,
  "part_length": 200.0,
  "bottom_width": 100.0,
  "left_flange_height": 40.0,
  "right_flange_height": 40.0,
  "bend_angle": 90
}
```

---

## 8. Mac 到 Windows 的开发与部署路线

### 8.1 路线总结

```text
Mac 做研发原型，Windows 做 CAD 可编辑性验证和后续落地。
```

### 8.2 阶段 1：Mac 环境开发 MVP

目前开发者人在国外，主要设备为 iMac mini，并且已经完成基础环境检查：

```text
macOS 可用
Python3 可用
pip 可用
venv 虚拟环境可用
ezdxf 可安装
可以成功生成测试 DXF 文件
```

因此项目第一阶段将在 Mac 环境下开发。

Mac 阶段主要完成：

```text
Python 核心代码
JSON 参数输入
U 型钣金件 DXF 生成
L 型件和平板开孔件扩展
Streamlit 简单 Web 界面
PDF 文本/尺寸辅助提取初版
FreeCAD 查看 DXF 和后续参数化建模探索
```

### 8.3 阶段 2：跨平台兼容

当 Mac 端 MVP 跑通后，需要保证代码可以在 Windows 上运行。

需要考虑：

```text
路径兼容
Python 虚拟环境兼容
DXF 文件兼容
字体和编码兼容
FreeCAD / CAD Viewer 打开兼容
```

建议使用 `pathlib` 处理路径，统一使用 UTF-8 编码，避免把 macOS 特有路径或字体写死在代码中。

### 8.4 阶段 3：Windows 工业落地测试

后期如果要对接真实钣金厂，Windows 会更适合工业场景。

原因包括：

```text
工厂常用 Windows 电脑
AutoCAD 多数部署在 Windows
SolidWorks / Inventor / 激光切割软件多在 Windows
CypCut 等激光切割相关软件常见于 Windows 环境
方便测试 DXF/DWG 在真实工程师 CAD 环境中的可编辑性
```

Windows 阶段主要完成：

```text
AutoCAD / FreeCAD 可打开、可编辑、可保存测试
DXF 图层标准验证
DWG 导出或转换探索
AutoCAD 插件或脚本自动化探索
真实工厂工作流适配
```

---

## 9. MVP 定义

### 9.1 MVP 目标

MVP 的目标是证明“参数化钣金件可以通过 Python 自动生成可打开的 DXF 加工图”，而不是证明系统已经能完全理解所有客户 PDF 图纸。

### 9.2 MVP 功能范围

| 功能 | 是否包含 | 说明 |
| --- | --- | --- |
| 读取 JSON 参数 | 包含 | 从示例 JSON 读取 U 型件参数 |
| 折弯展开计算 | 包含 | 使用 bend allowance 公式 |
| DXF 生成 | 包含 | 使用 ezdxf 输出文件 |
| 图层管理 | 包含 | 至少包含 CUT / BEND / TEXT |
| FreeCAD 打开检查 | 包含 | 验证 DXF 可查看 |
| PDF 自动识别 | 暂不作为核心 | 只做辅助探索，不影响 MVP 成败 |
| DWG 导出 | 暂不包含 | 后续 Windows 阶段探索 |

### 9.3 MVP 输出文件

```text
output/U_BRACKET_001.dxf
```

DXF 文件应至少包含：

| 图层 | 用途 |
| --- | --- |
| CUT | 外轮廓切割线 |
| BEND | 折弯线 |
| TEXT | 零件名、材料、厚度、折弯参数等文字说明 |

---

## 10. 系统功能模块

### 10.1 参数输入模块

负责读取 JSON 文件或 Web 表单输入，包括材料、厚度、折弯半径、K 因子、底宽、翻边高度、长度和折弯角度等。

### 10.2 钣金计算模块

负责计算展开尺寸、折弯补偿、折弯线位置、孔位、槽孔和轮廓坐标。第一阶段重点支持 U 型件，后续扩展 L 型件、平板开孔件、折弯+开孔组合件、多折弯件和箱体类零件。

### 10.3 DXF 生成模块

负责使用 ezdxf 生成 CAD 文件，包括外轮廓线、折弯线、文字标注和图层设置。

### 10.4 PDF 辅助解析模块

负责从 PDF 中提取文字、尺寸候选、材料说明和工艺备注。初期可使用 PyMuPDF 或 pdfplumber，后续结合 AI 视觉模型进行更复杂识别。

### 10.4.1 三维工程图理解模块

负责从复杂三维工程图、三维设计图或多视图工程图中提取产品结构候选，包括：

- 产品由哪些钣金面组成。
- 面与面之间的折弯或焊接关系。
- 孔、槽、缺口、翻边、折边避让和工艺备注属于哪个面。
- 哪些尺寸是外形尺寸、展开尺寸、孔位尺寸或装配尺寸。

该模块输出应进入人工确认流程，不能直接作为生产结论。

### 10.5 Web 界面模块

使用 Streamlit 提供简单界面，让用户输入参数、上传 JSON、生成并下载 DXF。

### 10.6 CAD 检查与兼容模块

用于验证 DXF 在 FreeCAD、AutoCAD 和激光切割软件中的打开效果，检查图层、尺寸、编码和单位兼容性。

### 10.7 拆图方案生成模块

负责根据产品 JSON 生成候选拆图方案。例如电缆盒类产品可生成：

- 一体展开方案。
- 底板 + 侧板分件方案。
- 底板与部分侧板一体、其余侧板单独加工方案。
- 盖板、安装耳、焊接边等附属件单独加工方案。

每个方案都应保留零件清单、折弯线、孔位、焊接边、装配关系和输出文件命名。

### 10.8 制造约束校验与评分模块

负责判断候选拆图方案是否满足生产条件，并给出可解释评分。可逐步纳入：

- 板材标准尺寸和最大可切割范围。
- 折弯机最大折弯长度。
- 最小折边高度。
- 最小孔到折弯线距离。
- 材料利用率。
- 零件数量。
- 折弯次数。
- 焊接长度和焊接成本。
- 工程师或工厂偏好的拆分策略。

评分结果只作为工程师决策辅助，不应自动替代工程师确认。

---

## 11. 数据流程

### 11.1 MVP 数据流程

```text
examples/u_bracket_sample.json
↓
src/main.py
↓
src/sheet_metal_math.py
↓
src/dxf_generator.py
↓
output/U_BRACKET_001.dxf
↓
FreeCAD / AutoCAD 打开检查
```

### 11.2 长期数据流程

```text
客户 PDF / 三维工程图 / 三维设计图
↓
文本 / 视觉 / 多视图解析
↓
尺寸、孔位、材料、结构、折弯关系、工艺备注候选
↓
AI 生成结构化产品 JSON
↓
工程师确认参数
↓
Python / CAD 几何引擎生成一体展开或多件拆分候选方案
↓
制造约束校验和方案评分
↓
工程师审核图纸
↓
导出 DXF / DWG / PDF 工艺单
```

---

## 12. 目录结构建议

第一阶段建议采用清晰、轻量的 Python 项目结构：

```text
Sheet_Metal_AI_Assistant/
├── README.md
├── requirements.txt
├── AI_Sheet_Metal_Drawing_Project_Plan.md
├── examples/
│   └── u_bracket_sample.json
├── output/
│   └── U_BRACKET_001.dxf
├── src/
│   ├── main.py
│   ├── sheet_metal_math.py
│   └── dxf_generator.py
└── tests/
    └── test_sheet_metal_math.py
```

### 12.1 文件职责建议

| 文件 | 职责 |
| --- | --- |
| README.md | 项目说明、安装方法、运行方法 |
| requirements.txt | Python 依赖 |
| examples/u_bracket_sample.json | 示例 U 型件参数 |
| src/main.py | 程序入口 |
| src/sheet_metal_math.py | 折弯展开和几何计算 |
| src/dxf_generator.py | DXF 图层和图形输出 |
| output/ | 生成的 DXF 文件 |
| tests/ | 单元测试 |

---

## 13. 关键技术与工具

### 13.1 Mac MVP 阶段技术栈

```text
Python
ezdxf
JSON
VS Code
Git
FreeCAD
Streamlit
PyMuPDF / pdfplumber
```

### 13.2 Windows 工业验证阶段技术栈

```text
AutoCAD
FreeCAD for Windows
可能的 AutoLISP / AutoCAD .NET / Python 脚本
DXF/DWG 兼容测试
激光切割软件兼容测试
```

### 13.3 AI 辅助开发工具

```text
Codex
Claude Code
ChatGPT
```

这些 AI 工具主要用于：

```text
辅助写代码
生成测试脚本
重构项目结构
编写文档
帮助解析 PDF 和生成结构化数据
```

AI 工具不能完全替代工程师判断。涉及尺寸、材料、折弯参数、焊接预留和生产可行性的结果，必须由工程师审核确认。

---

## 14. 分阶段实施计划

### 14.1 阶段计划总览

| 阶段 | 时间建议 | 目标 | 关键任务 |
| --- | --- | --- | --- |
| 阶段 1 | 1-2 周 | Mac MVP 技术闭环 | JSON 读取、U 型件计算、DXF 输出 |
| 阶段 2 | 2-4 周 | 基础件扩展和 Web 界面 | L 型件、开孔平板、Streamlit 下载 |
| 阶段 3 | 2-4 周 | 折弯+开孔组合能力 | U 型/ L 型带孔、孔到折弯线校验、面归属 |
| 阶段 4 | 2-4 周 | PDF / 三维图辅助解析初版 | PyMuPDF/pdfplumber、视觉识别、结构化产品 JSON 草稿 |
| 阶段 5 | 2-4 周 | Windows CAD 可编辑性验证 | AutoCAD/FreeCAD 打开、编辑、保存测试 |
| 阶段 6 | 长期 | 箱体/电缆盒和拆图优化原型 | 多面结构、候选拆分方案、制造约束评分、真实案例验证 |

### 14.2 阶段 1：Mac MVP

核心任务：

- 创建正式 Python 项目结构。
- 建立 `.venv` 虚拟环境。
- 安装 `ezdxf`。
- 创建 U 型件 JSON 示例。
- 编写折弯展开计算函数。
- 使用 `ezdxf` 生成 DXF。
- 设置 CUT / BEND / TEXT 图层。
- 使用 FreeCAD 打开检查。
- 编写 README 运行说明。

### 14.3 阶段 2：基础件与 Web 界面

核心任务：

- 支持 L 型件展开。
- 支持平板开孔件。
- 增加 Streamlit 参数输入页面。
- 支持上传 JSON 和下载 DXF。
- 增加基础输入校验。
- 增加简单示意预览。

### 14.4 阶段 3：折弯+开孔组合能力

核心任务：

- 完善 `u_bracket_with_holes`，并继续扩展 L 型件带孔或通用 `bent_plate_with_holes` 模板。
- 支持同一个零件内同时输出 `CUT / BEND / HOLE / TEXT`。
- 支持底面孔、翻边孔和展开坐标换算。
- 增加孔到折弯线的最小安全距离校验。
- 在 SVG 检查图中同时显示外轮廓、折弯线、孔位和孔表。
- 为后续箱体、电缆盒和多面结构建立面归属数据结构。

### 14.5 阶段 4：PDF / 三维工程图辅助解析

核心任务：

- 使用 PyMuPDF 或 pdfplumber 读取 PDF 文本。
- 提取材料、厚度、尺寸和备注候选。
- 探索复杂三维工程图 / 多视图工程图的尺寸、孔位、视图和结构关系识别。
- 将识别结果转换为结构化产品 JSON 草稿。
- 保留人工确认界面。
- 标记低置信度字段。

### 14.6 阶段 5：Windows CAD 可编辑性验证

核心任务：

- 在 Windows 上建立 Python 运行环境。
- 验证 DXF 在 AutoCAD 中打开效果。
- 验证 DXF 在 FreeCAD for Windows 中打开效果。
- 验证工程师能否在 CAD 中选择、编辑、移动、删除和保存生成的对象。
- 探索 DWG 转换或导出方案。
- 记录工厂工作流适配问题。

### 14.7 阶段 6：箱体/电缆盒和拆图优化原型

核心任务：

- 建立箱体、电缆盒类产品参数模板。
- 表达底板、侧板、盖板、翻边、安装孔、电缆孔、焊接边和装配关系。
- 输入生产约束，例如最大加工尺寸、板材规格、最大折弯长度和最小孔到折弯距离。
- 生成一体展开、多件拆分等候选方案。
- 按材料利用率、零件数量、折弯次数、焊接长度和加工难度进行评分。
- 输出推荐方案和备选方案，供工程师比较和审核。

---

## 15. 每阶段交付物

| 阶段 | 交付物 |
| --- | --- |
| 阶段 1 | 可运行 Python 项目、U 型件 JSON 示例、U_BRACKET_001.dxf、README |
| 阶段 2 | Streamlit Web MVP、至少 3 种基础钣金件、DXF 下载功能 |
| 阶段 3 | 带孔折弯件模板、孔到折弯线校验、同时包含 CUT/BEND/HOLE/TEXT 的 DXF |
| 阶段 4 | PDF / 三维图文本与尺寸提取脚本、结构化产品 JSON 草稿、人工确认流程 |
| 阶段 5 | Windows CAD 可编辑性测试报告、AutoCAD/FreeCAD 打开截图、图层和对象可编辑性记录 |
| 阶段 6 | 箱体/电缆盒原型、候选拆分方案、制造约束评分、真实案例测试报告 |

---

## 16. 风险与应对措施

| 风险 | 影响 | 应对策略 |
| --- | --- | --- |
| PDF 图纸尺寸识别不准确 | 生成错误参数，导致图纸错误 | 初期只做辅助提取，所有尺寸进入人工确认；保留原 PDF 对照 |
| 多视图到 3D 结构推断困难 | AI 难以准确理解复杂结构 | 第一阶段不做自动 3D 推断；先支持简单标准件和参数化模板 |
| 三维图结构识别不完整 | 面关系、折弯关系或装配关系错误 | 输出低置信度提示和待确认问题清单；由工程师确认面归属和装配关系 |
| 拆图方案“最优”定义不清 | 不同工厂可能优先材料利用率、少焊接或少零件 | 明确输入约束和评分权重；输出可解释评分，不宣称绝对最优 |
| 产品展开尺寸超过设备能力 | 一体展开方案不可加工 | 引入板材规格、最大切割尺寸和最大折弯长度校验；生成多件拆分候选方案 |
| 孔位靠近折弯线 | 折弯后孔变形或加工不可行 | 增加最小孔到折弯线距离规则；所有冲突进入人工审核 |
| 折弯展开参数受材料和设备影响 | 展开尺寸可能与实际生产不一致 | 将材料、厚度、内 R、K 因子做成可配置参数；后续建立工厂参数库 |
| 焊接、打磨、喷漆预留难以完全标准化 | 自动生成结果可能不符合工艺习惯 | 由工程师审核；先记录规则，再逐步形成工艺模板 |
| DXF 在不同 CAD 软件中兼容性不同 | 文件可能打不开、文字不显示或对象不便编辑 | 使用标准 DXF 版本；在 FreeCAD、AutoCAD 等 CAD 软件中分别测试 |
| Mac 开发环境与 Windows 工厂环境存在差异 | Mac 可运行但工厂无法使用 | 采用跨平台路径和编码；第二阶段后尽早做 Windows 验证 |
| AI 可能生成看似合理但工程上错误的结果 | 造成生产风险 | AI 输出必须标记为草稿；关键参数由工程师确认；加入校验规则 |
| 客户图纸缺尺寸或标注不一致 | 无法生成可靠加工图 | 系统标记缺失字段；生成待确认问题清单；不自动通过审核 |

---

## 17. 后续扩展方向

### 17.1 更多钣金结构

- L 型件。
- Z 型件。
- 带孔折弯件。
- 箱体类钣金件。
- 电缆盒类钣金件。
- 多折弯件。
- 带孔、槽、倒角和圆角的平板件。

### 17.2 CAD 自动化

- AutoCAD 脚本自动出图。
- AutoLISP 插件探索。
- AutoCAD .NET 插件探索。
- FreeCAD 参数化建模。
- DXF 到 DWG 转换流程。

### 17.3 AI 图纸理解

- PDF 图纸 OCR。
- 三维工程图 / 三维设计图视觉理解。
- 尺寸标注识别。
- 多视图关系识别。
- 面关系、折弯关系和装配关系识别。
- 工艺备注抽取。
- 自动生成结构化产品 JSON。

### 17.3.1 拆图方案优化

- 一体展开可行性判断。
- 多件拆分候选方案生成。
- 板材尺寸和设备加工范围校验。
- 折弯能力、孔到折弯线距离和折边避让校验。
- 材料利用率、零件数量、折弯次数、焊接长度和加工难度评分。
- 推荐方案和备选方案对比输出。

### 17.4 工艺知识库

- 材料参数库。
- K 因子经验库。
- 折弯设备参数库。
- 焊接和打磨预留规则。
- 表面处理规则。

---

## 18. 成功标准

### 18.1 第一阶段成功标准

```text
Mac 上可以运行项目
可以读取 JSON
可以生成 U 型件 DXF
DXF 有 CUT / BEND / TEXT 图层
可以在 FreeCAD 打开
README 清楚说明运行方法
```

### 18.2 第二阶段成功标准

```text
可以通过简单 Web 界面输入参数
可以下载 DXF
支持至少 3 种基础钣金件
```

### 18.3 第三阶段成功标准

```text
可以在 Windows 上运行
DXF 可以在 AutoCAD 或 FreeCAD 等 CAD 软件中打开并继续编辑
图层、尺寸和说明信息清楚
```

### 18.4 长期成功标准

```text
上传 PDF / 复杂三维工程图 / 三维设计图后，
系统能生成结构化产品 JSON，
并给出满足生产约束的可审核拆图方案，
工程师只需要比较、修改和确认，而不是从零手绘和完全凭经验拆件。
```

---

## 当前进度

### 2026-05-21 带孔折弯件公共逻辑抽象更新

已完成：

- 已按用户要求跳过人工 CAD 检查，继续推进下一步行动清单中的代码项。
- 已在 `src/sheet_metal_math.py` 中抽象带孔折弯件公共逻辑：
  - 新增内部 `BentPlateFaceDefinition`，统一描述面宽、展开 X 偏移和折弯相邻边。
  - 新增通用面内孔校验逻辑，复用到带孔 U 型件和带孔 L 型件。
  - 新增通用孔到折弯相邻边距离校验逻辑，支持圆孔和长圆槽孔的半宽计算。
  - 新增通用面内孔展开逻辑，把所属面局部坐标统一换算到展开图坐标。
- 保留现有公开零件类型不变：`u_bracket_with_holes` 和 `l_bracket_with_holes` 仍按原 JSON 接口使用。
- 已补充带孔 U 型件长圆槽孔测试，验证通用逻辑可处理非圆孔的展开坐标和折弯邻边距离校验。
- 已重新生成带孔 U 型件和带孔 L 型件 DXF / SVG 样例。
- 已更新 README，说明带孔 U/L 型件现在复用公共面定义逻辑，下一步重点转向校验增强和 Streamlit 手动表单。

本次修改的文件：

- `src/sheet_metal_math.py`
- `tests/test_sheet_metal_math.py`
- `README.md`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`
- `output/U_BRACKET_HOLES_001.dxf`
- `output/U_BRACKET_HOLES_001_preview.svg`
- `output/L_BRACKET_HOLES_001.dxf`
- `output/L_BRACKET_HOLES_001_preview.svg`

测试结果：

- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，编译检查通过。
- 已运行 `.venv/bin/python -m unittest tests.test_sheet_metal_math`，共 `26` 个数学层测试通过。
- 已运行 `.venv/bin/python -m unittest discover tests`，共 `70` 个测试通过。
- 已运行 `.venv/bin/python src/main.py --input examples/u_bracket_with_holes_sample.json --output-dir output --preview-svg`，成功生成 `output/U_BRACKET_HOLES_001.dxf` 和 `output/U_BRACKET_HOLES_001_preview.svg`。
- 已运行 `.venv/bin/python src/main.py --input examples/l_bracket_with_holes_sample.json --output-dir output --preview-svg`，成功生成 `output/L_BRACKET_HOLES_001.dxf` 和 `output/L_BRACKET_HOLES_001_preview.svg`。

存在问题：

- 本次完成的是内部公共逻辑抽象，还没有新增公开的 `bent_plate_with_holes` JSON 零件类型。
- 孔到折弯距离仍按折弯相邻面边界做 MVP 简化校验，尚未区分真实折弯线、折弯影响区、模具压痕区或孔变形风险。
- Streamlit 手动参数页仍未提供带孔 U/L 型件编辑表单。
- 带孔 U/L 型折弯件的最新 DXF 仍需后续人工 CAD 审核。

---

### 2026-05-21 项目进展汇报更新

已完成：

- 已按项目规则重新读取 `AGENTS.md`、`README.md` 和本项目计划书，并检查当前项目结构。
- 确认当前项目已超过第一阶段 U 型件 MVP，已经形成 `JSON 参数 -> Python 计算 -> DXF / SVG / Streamlit 预览与下载` 的基础闭环。
- 当前代码支持 U 型件、带孔 U 型件、L 型件、带孔 L 型件、平板开孔件和平板异形特征件。
- 当前输出目录已有 `U_BRACKET_001.dxf`、`U_BRACKET_HOLES_001.dxf`、`L_BRACKET_001.dxf`、`L_BRACKET_HOLES_001.dxf`、`FLAT_PLATE_001.dxf`、`FLAT_PLATE_FEATURES_001.dxf` 及对应 SVG / FreeCAD 检查版本。
- 已确认当前目录不是 Git 仓库，无法通过 `git status` 检查版本控制差异。

本次修改的文件：

- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `.venv/bin/python -m unittest discover tests`。
- 当前 `68` 个测试全部通过。

存在问题：

- 带孔 U/L 型折弯件尚未完成 AutoCAD / FreeCAD 人工视觉审核。
- Streamlit 手动参数页尚未提供带孔 U/L 型件编辑表单，当前主要通过 JSON 上传、SVG 预览和交付包流程使用。
- 当前孔到折弯校验仍是 MVP 简化规则，尚未区分真实折弯影响区、模具压痕区和孔变形风险。
- 项目目录当前未初始化为 Git 仓库，后续不利于跟踪代码变更和回滚。

---

### 2026-05-20 带孔 L 型折弯件模板更新

已完成：

- 已根据用户确认继续推进下一步行动清单，扩展带孔折弯件能力。
- 新增 `l_bracket_with_holes` 零件类型：
  - 支持 `flange` 和 `base` 两个孔所属面。
  - 孔位 `x / y` 使用所属面内局部坐标，程序会换算到展开图坐标。
  - `min_hole_to_bend_distance` 用于做孔到折弯相邻面边界的 MVP 级安全距离校验。
- DXF 输出已支持带孔 L 型件：
  - 同时输出 `CUT / BEND / HOLE / TEXT` 图层。
  - 圆孔写入 `HOLE` 图层。
  - 文字中记录 `TYPE: L_BRACKET_WITH_HOLES`、孔位来源和最小孔边距离。
- SVG 检查图已支持带孔 L 型件，同时显示外轮廓、折弯线、孔位、孔编号和孔表。
- Streamlit JSON 上传预览的图层开关已支持 `l_bracket_with_holes` 的 `BEND` 和 `HOLE` 图层。
- 新增示例文件 `examples/l_bracket_with_holes_sample.json`。
- 已更新 README，补充带孔 L 型件运行命令、JSON 示例、字段说明、校验规则、当前限制和下一步建议。

本次修改的文件：

- `src/sheet_metal_math.py`
- `src/dxf_generator.py`
- `src/svg_preview.py`
- `src/generation.py`
- `src/streamlit_app.py`
- `examples/l_bracket_with_holes_sample.json`
- `tests/test_sheet_metal_math.py`
- `tests/test_dxf_generator.py`
- `tests/test_svg_preview.py`
- `tests/test_generation.py`
- `tests/test_main_cli.py`
- `README.md`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`
- `output/L_BRACKET_HOLES_001.dxf`
- `output/L_BRACKET_HOLES_001_preview.svg`

测试结果：

- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。
- 已运行 `.venv/bin/python -m unittest tests.test_sheet_metal_math tests.test_dxf_generator tests.test_svg_preview tests.test_generation tests.test_main_cli tests.test_streamlit_app`，共 `68` 个相关测试通过。
- 已运行 `.venv/bin/python -m unittest discover tests`，共 `68` 个测试通过。
- 已运行 `.venv/bin/python src/main.py --input examples/l_bracket_with_holes_sample.json --output-dir output --preview-svg`，成功生成 `output/L_BRACKET_HOLES_001.dxf` 和 `output/L_BRACKET_HOLES_001_preview.svg`。
- 已使用 `ezdxf.readfile()` 读回 `output/L_BRACKET_HOLES_001.dxf`，确认包含 `CUT / BEND / HOLE / TEXT` 图层，其中 `CUT` 外轮廓 `1` 个、`BEND` 真实线段 `12` 条、`HOLE` 圆孔 `3` 个、`TEXT` 普通文字 `12` 条。
- 已运行 `env PYTHONPATH=src .venv/bin/python -c "from streamlit.testing.v1 import AppTest; ..."`，Streamlit 页面加载检查通过。

存在问题：

- 当前已支持 U 型件带孔和 L 型件带孔，但尚未抽象成通用 `bent_plate_with_holes` 多折弯模板。
- 当前孔到折弯安全距离仍是按孔边到折弯相邻面边界的简化校验，尚未区分真实折弯线、折弯影响区或模具压痕区。
- 带孔 L 型件尚未在 AutoCAD / FreeCAD 中人工视觉审核。
- 当前 Streamlit 手动表单尚未提供带孔 U/L 型件编辑页，但 JSON 上传、SVG 预览和交付包流程已可使用这些类型。

---

### 2026-05-20 带孔 U 型折弯件模板更新

已完成：

- 已按“下一步行动清单”第一项推进带孔折弯件能力。
- 新增 `u_bracket_with_holes` 零件类型，初步打通同一零件内同时存在折弯线和孔位的能力。
- 新增带孔 U 型件参数结构：
  - 复用 U 型件材料、厚度、内 R、K 因子、底宽、翻边高度和折弯角度字段。
  - `holes` 每一项增加 `face` 字段，当前支持 `left_flange`、`bottom`、`right_flange`。
  - 孔位 `x / y` 使用所属面内局部坐标，程序会换算到展开图坐标。
  - `min_hole_to_bend_distance` 用于做孔到折弯相邻面边界的 MVP 级安全距离校验。
- DXF 输出已支持带孔 U 型件：
  - 同时输出 `CUT / BEND / HOLE / TEXT` 图层。
  - 折弯线继续使用真实短线段模拟虚线。
  - 圆孔写入 `HOLE` 图层。
  - 文字中记录 `TYPE: U_BRACKET_WITH_HOLES`、孔位来源和最小孔边距离。
- SVG 检查图已支持带孔 U 型件，同时显示外轮廓、折弯线、孔位、孔编号和孔表。
- Streamlit JSON 上传预览的图层开关已支持 `u_bracket_with_holes` 的 `BEND` 和 `HOLE` 图层。
- 新增示例文件 `examples/u_bracket_with_holes_sample.json`。
- 已更新 README，补充带孔 U 型件运行命令、JSON 示例、字段说明、校验规则、当前限制和下一步建议。

本次修改的文件：

- `src/sheet_metal_math.py`
- `src/dxf_generator.py`
- `src/svg_preview.py`
- `src/generation.py`
- `src/streamlit_app.py`
- `examples/u_bracket_with_holes_sample.json`
- `tests/test_sheet_metal_math.py`
- `tests/test_dxf_generator.py`
- `tests/test_svg_preview.py`
- `tests/test_generation.py`
- `tests/test_main_cli.py`
- `README.md`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`
- `output/U_BRACKET_HOLES_001.dxf`
- `output/U_BRACKET_HOLES_001_preview.svg`

测试结果：

- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。
- 已运行 `.venv/bin/python -m unittest tests.test_sheet_metal_math tests.test_dxf_generator tests.test_svg_preview tests.test_generation tests.test_main_cli tests.test_streamlit_app`，共 `62` 个相关测试通过。
- 已运行 `.venv/bin/python -m unittest discover tests`，共 `62` 个测试通过。
- 已运行 `.venv/bin/python src/main.py --input examples/u_bracket_with_holes_sample.json --output-dir output --preview-svg`，成功生成 `output/U_BRACKET_HOLES_001.dxf` 和 `output/U_BRACKET_HOLES_001_preview.svg`。
- 已使用 `ezdxf.readfile()` 读回 `output/U_BRACKET_HOLES_001.dxf`，确认包含 `CUT / BEND / HOLE / TEXT` 图层，其中 `CUT` 外轮廓 `1` 个、`BEND` 真实线段 `24` 条、`HOLE` 圆孔 `4` 个、`TEXT` 普通文字 `13` 条。
- 已运行 `env PYTHONPATH=src .venv/bin/python -c "from streamlit.testing.v1 import AppTest; ..."`，Streamlit 页面加载检查通过。

存在问题：

- 当前只支持带孔 U 型件，尚未支持 L 型件带孔或通用多折弯带孔模板。
- 当前孔到折弯安全距离是按孔边到折弯相邻面边界的简化校验，尚未区分真实折弯影响区、模具压痕区或孔变形风险区。
- 带孔 U 型件尚未在 AutoCAD / FreeCAD 中人工视觉审核。
- 当前 Streamlit 手动表单尚未提供带孔 U 型件编辑页，但 JSON 上传、SVG 预览和交付包流程已可使用该类型。

---

### 2026-05-20 长期产品目标和拆图优化路线更新

已完成：

- 已根据用户新的产品设想，重新明确本项目长期目标：
  - 输入不应只局限于简单 PDF，而应逐步支持复杂三维工程图、三维设计图和多视图工程图。
  - AI 需要识别尺寸、孔位、视图、结构、折弯关系和工艺备注，并生成结构化产品 JSON。
  - 系统后期需要根据生产条件生成候选拆图方案，而不是只输出单个展开图。
- 已把电缆盒 / 箱体类产品作为长期关键应用场景写入计划：
  - 当一体展开超出板材或设备加工范围时，系统应能生成多件拆分方案。
  - 候选方案应按材料利用率、零件数量、折弯次数、焊接长度、加工难度等因素评分。
- 已明确“最优解”边界：
  - 不宣称自动给出所有场景的绝对最优生产方案。
  - 目标是生成满足生产约束的可解释推荐方案和备选方案，供工程师审核。
- 已把短期技术路线调整为优先补齐“折弯 + 开孔同时存在”的能力：
  - 下一步建议新增 `u_bracket_with_holes` 或 `bent_plate_with_holes` 模板。
  - 支持同一零件内同时输出 `CUT / BEND / HOLE / TEXT`。
  - 增加孔到折弯线的最小安全距离校验和孔所属面表达。
- 已更新 README，补充长期产品目标、当前限制和下一步路线。

本次修改的文件：

- `README.md`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 本次为文档和产品路线更新，未修改 Python 代码。
- 已运行 `rg` 检查 README 和项目计划书中的项目目标、下一步行动清单、PDF/三维图、拆图优化相关表述。

存在问题：

- 带孔折弯件模板尚未实现。
- 电缆盒 / 箱体类产品的数据结构、面归属、焊接边和装配关系尚未实现。
- 制造约束评分模块尚未实现，后续需要用户提供设备加工范围、板材规格、折弯能力和成本偏好等参数。

---

### 2026-05-19 平板角部圆角特征更新

已完成：

- 已按“下一步行动清单”继续扩展非规则外轮廓能力。
- 平板/异形开孔件 `features` 新增 `corner_radius` 参数化特征：
  - 支持 `lower_left`、`lower_right`、`upper_right`、`upper_left` 四个角。
  - 使用 `radius` 表示圆角半径。
  - 同一角不允许同时设置 `corner_chamfer` 和 `corner_radius`。
  - 边缘矩形缺口会避开相邻倒角或圆角占用区域。
- DXF / SVG 输出已支持角部圆角：
  - 当前 MVP 使用固定分段线近似圆弧，继续写入 `CUT` 外轮廓。
  - DXF 文字摘要会显示 `ROUND CORNER` 特征数量。
  - SVG 检查图的特征摘要会显示 `ROUND CORNER`。
- Streamlit 平板/异形开孔件表单新增“角部圆角”表格，可直接输入角和半径。
- 已更新 `examples/flat_plate_with_features_sample.json`，加入右下角圆角示例。
- 已更新 README，说明 `corner_radius` JSON 格式、当前分段线近似限制和人工审核要求。

本次修改的文件：

- `src/sheet_metal_math.py`
- `src/dxf_generator.py`
- `src/svg_preview.py`
- `src/streamlit_app.py`
- `examples/flat_plate_with_features_sample.json`
- `tests/test_sheet_metal_math.py`
- `tests/test_dxf_generator.py`
- `tests/test_svg_preview.py`
- `tests/test_streamlit_app.py`
- `README.md`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`
- `output/FLAT_PLATE_FEATURES_001.dxf`
- `output/FLAT_PLATE_FEATURES_001_preview.svg`
- `output/U_BRACKET_001.dxf`

测试结果：

- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。
- 已运行 `.venv/bin/python -m unittest tests.test_sheet_metal_math tests.test_dxf_generator tests.test_svg_preview tests.test_streamlit_app`，共 `42` 个相关测试通过。
- 已运行 `.venv/bin/python -m unittest discover tests`，共 `56` 个测试通过。
- 已运行 `env PYTHONPATH=src .venv/bin/python -c "from streamlit.testing.v1 import AppTest; ..."`，Streamlit 页面加载检查通过。
- 已运行 `.venv/bin/python src/main.py --input examples/flat_plate_with_features_sample.json --output-dir output --preview-svg`，成功生成 `output/FLAT_PLATE_FEATURES_001.dxf` 和 `output/FLAT_PLATE_FEATURES_001_preview.svg`。
- 已运行 `.venv/bin/python src/main.py examples/u_bracket_sample.json`，成功生成 `output/U_BRACKET_001.dxf`。
- 已运行 `ls -l output`，确认 `output/U_BRACKET_001.dxf` 存在。

存在问题：

- 角部圆角当前以固定分段线近似圆弧，尚未输出真实 DXF `ARC` 或带 bulge 的多段线；需要在 CAD 中人工检查视觉效果和可编辑性。
- 新加入的角部圆角示例尚未由用户在 AutoCAD / FreeCAD 中人工审核。
- 折边避让尚未实现，下一步可继续做参数化折边避让缺口或折弯释放槽。

---

### 2026-05-19 无效孔位诊断预览更新

已完成：

- 已按“下一步行动清单”推进 SVG 预览诊断能力。
- 当平板/异形件因孔位与 CUT 外轮廓、倒角或缺口冲突而不能生成正式预览时，Streamlit 现在会尽量显示诊断预览：
  - CUT 外轮廓仍显示。
  - 冲突孔位以半透明红色和虚线边框显示。
  - 冲突孔位标签使用红色文字。
- 已保持生产输出严格性：
  - DXF 生成仍会报错并阻止输出。
  - 交付包仍会报错并阻止输出。
  - 诊断预览只用于帮助用户定位参数问题，不作为正式图纸。
- 已更新 SVG 预览支持 `invalid_hole_indexes`，用于把指定孔位渲染为无效孔样式。
- 已新增测试覆盖：
  - SVG 中无效孔位的红色诊断样式。
  - Streamlit 对底部缺口冲突槽孔生成诊断 SVG。
- 已更新 README，说明无效孔位会以半透明红色显示。

本次修改的文件：

- `src/svg_preview.py`
- `src/streamlit_app.py`
- `tests/test_svg_preview.py`
- `tests/test_streamlit_app.py`
- `README.md`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。
- 已运行 `.venv/bin/python -m unittest tests.test_svg_preview tests.test_streamlit_app`，共 `18` 个相关测试通过。
- 已运行 `.venv/bin/python -m unittest discover tests`，共 `54` 个测试通过。
- 已运行 Streamlit `AppTest`，确认页面可加载并可切换到“平板/异形开孔件”。

存在问题：

- 当前诊断预览只标出触发校验错误的孔位；如果未来多个孔同时冲突，需要进一步增强批量冲突检测。
- 下一步建议继续推进非规则外轮廓能力，优先支持圆角和折边避让。

---

### 2026-05-19 异形缺口孔位冲突提示修复

已完成：

- 已根据用户截图确认问题：当前“中心允许范围”只按基础矩形板边计算，没有表达底部缺口、倒角等异形切除区域；当长圆槽孔移动到底部缺口位置时，表格范围看似允许，但几何校验会正确拦截。
- 已更新 Streamlit 允许范围提示文案：
  - 明确该范围仅按基础矩形板边计算。
  - 明确仍需避开倒角、缺口和异形切边。
- 已新增平板/异形件即时几何校验提示：
  - 当孔或槽孔与异形外轮廓、倒角或缺口相交时，表单区域会提前显示中文提示。
  - `holes[1] must keep the full hole inside the cut outline.` 已转换为“第 2 个孔/槽孔与异形外轮廓、倒角或缺口相交，必须把整个孔移到 CUT 外轮廓内部。”
- 已新增测试覆盖用户截图中的槽孔与底部缺口相交场景。
- 已更新 README，说明中心允许范围是基础矩形范围，异形切边冲突会另行提示。

本次修改的文件：

- `src/streamlit_app.py`
- `tests/test_streamlit_app.py`
- `README.md`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。
- 已运行 `.venv/bin/python -m unittest tests.test_streamlit_app`，共 `7` 个 Streamlit 表单辅助测试通过。
- 已运行 `.venv/bin/python -m unittest discover tests`，共 `52` 个测试通过。
- 已运行 Streamlit `AppTest`，确认可切换到“平板/异形开孔件”，并能看到“仍需避开倒角、缺口和异形切边”的提示。

存在问题：

- 当前只是把异形冲突提示清楚化，并没有计算“扣除缺口/倒角后的完整可放置区域”；更精确的实时可放置区域需要后续做几何偏置或区域可视化。
- 下一步可考虑在 SVG 预览中把无效孔位以半透明红色显示出来，而不是完全不生成预览。

---

### 2026-05-19 Streamlit 孔/槽孔允许范围提示更新

已完成：

- 已按“下一步行动清单”推进 Streamlit 平板/异形件表单的人机体验。
- 已在圆孔表格下方显示每一行圆孔中心允许范围：
  - 根据孔径、板宽和板长计算 `X/Y` 合法区间。
- 已在长圆槽孔表格下方显示每一行槽孔中心允许范围：
  - 水平槽孔按 `length/2` 计算 `中心 X` 范围，按 `width/2` 计算 `中心 Y` 范围。
  - 竖直槽孔按 `width/2` 计算 `中心 X` 范围，按 `length/2` 计算 `中心 Y` 范围。
- 已新增测试覆盖圆孔、水平槽孔和竖直槽孔的允许范围文本。
- 已更新 README，说明孔表下方会显示中心坐标允许范围。

本次修改的文件：

- `src/streamlit_app.py`
- `tests/test_streamlit_app.py`
- `README.md`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。
- 已运行 `.venv/bin/python -m unittest tests.test_streamlit_app`，共 `6` 个 Streamlit 表单辅助测试通过。
- 已运行 `.venv/bin/python -m unittest discover tests`，共 `51` 个测试通过。
- 已运行 Streamlit `AppTest`，确认可切换到“平板/异形开孔件”，并能看到“槽孔中心允许范围”提示。

存在问题：

- 当前允许范围提示只考虑板宽、板长和孔/槽孔自身尺寸；如果孔靠近倒角、缺口或未来自由外轮廓，仍由几何校验继续拦截。
- 下一步建议开始实现圆角和折边避让等更高频的非规则外轮廓特征。

---

### 2026-05-19 Streamlit 本地服务恢复

已完成：

- 已检查 `http://localhost:8506` 无法打开的原因：
  - 初始检查时 `8506` 没有监听进程。
  - Streamlit 页面代码通过 `AppTest` 检查，无页面异常。
  - 直接在沙盒内启动 Streamlit 会因端口绑定权限报 `PermissionError: [Errno 1] Operation not permitted`。
- 已使用提升权限方式启动 Streamlit：
  - 启动命令为 `.venv/bin/streamlit run src/streamlit_app.py --server.port 8506 --server.headless true`。
  - Streamlit 输出当前 Local URL 为 `http://localhost:8506`。
- 已用 `lsof` 确认 Python/Streamlit 进程正在监听 `8506`。

本次修改的文件：

- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 Streamlit `AppTest`，页面代码无异常。
- 已运行 `lsof -nP -iTCP:8506 -sTCP:LISTEN`，确认 `8506` 有 Python 进程监听。

存在问题：

- Codex 沙盒内 `curl http://localhost:8506` 仍无法连接，但 `lsof` 与 Streamlit 启动日志均显示服务已启动；这与此前沙盒网络边界现象一致。
- 如果浏览器仍打不开，建议用户手动刷新页面，或在终端结束旧进程后重新运行计划书开头记录的启动命令。

---

### 2026-05-18 Streamlit 平板预览实时刷新修复

已完成：

- 已定位平板/异形开孔件参数修改后预览图不自动更新的原因：
  - 手动参数区整体包在 `st.form` 里。
  - 平板/异形件大量使用 `st.data_editor` 表格控件，表格在 form 内部的状态提交机制不会稳定触发外部预览实时刷新。
  - U 型件和 L 型件主要是普通输入控件，因此表现上更像可以正常刷新。
- 已将手动参数区改为实时输入区：
  - U 型件、L 型件、平板/异形开孔件参数控件不再包在 `st.form` 中。
  - 预览、SVG 下载、参数模板和交付包读取当前控件状态。
  - `生成 DXF` 保留为按钮，仍需用户点击后才写入/下载 DXF。
- 已新增测试，防止手动参数区重新被 `st.form("manual_parameters")` 包裹导致实时预览失效。
- 已更新 README，说明 Web 界面会根据当前输入实时刷新简易图形预览。

本次修改的文件：

- `src/streamlit_app.py`
- `tests/test_streamlit_app.py`
- `README.md`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。
- 已运行 `.venv/bin/python -m unittest tests.test_streamlit_app`，共 `5` 个 Streamlit 表单辅助测试通过。
- 已运行 `.venv/bin/python -m unittest discover tests`，共 `50` 个测试通过。
- 已运行 Streamlit `AppTest`，确认页面可加载、可切换到“平板/异形开孔件”，且保留 `生成 DXF` 按钮。

存在问题：

- 本次修复的是 Streamlit 状态刷新机制；浏览器中的既有页面需要刷新或重启当前 `8506` 服务后才能加载新代码。
- `st.data_editor` 的逐格编辑体验仍由 Streamlit 控件本身决定；后续如果需要更强的图形化编辑，可考虑在预览图上增加直接编辑能力。

---

### 2026-05-18 Streamlit 孔坐标校验提示优化

已完成：

- 已根据用户截图确认当前问题原因：长圆槽孔第二行参数为 `中心 X=300.00 mm`、`中心 Y=1000.00 mm`，但当前平板默认尺寸约为 `180.00 x 110.00 mm`，槽孔中心和整体槽孔已超出板件范围，因此预览、交付包和 DXF 生成被校验拦截。
- 已优化 Streamlit 表格输入：
  - 圆孔 `X/Y` 最大值跟随当前板宽/板长。
  - 长圆槽孔 `中心 X/中心 Y` 最大值跟随当前板宽/板长。
- 已新增 Streamlit 友好错误提示：
  - 将 `holes[1].x must keep the hole inside the plate.` 转换为中文说明。
  - 提示第几个孔/槽孔、哪个坐标超出、当前值是多少、建议范围是多少。
- 已新增测试覆盖用户截图中的 `holes[1].x` 超出板件范围场景。
- 已更新 README，记录孔和槽孔坐标会按板宽/板长限制，并显示中文建议范围。

本次修改的文件：

- `src/streamlit_app.py`
- `tests/test_streamlit_app.py`
- `README.md`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。
- 已运行 `.venv/bin/python -m unittest tests.test_streamlit_app`，共 `4` 个 Streamlit 表单辅助测试通过。
- 已运行 `.venv/bin/python -m unittest discover tests`，共 `49` 个测试通过。
- 已运行 Streamlit `AppTest`，确认页面可加载并可切换到“平板/异形开孔件”表单。

存在问题：

- 当前表格只能限制 `X/Y` 不超过板宽/板长；槽孔是否完整留在板内仍需要结合槽孔长度、宽度和方向继续由几何校验判断。
- 后续可进一步在表格旁显示实时“允许范围”，例如水平槽孔 `中心 X` 应位于 `length/2` 到 `板宽 - length/2` 之间。

---

### 2026-05-18 SVG 孔编号避让修复

已完成：

- 已根据用户截图反馈修复平板/异形开孔件预览中 `H2` 与长圆槽孔线条交叉的问题。
- 已将孔编号放置逻辑改为基于孔或槽孔外接框：
  - 默认放在圆孔或长圆槽孔外接框上方。
  - 上方空间不足时放到外接框下方。
  - 文本使用居中锚点，避免再按圆孔半径简单偏移导致槽孔标签压线。
- 已新增回归测试，确认孔编号文字坐标不落入对应孔/槽孔外接框范围。
- 已重新生成平板开孔件和平板/异形开孔件 SVG 检查图。
- 已更新 README，补充孔编号会避开圆孔和长圆槽孔线条的说明。

本次修改的文件：

- `src/svg_preview.py`
- `tests/test_svg_preview.py`
- `output/FLAT_PLATE_001_preview.svg`
- `output/FLAT_PLATE_FEATURES_001_preview.svg`
- `README.md`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。
- 已运行 `.venv/bin/python -m unittest tests.test_svg_preview`，共 `9` 个 SVG 预览测试通过。
- 已运行 `.venv/bin/python -m unittest discover tests`，共 `48` 个测试通过。
- 已运行 CLI 重新生成 `output/FLAT_PLATE_FEATURES_001_preview.svg`，确认 `H2` 位于长圆槽孔上方，未再压到槽孔线条。

存在问题：

- 当前避让规则优先保证孔编号不与孔线/槽孔线交叉；后续如果增加更多孔距尺寸链或更密集孔阵列，还需要进一步做标签自动避让和冲突检测。
- 本次未重新验证浏览器页面截图；需要用户刷新或重启 `8506` 上的 Streamlit 页面后目视确认。

---

### 2026-05-18 SVG 尺寸箭头与平板孔预览修复

已完成：

- 已修复 SVG 检查图尺寸线箭头越过尺寸线端点的问题：
  - 尺寸线不再使用会向端点外溢出的 SVG marker。
  - 新增尺寸线内部实体箭头，箭头尖端落在尺寸线端点，箭头主体保持在线段内部。
- 已修复 Streamlit 从 U 型件或 L 型件切换到“平板/异形开孔件”后，`HOLE` 图层可能沿用旧零件状态而未默认勾选的问题：
  - 预览图层复选框 key 已按零件类型隔离。
  - 平板/异形开孔件的 `HOLE` 图层现在会按该零件类型默认启用。
- 已重新生成 U 型件、L 型件、平板开孔件和平板/异形开孔件 SVG 检查图。
- 已更新 README，记录尺寸箭头和孔图层默认显示行为。

本次修改的文件：

- `src/svg_preview.py`
- `src/streamlit_app.py`
- `tests/test_svg_preview.py`
- `tests/test_streamlit_app.py`
- `output/U_BRACKET_001_preview.svg`
- `output/L_BRACKET_001_preview.svg`
- `output/FLAT_PLATE_001_preview.svg`
- `output/FLAT_PLATE_FEATURES_001_preview.svg`
- `README.md`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。
- 已运行 `.venv/bin/python -m unittest tests.test_svg_preview tests.test_streamlit_app`，共 `11` 个相关测试通过。
- 已运行 `.venv/bin/python -m unittest discover tests`，共 `47` 个测试通过。
- 已运行 Streamlit `AppTest`，确认切换到“平板/异形开孔件”后 `HOLE` 图层默认启用。
- 已运行 CLI 重新生成 SVG 检查图，并用文本检索确认 `output/FLAT_PLATE_FEATURES_001_preview.svg` 中包含圆孔 `<circle class="hole">` 和长圆槽孔 `<path class="hole">`。

存在问题：

- 当前沙盒内直接启动 Streamlit 绑定 `8506` 会触发权限限制；提升权限后 Streamlit 报告 `8506` 已被占用。
- 已用 `lsof` 确认有 Python 进程监听 `8506`，但沙盒内 `curl http://localhost:8506` 仍无法连接；本次页面层验证以 Streamlit `AppTest` 和生成 SVG 文件检查为准。
- 如果用户浏览器中仍看不到孔，建议刷新页面或重启当前 `8506` 上的 Streamlit 进程，避免继续使用旧代码状态。

---

### 2026-05-18 Streamlit 本地端口记录更新

已完成：

- 已确认当前 Streamlit 本地访问端口更新为 `8506`。
- 已在项目计划书开头新增“当前本地服务地址”显眼区块，记录当前访问地址、推荐启动命令和端口维护规则。
- 已同步更新 README 中的 Streamlit 启动命令和本地访问地址，减少 `8501`、`8503`、`8506` 历史记录造成的混淆。

本次修改的文件：

- `AI_Sheet_Metal_Drawing_Project_Plan.md`
- `README.md`

测试结果：

- 本次为文档和项目规则更新，不涉及 Python 计算、DXF 生成或 Streamlit 代码修改。
- 已用文本检索检查 Streamlit 端口相关说明，确认当前显眼入口记录为 `http://localhost:8506`。

存在问题：

- 本次未重新启动 Streamlit 服务；当前端口信息按用户确认记录。
- 后续如再次改端口，必须同步更新计划书开头的“当前本地服务地址”区块，并在当前进度中记录。

---

### 2026-05-18 Streamlit 平板/异形表单更新

已完成：

- 已按“下一步行动清单”继续推进 Web 表单输入能力。
- 已将 Streamlit 中的“平板开孔件”调整为“平板/异形开孔件”，更贴合当前可编辑 CAD 初稿目标。
- 已为平板/异形开孔件表单增加基础表格输入：
  - 圆孔。
  - 长圆槽孔。
  - 角部倒角。
  - 边缘矩形缺口。
- 已把表格输入转换为现有 `holes` 和 `features` JSON 结构，继续复用已有计算、校验、DXF 和 SVG 生成链路。
- 已将 Streamlit 默认平板示例调整为此前人工审核通过的非规则平板样式，便于用户打开网页后直接看到更接近实际图纸的例子。
- 已新增 Streamlit 表单辅助逻辑测试，覆盖圆孔、长圆槽孔、倒角和缺口的数据转换。
- 已更新 README，说明 Web 界面现在可以直接编辑圆孔、长圆槽孔和基础非规则外轮廓特征。

本次修改的文件：

- `src/streamlit_app.py`
- `tests/test_streamlit_app.py`
- `README.md`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。
- 已运行 `.venv/bin/python -m unittest discover tests`，共 `45` 个测试通过。
- 已运行 Streamlit `AppTest`，确认页面可执行，并可切换到“平板/异形开孔件”，显示圆孔、长圆槽孔、角部倒角和边缘矩形缺口四类编辑区。

存在问题：

- 当前 Web 表单仍是表格输入，还不是拖拽式图形编辑器；用户需要理解 X/Y、长度、宽度、偏移和方向等参数含义。
- 当前平板/异形件仍采用“基础矩形 + 参数化特征”的方式，尚未支持自由 `cut_outline` 多段线、圆角和折边避让。
- 本轮未新增真实 CAD 人工审核截图记录；已通过的长圆槽孔示例仍以用户确认和测试记录为准。

---

### 2026-05-18 长圆槽孔人工审核确认更新

已完成：

- 已由用户确认：带角部倒角、边缘缺口和长圆槽孔的平板件示例已人工审核通过。
- 本次确认覆盖当前示例输出：
  - `output/FLAT_PLATE_FEATURES_001.dxf`
  - `output/FLAT_PLATE_FEATURES_001_FREECAD.dxf`
  - `output/FLAT_PLATE_FEATURES_001_preview.svg`
- 已将长圆槽孔示例从“待人工 CAD 检查”推进为“已通过人工审核”。
- 已更新 README 的当前限制/验证状态，记录该人工审核结果。
- 已更新下一步行动清单，把优先级转向圆角、折边避让和 Web 表单输入能力。

本次修改的文件：

- `README.md`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 本次为人工审核结果和文档状态更新，不涉及 Python 计算、DXF 生成或 SVG 渲染逻辑修改。
- 已运行 `rg` 检查 README 和项目计划书中的“人工审核 / 长圆槽孔 / 下一步行动清单”相关表述。

存在问题：

- 当前人工审核结果来自用户确认，尚未形成独立的截图记录或结构化 CAD 检查报告。
- Streamlit 手动表单仍未提供槽孔和 `features` 图形化输入控件。

---

### 2026-05-18 平板件长圆槽孔更新

已完成：

- 已根据用户“确认”继续推进下一步高频特征扩展。
- 已在 `flat_plate.holes` 中增加长圆槽孔 `slot` 支持：
  - `x`、`y` 表示槽孔中心点。
  - `length` 表示槽孔总长。
  - `width` 表示槽孔宽度和两端圆弧直径。
  - `orientation` 可选 `horizontal` 或 `vertical`，默认 `horizontal`。
- 已保留早期圆孔 JSON 兼容性：不写 `type` 时仍按圆孔处理。
- 已更新计算层：
  - 新增 `SlotHole` 数据结构。
  - 长圆槽孔会校验 `length > width`。
  - 槽孔会按两端圆心和半径检查是否完整落在最终 `CUT` 外轮廓内。
- 已更新 DXF 输出：
  - 圆孔继续输出为 `HOLE` 图层 `CIRCLE`。
  - 长圆槽孔输出为 `HOLE` 图层的真实 `LINE + ARC` 几何，便于 CAD 中查看和编辑。
  - 孔标签支持 `Hn SLOT length x width`。
- 已更新 SVG 检查图：
  - 长圆槽孔会显示为长圆形 `path`。
  - 孔表尺寸列支持 `DIA/SIZE`。
- 已更新 `examples/flat_plate_with_features_sample.json`，示例中包含 1 个圆孔和 1 个水平长圆槽孔。
- 已重新生成：
  - `output/FLAT_PLATE_FEATURES_001.dxf`
  - `output/FLAT_PLATE_FEATURES_001_FREECAD.dxf`
  - `output/FLAT_PLATE_FEATURES_001_preview.svg`

本次修改的文件：

- `src/sheet_metal_math.py`
- `src/dxf_generator.py`
- `src/svg_preview.py`
- `tests/test_sheet_metal_math.py`
- `tests/test_dxf_generator.py`
- `tests/test_svg_preview.py`
- `examples/flat_plate_with_features_sample.json`
- `output/FLAT_PLATE_FEATURES_001.dxf`
- `output/FLAT_PLATE_FEATURES_001_FREECAD.dxf`
- `output/FLAT_PLATE_FEATURES_001_preview.svg`
- `README.md`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。
- 已运行 `.venv/bin/python -m unittest tests.test_sheet_metal_math tests.test_dxf_generator tests.test_svg_preview`，共 `29` 个相关测试通过。
- 已运行 `.venv/bin/python src/main.py --input examples/flat_plate_with_features_sample.json --output-dir output --preview-svg`，成功生成标准 DXF 和 SVG 检查图。
- 已运行 `.venv/bin/python src/main.py --input examples/flat_plate_with_features_sample.json --output-dir output --text-mode outline --file-suffix _FREECAD`，成功生成 FreeCAD 检查版 DXF。
- 已使用 `ezdxf.readfile()` 读回 `output/FLAT_PLATE_FEATURES_001.dxf`，确认：
  - `CUT` 图层包含 1 个外轮廓。
  - `HOLE` 图层包含 1 个圆孔、2 条槽孔直线和 2 段槽孔圆弧。
  - `TEXT` 中包含 `H2 SLOT 34.00x10.00`。

存在问题：

- 长圆槽孔当前支持水平和竖直方向，暂不支持任意角度旋转槽孔。
- Streamlit 手动表单尚未提供槽孔和 `features` 图形化编辑控件；用户目前可通过 JSON 上传使用。
- 仍需在 AutoCAD / FreeCAD 中人工打开新槽孔示例，确认槽孔几何选择、编辑和显示体验。

---

### 2026-05-17 平板件非规则外轮廓 features 初版更新

已完成：

- 已按“下一步行动清单”第一项继续推进非规则外轮廓能力。
- 已在 `flat_plate` 参数中引入可选 `features` 数据结构，当前支持：
  - `corner_chamfer`：角部倒角。
  - `edge_notch`：边缘矩形缺口。
- 已更新计算层：
  - 平板件不再只能生成规则矩形外轮廓。
  - 可根据 `features` 生成带倒角、缺口的 `CUT` 外轮廓点列。
  - 对边缘缺口、倒角范围、同边缺口重叠做基础校验。
  - 孔位校验改为基于最终 `CUT` 外轮廓，避免孔落在已切除区域。
- 已更新 DXF 输出：
  - 非规则外轮廓仍写入 `CUT` 图层，保持 CAD 中可选择、可编辑。
  - 平板件文字信息增加 `FEATURES` 汇总。
- 已更新 SVG 检查图：
  - 复用最终 `cut_outline` 渲染非规则外轮廓。
  - 对带特征平板件显示 `FEATURES` 汇总。
- 已新增示例参数文件 `examples/flat_plate_with_features_sample.json`。
- 已生成示例输出：
  - `output/FLAT_PLATE_FEATURES_001.dxf`
  - `output/FLAT_PLATE_FEATURES_001_FREECAD.dxf`
  - `output/FLAT_PLATE_FEATURES_001_preview.svg`

本次修改的文件：

- `src/sheet_metal_math.py`
- `src/dxf_generator.py`
- `src/svg_preview.py`
- `tests/test_sheet_metal_math.py`
- `tests/test_dxf_generator.py`
- `tests/test_svg_preview.py`
- `examples/flat_plate_with_features_sample.json`
- `output/FLAT_PLATE_FEATURES_001.dxf`
- `output/FLAT_PLATE_FEATURES_001_FREECAD.dxf`
- `output/FLAT_PLATE_FEATURES_001_preview.svg`
- `README.md`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。
- 已运行 `.venv/bin/python -m unittest tests.test_sheet_metal_math tests.test_dxf_generator tests.test_svg_preview`，共 `25` 个相关测试通过。
- 已运行 `.venv/bin/python src/main.py --input examples/flat_plate_with_features_sample.json --output-dir output --preview-svg`，成功生成标准 DXF 和 SVG 检查图。
- 已运行 `.venv/bin/python src/main.py --input examples/flat_plate_with_features_sample.json --output-dir output --text-mode outline --file-suffix _FREECAD`，成功生成 FreeCAD 检查版 DXF。
- 已使用 `ezdxf.readfile()` 读回 `output/FLAT_PLATE_FEATURES_001.dxf`，确认 `CUT` 外轮廓包含 `11` 个顶点，`HOLE` 图层包含 `2` 个孔，`TEXT` 中包含 `FEATURES: 2 CHAMFER, 1 EDGE NOTCH`。

存在问题：

- 当前 `features` 只覆盖角部倒角和边缘矩形缺口，尚未支持圆角、长圆槽孔、沉孔、折边避让或任意自由外轮廓。
- 当前 Streamlit 手动表单尚未提供 `features` 图形化编辑控件；用户可以通过 JSON 上传使用该能力。
- 非规则外轮廓仍需在 AutoCAD / FreeCAD 中进行人工视觉检查，确认 CAD 选择和二次编辑体验。

---

### 2026-05-17 SVG 标注专业化与非规则轮廓路线更新

已完成：

- 已根据用户反馈修正 SVG 检查图的标注表现：
  - 外形宽度尺寸文字保持水平，并与水平尺寸线平行。
  - 外形长度尺寸文字旋转为竖向，并与竖向尺寸线平行。
  - 折弯方向提示移动到外轮廓上方，避免压住 CUT / BEND 图形线条。
  - 底部图例由整句文字改为短线条、虚线和孔样式加文字，更接近实际图纸说明习惯。
- 已补充 SVG 预览测试，检查尺寸文字锚点、竖向旋转标注和图例样式。
- 已重新生成 U 型件、L 型件和平板开孔件的 SVG 检查图。
- 已明确下一阶段方向：用户最终需要的通常不是规则矩形，而是带倒角、圆角、缺口、槽孔、折边避让等特征的可编辑 CAD 初稿。
- 已将后续路线调整为“基础模板 + 可编辑特征 + 后续自由外轮廓”，而不是继续只围绕规则矩形模板打磨。

本次修改的文件：

- `src/svg_preview.py`
- `tests/test_svg_preview.py`
- `output/U_BRACKET_001_preview.svg`
- `output/L_BRACKET_001_preview.svg`
- `output/FLAT_PLATE_001_preview.svg`
- `README.md`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。
- 已运行 `.venv/bin/python -m unittest tests.test_svg_preview tests.test_generation`，共 `10` 个相关测试通过。
- 已运行 CLI 重新生成三种示例件的 SVG 检查图，输出文件已更新。
- 已在浏览器打开 Streamlit 页面 `http://localhost:8506/`，确认页面可加载并能显示当前参数输入、预览入口和下载功能；浏览器安全策略不允许直接打开本地 SVG 文件，因此本地 SVG 视觉细节以生成文件和单元测试作为验证依据。

存在问题：

- 当前 DXF/SVG 几何仍主要来自矩形基础模板，尚未支持真实客户图纸中常见的倒角、圆角、边缘缺口、长圆槽和异形外轮廓。
- 下一步不宜继续只增加规则矩形模板，应优先建立非规则外轮廓的数据结构和几何生成能力。
- 当前 SVG 检查图仍是审核辅助图，不等同于正式工程尺寸图；完整 CAD 尺寸链和工程审核签名区仍需后续补充。

---

### 2026-05-17 Streamlit 一键交付包更新

已完成：

- 已按“下一步行动清单”第一项，在 Streamlit 中增加一键下载交付包能力。
- 已新增 `generate_delivery_package_from_data()`，用于从同一份 JSON 参数生成 ZIP 交付包。
- 交付包当前包含：
  - 标准 DXF 文件，用于 CAD 软件继续编辑。
  - SVG 检查图，用于浏览器快速查看和沟通。
  - JSON 参数文件，用于复用、修改和回溯生成来源。
- 已更新 `src/streamlit_app.py`，在参数输入页和 JSON 上传页都增加“下载交付包 ZIP”按钮。
- 已更新测试，直接打开 ZIP 验证其中包含 `DXF + SVG + JSON` 三类文件。
- 已更新 `README.md`，补充交付包的定位、内容和测试覆盖。

本次修改的文件：

- `src/generation.py`
- `src/streamlit_app.py`
- `tests/test_generation.py`
- `README.md`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。
- 已运行 `.venv/bin/python -m unittest tests.test_generation`，共 `5` 个生成工作流测试通过。
- 已运行 `PYTHONPATH=src .venv/bin/python -c "from streamlit.testing.v1 import AppTest; ..."`，确认 Streamlit 页面执行无异常。
- 已运行 `.venv/bin/python -m unittest discover tests`，共 `34` 个测试通过。
- 已运行 `PYTHONPATH=src .venv/bin/python -c "...generate_delivery_package_from_data..."`，确认 `U_BRACKET_001_delivery_package.zip` 中包含：
  - `U_BRACKET_001.dxf`
  - `U_BRACKET_001_preview.svg`
  - `U_BRACKET_001_parameters.json`

存在问题：

- 当前交付包只包含标准 AutoCAD/CAD 版 DXF，不包含 `*_FREECAD.dxf` 兼容检查版，避免把检查版误当正式交付文件。
- 当前交付包仍是单零件交付包，尚未支持多零件项目打包、版本号或审核记录。

---

### 2026-05-17 项目定位与行动清单纠偏更新

已完成：

- 已根据用户反馈重新明确项目主线：本项目交付目标是可编辑、可审核、可修改的钣金 CAD 拆图初稿，而不是直接生成可上机切割的最终生产文件。
- 已明确后续激光切割软件、设备参数、排版套料和上机工艺属于用户或工厂既有生产流程，不作为当前 MVP 主线。
- 已更新 `README.md`：
  - 增加当前项目目标说明。
  - 明确 DXF 是工程师审核和编辑初稿，不是直接投产或上机切割文件。
  - 将后续行动从激光切割软件兼容验证调整为 CAD 可编辑性、模板扩展和 PDF 到 JSON 草稿探索。
- 已更新本项目计划书：
  - 项目定位改为“钣金 CAD 拆图初稿”。
  - 阶段目标从“Windows 工业验证/激光切割软件兼容”调整为“CAD 可编辑性与模板扩展”。
  - Windows 阶段重点改为 AutoCAD / FreeCAD 可打开、可编辑、可保存测试。
  - 下一步行动清单移除激光切割软件验证，改为交付包、SVG 审核图、模板库、更多钣金件模板和 PDF 辅助提取。

本次修改的文件：

- `README.md`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 本次为文档和项目方向调整，不涉及 Python 计算或 DXF 生成逻辑修改。
- 已运行 `rg` 检查 README 和项目计划书中的相关定位、下一步行动清单和后续建议表述。

存在问题：

- 历史记录中仍保留早期“激光切割软件兼容测试”的开发语境，作为项目演进记录保留不删除。
- 后续需要继续把新增功能聚焦在“可编辑 CAD 初稿”和“工程师审核效率”上，避免过早扩展到上机切割流程。

---

### 2026-05-17 SVG 审核图尺寸线与孔表更新

已完成：

- 已按“下一步行动清单”继续增强 SVG 检查图，让网页端预览更接近工程审核图。
- 已更新 `src/svg_preview.py`：
  - 增加外形宽度尺寸线和长度尺寸线。
  - 增加尺寸箭头和延长线。
  - 为 U 型件和 L 型件增加折弯线编号与 `BEND UP VERIFY` 折弯方向待确认提示。
  - 为平板开孔件增加孔表，列出孔编号、X 坐标、Y 坐标和孔径。
  - 扩大 SVG 画布并调整绘图区，避免顶部信息、尺寸线和几何图形重叠。
- 已更新 `tests/test_svg_preview.py`，覆盖尺寸线、折弯方向提示、孔表和大尺寸预览安全区。
- 已重新生成三份 SVG 检查图：
  - `output/U_BRACKET_001_preview.svg`
  - `output/L_BRACKET_001_preview.svg`
  - `output/FLAT_PLATE_001_preview.svg`
- 已更新 `README.md`，说明 SVG 检查图现在包含外形尺寸线、折弯方向待确认提示和孔表。

本次修改的文件：

- `src/svg_preview.py`
- `tests/test_svg_preview.py`
- `README.md`
- `output/U_BRACKET_001.dxf`
- `output/L_BRACKET_001.dxf`
- `output/FLAT_PLATE_001.dxf`
- `output/U_BRACKET_001_preview.svg`
- `output/L_BRACKET_001_preview.svg`
- `output/FLAT_PLATE_001_preview.svg`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。
- 已运行 `.venv/bin/python -m unittest tests.test_svg_preview tests.test_generation tests.test_main_cli`，共 `18` 个相关测试通过。
- 已运行 `PYTHONPATH=src .venv/bin/python -c "from streamlit.testing.v1 import AppTest; ..."`，确认 Streamlit 页面执行无异常。
- 已运行 `.venv/bin/python -m unittest discover tests`，共 `33` 个测试通过。
- 已运行 `.venv/bin/python src/main.py --input examples/u_bracket_sample.json --output-dir output --preview-svg`，成功生成 `output/U_BRACKET_001.dxf` 和 `output/U_BRACKET_001_preview.svg`。
- 已运行对应命令生成 `L_BRACKET_001_preview.svg` 和 `FLAT_PLATE_001_preview.svg`。
- 已运行 `find output -maxdepth 1 -name '*.svg' -print -exec ls -l {} \;`，确认三份 SVG 检查图均已更新。

存在问题：

- 折弯方向当前仅是 `BEND UP VERIFY` 待确认提示，尚未由参数明确表达真实折弯方向。
- SVG 孔表当前列出孔坐标和孔径，但尚未生成孔距尺寸链、尺寸公差或正式孔表编号规则。
- 当前 SVG 检查图仍是审核辅助图，不是生产批准图。

---

### 2026-05-17 浏览器 SVG 检查图输出更新

已完成：

- 已根据用户对“单一软件依赖”和“网页使用局限性”的担忧，继续推进 CAD 无关的检查能力。
- 已明确产品方向：网页/SVG 检查图用于通用预览和沟通，标准 DXF 用于 CAD/生产软件，FreeCAD 轮廓版仅作为兼容性检查备选。
- 已增强 `src/svg_preview.py`：
  - SVG 预览现在包含零件名、材料、厚度、展开尺寸。
  - 折弯件显示 bend allowance。
  - 平板开孔件显示孔数量。
  - 绘图区下移，避免文字信息和几何图形重叠。
- 已更新 `src/generation.py`，新增 `generate_svg_preview_from_data()`，可从同一份 JSON 参数生成浏览器 SVG 检查图。
- 已更新 `src/main.py`，新增 `--preview-svg` 参数，可在生成 DXF 的同时输出 `*_preview.svg`。
- 已更新 `src/streamlit_app.py`，在图形预览区新增“下载 SVG 检查图”按钮。
- 已重新生成三份浏览器 SVG 检查图：
  - `output/U_BRACKET_001_preview.svg`
  - `output/L_BRACKET_001_preview.svg`
  - `output/FLAT_PLATE_001_preview.svg`
- 已更新测试，覆盖 SVG 信息文字、SVG 文件生成、CLI `--preview-svg` 和 Streamlit 页面执行。
- 已更新 `README.md`，补充 SVG 检查图的定位、运行命令、输出文件和测试覆盖。

本次修改的文件：

- `src/svg_preview.py`
- `src/generation.py`
- `src/main.py`
- `src/streamlit_app.py`
- `tests/test_svg_preview.py`
- `tests/test_generation.py`
- `tests/test_main_cli.py`
- `README.md`
- `output/U_BRACKET_001.dxf`
- `output/L_BRACKET_001.dxf`
- `output/FLAT_PLATE_001.dxf`
- `output/U_BRACKET_001_FREECAD.dxf`
- `output/L_BRACKET_001_FREECAD.dxf`
- `output/FLAT_PLATE_001_FREECAD.dxf`
- `output/U_BRACKET_001_preview.svg`
- `output/L_BRACKET_001_preview.svg`
- `output/FLAT_PLATE_001_preview.svg`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。
- 已运行 `.venv/bin/python -m unittest tests.test_svg_preview tests.test_generation tests.test_main_cli`，共 `18` 个相关测试通过。
- 已运行 `PYTHONPATH=src .venv/bin/python -c "from streamlit.testing.v1 import AppTest; ..."`，确认 Streamlit 页面执行无异常。
- 已运行 `.venv/bin/python -m unittest discover tests`，共 `33` 个测试通过。
- 已运行 `.venv/bin/python src/main.py --input examples/u_bracket_sample.json --output-dir output --text-mode standard --preview-svg`，成功生成 `output/U_BRACKET_001.dxf` 和 `output/U_BRACKET_001_preview.svg`。
- 已运行对应命令生成 `L_BRACKET_001_preview.svg` 和 `FLAT_PLATE_001_preview.svg`。
- 已重新生成三份 `*_FREECAD.dxf` 检查版。

存在问题：

- 当前 SVG 检查图仍是简易审核预览，不包含正式尺寸线、箭头、孔表、折弯方向或工程签核区。
- Streamlit 当前可下载 SVG 检查图，但尚未提供一键下载“DXF + SVG + JSON”的打包功能。
- 当前 SVG 不是生产批准文件，仍需工程师按真实 CAD/DXF 和制造参数复核。

---

### 2026-05-17 FreeCAD 文字检查版输出更新

已完成：

- 已根据用户反馈确认：Windows AutoCAD 打开标准版 DXF 后文字显示正常，但 Mac FreeCAD 打开标准 `TEXT` 时看不到文字。
- 已明确当前兼容策略：不再让同一个 DXF 同时包含普通文字和文字轮廓，避免 AutoCAD 重影；改为提供两种输出模式。
- 已更新 `src/dxf_generator.py`，新增文字输出模式：
  - `standard`：标准 `TEXT` 实体，面向 Windows AutoCAD 和常规 CAD 检查。
  - `outline`：文字轮廓 `LWPOLYLINE`，面向 Mac FreeCAD 检查。
- 已更新 `src/generation.py` 和 `src/main.py`，新增命令参数：
  - `--text-mode standard|outline`
  - `--file-suffix`
- 已重新生成 AutoCAD 标准版：
  - `output/U_BRACKET_001.dxf`
  - `output/L_BRACKET_001.dxf`
  - `output/FLAT_PLATE_001.dxf`
- 已新增生成 Mac FreeCAD 检查版：
  - `output/U_BRACKET_001_FREECAD.dxf`
  - `output/L_BRACKET_001_FREECAD.dxf`
  - `output/FLAT_PLATE_001_FREECAD.dxf`
- 已更新测试，覆盖 FreeCAD 轮廓文字模式和 CLI 后缀输出。
- 已更新 `README.md`，说明两种文字模式的使用场景和命令。

本次修改的文件：

- `src/dxf_generator.py`
- `src/generation.py`
- `src/main.py`
- `tests/test_dxf_generator.py`
- `tests/test_main_cli.py`
- `README.md`
- `output/U_BRACKET_001.dxf`
- `output/L_BRACKET_001.dxf`
- `output/FLAT_PLATE_001.dxf`
- `output/U_BRACKET_001_FREECAD.dxf`
- `output/L_BRACKET_001_FREECAD.dxf`
- `output/FLAT_PLATE_001_FREECAD.dxf`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。
- 已运行 `.venv/bin/python -m unittest tests.test_dxf_generator tests.test_main_cli tests.test_generation`，共 `15` 个相关测试通过。
- 已重新生成三份 AutoCAD 标准版 DXF，文字模式为 `standard`。
- 已生成三份 Mac FreeCAD 检查版 DXF，文字模式为 `outline`，文件名后缀为 `_FREECAD`。
- 已使用 `ezdxf.readfile()` 读回六个 DXF，确认文字实体策略正确：
  - `U_BRACKET_001.dxf`: `TEXT=5`, `TEXT_LWPOLYLINE=0`
  - `L_BRACKET_001.dxf`: `TEXT=6`, `TEXT_LWPOLYLINE=0`
  - `FLAT_PLATE_001.dxf`: `TEXT=11`, `TEXT_LWPOLYLINE=0`
  - `U_BRACKET_001_FREECAD.dxf`: `TEXT=0`, `TEXT_LWPOLYLINE=141`
  - `L_BRACKET_001_FREECAD.dxf`: `TEXT=0`, `TEXT_LWPOLYLINE=159`
  - `FLAT_PLATE_001_FREECAD.dxf`: `TEXT=0`, `TEXT_LWPOLYLINE=253`
- 已运行 `.venv/bin/python -m unittest discover tests`，共 `31` 个测试通过。

存在问题：

- 需要用户用 Mac FreeCAD 打开 `*_FREECAD.dxf`，确认文字轮廓可见且没有明显重叠。
- 需要继续保留 AutoCAD 标准版和 FreeCAD 检查版的区别，避免把两类文字重新混在一个文件中。
- Streamlit 当前默认仍输出 AutoCAD 标准版，暂未在 Web 界面加入 FreeCAD 文字模式选择。

---

### 2026-05-17 AutoCAD 文字重影修复更新

已完成：

- 已根据用户提供的 AutoCAD 截图确认：`CUT` 外轮廓、`BEND` 折弯虚线、`HOLE` 孔图层显示正常，问题集中在 `TEXT` 图层文字重影、轮廓线混乱和局部重叠。
- 已定位原因为：DXF 同时写入普通 `TEXT` 实体和文字轮廓 `LWPOLYLINE`，AutoCAD 会同时显示两套文字，导致重影和混乱。
- 已更新 `src/dxf_generator.py`，默认只写入 AutoCAD 友好的标准 `TEXT` 实体，不再生成文字轮廓多段线。
- 已调整信息文字排版，从上到下写入并增加行距，减少信息区文字互相压住的风险。
- 已重新生成 `output/U_BRACKET_001.dxf`、`output/L_BRACKET_001.dxf` 和 `output/FLAT_PLATE_001.dxf`。
- 已更新测试，明确验证 `TEXT` 图层不再包含文字轮廓 `LWPOLYLINE`。
- 已更新 `README.md`，记录当前 `TEXT` 图层策略改为标准文字实体，并标记需要重新用 AutoCAD 复核。

本次修改的文件：

- `src/dxf_generator.py`
- `tests/test_dxf_generator.py`
- `README.md`
- `output/U_BRACKET_001.dxf`
- `output/L_BRACKET_001.dxf`
- `output/FLAT_PLATE_001.dxf`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。
- 已运行 `.venv/bin/python -m unittest tests.test_dxf_generator`，共 `3` 个 DXF 生成测试通过。
- 已运行 `.venv/bin/python src/main.py --input examples/u_bracket_sample.json --output-dir output`，成功重新生成 `output/U_BRACKET_001.dxf`。
- 已运行 `.venv/bin/python src/main.py --input examples/l_bracket_sample.json --output-dir output`，成功重新生成 `output/L_BRACKET_001.dxf`。
- 已运行 `.venv/bin/python src/main.py --input examples/flat_plate_with_holes_sample.json --output-dir output`，成功重新生成 `output/FLAT_PLATE_001.dxf`。
- 已使用 `ezdxf.readfile()` 读回三个 DXF，确认 `TEXT_LWPOLYLINE=0`：
  - `U_BRACKET_001.dxf`: `TEXT=5`, `TEXT_LWPOLYLINE=0`
  - `L_BRACKET_001.dxf`: `TEXT=6`, `TEXT_LWPOLYLINE=0`
  - `FLAT_PLATE_001.dxf`: `TEXT=11`, `TEXT_LWPOLYLINE=0`
- 已运行 `.venv/bin/python -m unittest discover tests`，共 `29` 个测试通过。

存在问题：

- 最新 DXF 还需要用户重新用 AutoCAD 打开确认文字是否已无重影、无重叠。
- 由于移除了文字轮廓多段线，FreeCAD 中普通 `TEXT` 的显示效果需要后续重新抽查；如果 FreeCAD 仍有文字显示问题，可以考虑增加单独的可开关 `TEXT_OUTLINE` 图层，而不是与 `TEXT` 混在一起。
- 当前文字仍是说明性标注，不是正式尺寸链、孔表或生产工艺卡。

---

### 2026-05-15 Streamlit 预览图层开关与 CLI 兼容更新

已完成：

- 已阅读项目计划书，并按当前下一步行动清单继续推进 Streamlit 图形预览能力。
- 已为 Streamlit SVG 预览增加 `CUT`、`BEND`、`HOLE`、`TEXT` 图层开关，便于单独检查切割轮廓、折弯线、孔位和标注。
- 已更新 `src/svg_preview.py`，支持按可见图层渲染预览，不影响 DXF 输出逻辑。
- 已更新 `src/main.py`，兼容计划书中的位置参数运行方式：`.venv/bin/python src/main.py examples/u_bracket_sample.json`。
- 已新增回归测试，覆盖 SVG 图层隐藏逻辑和 CLI 位置参数输入。
- 已更新 `README.md`，同步新的运行方式、预览图层开关和测试覆盖范围。

本次修改的文件：

- `src/main.py`
- `src/svg_preview.py`
- `src/streamlit_app.py`
- `tests/test_main_cli.py`
- `tests/test_svg_preview.py`
- `README.md`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。
- 已运行 `.venv/bin/python -m unittest tests.test_svg_preview tests.test_main_cli`，共 `12` 个相关测试通过。
- 已运行 `.venv/bin/python -m unittest discover tests`，共 `29` 个测试通过。
- 已运行 `PYTHONPATH=src .venv/bin/python -c "from streamlit.testing.v1 import AppTest; ..."`，确认 Streamlit 页面执行无异常。
- 已运行 `.venv/bin/python src/main.py examples/u_bracket_sample.json`，成功生成 `output/U_BRACKET_001.dxf`。
- 已运行 `ls -l output/`，确认 `output/U_BRACKET_001.dxf` 存在。
- 已启动 Streamlit 本地预览服务，`8501` 和 `8502` 已被占用，当前可用地址为 `http://localhost:8503`。
- 已运行 `curl -I http://localhost:8503`，本地服务返回 `HTTP/1.1 200 OK`。

存在问题：

- 当前图层开关只影响 Streamlit SVG 预览，不改变 DXF 文件中的实体和图层。
- 当前 SVG 预览仍不是正式生产图，尚未加入正式尺寸线、折弯方向箭头、孔表或工程审核状态。
- AutoCAD 或其他 CAD Viewer 交叉验证仍未完成。

---

### 2026-05-15 Streamlit 图形预览重叠修复更新

已完成：

- 已修复 Streamlit 图形预览中“大尺寸外轮廓与标题/说明文字重叠”的问题。
- 已调整 `src/svg_preview.py` 的 SVG 缩放逻辑，将画布拆分为固定 header、drawing、legend 区域。
- 几何图形现在只会缩放到 drawing 安全区内，不再占用顶部零件名称和预览说明区域。
- 已新增回归测试，验证大尺寸平板预览的外轮廓 Y 坐标不会进入 header 文字区域。

本次修改的文件：

- `src/svg_preview.py`
- `tests/test_svg_preview.py`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。
- 已运行 `.venv/bin/python -m unittest tests.test_svg_preview`，共 `3` 个 SVG 预览测试通过。
- 已运行 `.venv/bin/python -m unittest discover tests`，共 `26` 个测试通过。

存在问题：

- 当前预览仍是简易 SVG 示意图，尚未加入正式尺寸线、图层开关或折弯方向箭头。

---

### 2026-05-15 Streamlit 图形预览与参数模板更新

已完成：

- 已回到 Streamlit 功能本身，优先完成图形预览和参数模板保存。
- 已新增 `src/svg_preview.py`，将已计算的展开图渲染为简易 SVG 预览。
- 已更新 `src/generation.py`，新增 `calculate_pattern_from_data()`，用于只校验和计算展开图，不写入 DXF 文件。
- 已更新 `src/streamlit_app.py`：
  - 参数输入页会显示当前参数对应的图形预览。
  - JSON 上传页会显示上传参数对应的图形预览。
  - 参数输入页和 JSON 上传页均可下载当前参数为 JSON 模板。
  - 预览只展示外轮廓、折弯线和孔位大致位置，并明确标注仍需工程审核。
- 已更新 `README.md`，补充 Streamlit 图形预览、参数模板保存/加载、测试覆盖和当前限制说明。

本次修改的文件：

- `src/generation.py`
- `src/streamlit_app.py`
- `src/svg_preview.py`
- `tests/test_generation.py`
- `tests/test_svg_preview.py`
- `README.md`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。
- 已运行 `.venv/bin/python -m unittest discover tests`，共 `25` 个测试通过。
- 已运行 Streamlit `AppTest`，确认默认 U 型件页面和切换到平板开孔件页面均无执行异常，并能显示 `图形预览` 与 `参数模板` 区块。
- 已临时启动 `.venv/bin/streamlit run src/streamlit_app.py --server.headless true --server.port 8502`，并用浏览器确认页面包含 `图形预览`、`参数模板`、`保存参数模板 JSON` 和 `生成 DXF`。

存在问题：

- 当前 SVG 预览是 MVP 简易示意图，不包含正式尺寸线、箭头、孔表、折弯方向或图层开关。
- 参数模板当前是下载/上传 JSON 文件的轻量闭环，尚未提供本地模板库、模板命名管理或历史版本管理。

---

### 2026-05-15 FreeCAD 流程演示视频撤回与清理更新

已完成：

- 已按用户要求撤回本轮 FreeCAD 流程演示视频工作。
- 已删除最新流程演示视频项目目录 `videos/streamlit-freecad-flow/`，包括 HyperFrames 源文件、截图素材和渲染出的 MP4。
- 已删除本轮演示专用 DXF 文件：
  - `output/U_BRACKET_FLOW_A.dxf`
  - `output/FLAT_PLATE_FLOW_B.dxf`
- 已保留项目核心代码、正式示例 DXF、示例 JSON、README 和上一轮已有文件不变。

本次修改的文件：

- `AI_Sheet_Metal_Drawing_Project_Plan.md`

本次删除的文件/目录：

- `videos/streamlit-freecad-flow/`
- `output/U_BRACKET_FLOW_A.dxf`
- `output/FLAT_PLATE_FLOW_B.dxf`

测试结果：

- 已确认 `videos/streamlit-freecad-flow/` 不再存在。
- 已确认 `output/` 中仅保留正式/既有 DXF：`U_BRACKET_001.dxf`、`L_BRACKET_001.dxf`、`FLAT_PLATE_001.dxf` 和 `U_BRACKET_STREAMLIT.dxf`。

存在问题：

- 本轮不再继续制作演示视频；后续开发重心回到 Streamlit 功能和 DXF 生成能力本身。

### 2026-05-15 Streamlit 页面演示视频更新

已完成：

- 已使用 HyperFrames 捕获本地 Streamlit 页面 `http://localhost:8501`。
- 已创建 HyperFrames 视频项目 `videos/streamlit-dxf-video/`。
- 已编写 `DESIGN.md`、`SCRIPT.md`、`STORYBOARD.md` 和 `narration.txt`，用于记录网页设计基准、演示脚本和分镜。
- 已编写 `index.html` HyperFrames composition，生成 24 秒横版演示视频。
- 视频展示内容包括：参数输入、U 型件尺寸参数、共享 Python 生成流程、DXF 下载、工程师审核提示。
- 已渲染 MP4：`videos/streamlit-dxf-video/renders/streamlit-dxf-demo.mp4`。
- 已启动 HyperFrames Studio 预览服务，项目为 `streamlit-dxf-video`。

本次修改的文件：

- `videos/streamlit-dxf-demo/capture/`
- `videos/streamlit-dxf-video/DESIGN.md`
- `videos/streamlit-dxf-video/SCRIPT.md`
- `videos/streamlit-dxf-video/STORYBOARD.md`
- `videos/streamlit-dxf-video/narration.txt`
- `videos/streamlit-dxf-video/index.html`
- `videos/streamlit-dxf-video/renders/streamlit-dxf-demo.mp4`
- `videos/streamlit-dxf-video/snapshots/`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `npx hyperframes capture http://localhost:8501`，成功捕获 1 张截图、20 个资产、3 条资产描述和页面字体/颜色信息。
- 已运行 `npx hyperframes lint`，结果为 `0 errors, 0 warnings`。
- 已运行 `npx hyperframes validate`，结果为无 console error，`56` 个文本元素通过 WCAG AA。
- 已运行 `npx hyperframes inspect`，结果为 `0 layout issues across 9 samples`。
- 已运行 `npx hyperframes snapshot . --at 6.7,11.5,16.5,21.5`，已人工查看关键帧并确认字幕切换、页面截图、参数卡片和最终审核提示可读。
- 已运行 `npx hyperframes render --output renders/streamlit-dxf-demo.mp4`，成功输出 MP4。
- 已运行 `ffprobe`，确认 MP4 时长为 `24.000000` 秒，文件大小约 `3.1 MB`。

存在问题：

- 当前视频为字幕式演示，未生成语音旁白。
- 渲染时 HyperFrames 提示部分中文字体未做确定性字体映射；当前画面可正常显示，但后续如果需要严格跨机器复现，可补充本地中文字体或改用可映射字体。
- 当前视频是产品演示素材，不改变 DXF 生成逻辑或工程计算能力。

---

### 2026-05-15 Streamlit Web MVP 初版更新

已完成：

- 已根据第二阶段行动清单开始 Streamlit 参数输入和 DXF 下载界面。
- 已新增 `src/generation.py`，将 JSON/参数字典到 DXF 的生成流程抽成共享工作流，供命令行和 Web 界面共用。
- 已更新 `src/main.py`，命令行入口改为调用共享生成工作流，避免 CLI 和 Streamlit 走两套逻辑。
- 已新增 `src/streamlit_app.py`，支持手动输入 U 型件、L 型件和平板开孔件参数。
- Streamlit 界面已支持上传 JSON 参数文件、生成 DXF、显示展开尺寸摘要，并提供 DXF 下载按钮。
- 已安装并记录 `streamlit==1.50.0`。
- 已新增 `tests/test_generation.py`，覆盖共享生成工作流的成功和失败路径。
- 已更新 `README.md`，补充 Streamlit 启动命令、Web 界面能力、项目结构、测试覆盖和当前限制。

本次修改的文件：

- `src/generation.py`
- `src/main.py`
- `src/streamlit_app.py`
- `tests/test_generation.py`
- `requirements.txt`
- `README.md`
- `output/U_BRACKET_001.dxf`
- `output/U_BRACKET_STREAMLIT.dxf`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `.venv/bin/python -m unittest discover tests`，共 `22` 个测试通过。
- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。
- 已运行 `PYTHONPATH=src .venv/bin/python -c "from streamlit.testing.v1 import AppTest; ..."`，确认默认 U 型件界面和切换到平板开孔件界面均无 Streamlit 执行异常。
- 已运行 `.venv/bin/python src/main.py --input examples/u_bracket_sample.json --output-dir output`，成功生成 `output/U_BRACKET_001.dxf`。
- 已启动 `.venv/bin/streamlit run src/streamlit_app.py --server.headless true --server.port 8501`，本地页面可访问。
- 已用浏览器打开 `http://localhost:8501`，确认参数输入页可加载，点击“生成 DXF”后出现展开宽度、展开长度、折弯补偿和“下载 DXF”按钮。
- 浏览器页面生成了 `output/U_BRACKET_STREAMLIT.dxf`。

存在问题：

- Codex 内置浏览器不支持实际接收下载文件事件，因此本次只验证下载按钮出现，并通过本地输出文件确认 DXF 已生成。
- Streamlit 当前仍是 Web MVP 初版，尚未包含图形预览、参数模板保存、工程审核流、登录权限或完整尺寸标注。
- AutoCAD、FreeCAD for Windows、激光切割软件交叉验证暂未完成。

---

### 2026-05-15 命令行边界测试补强更新

已完成：

- 已补充命令行边界测试，进一步降低错误输入生成错误 DXF 的风险。
- 已新增缺失输入文件测试，确认程序输出 `Input error` 且不会生成 DXF。
- 已新增缺少必要字段测试，确认缺字段会被拦截并输出清晰错误。
- 已新增成功路径测试，确认合法 U 型件 JSON 可以生成 DXF，并输出 `Generated DXF`、`Part type`、`Flat size` 和 `Bend allowance` 摘要。
- 已更新 `README.md`，补充命令行边界测试覆盖范围。

本次修改的文件：

- `tests/test_main_cli.py`
- `README.md`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `.venv/bin/python -m unittest discover tests`，共 `20` 个测试通过。
- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。

存在问题：

- 输出目录权限异常测试暂未覆盖，因为这类测试在不同操作系统和文件系统上的行为可能不一致。
- AutoCAD、FreeCAD for Windows、激光切割软件交叉验证暂未完成。

---

### 2026-05-15 人工审核与工程假设说明更新

已完成：

- 已由用户确认当前 FreeCAD 人工审核通过。
- 当前已通过 FreeCAD 人工检查的文件包括 `output/U_BRACKET_001.dxf`、`output/L_BRACKET_001.dxf` 和 `output/FLAT_PLATE_001.dxf`。
- 已在 `README.md` 中新增“工程假设与审核责任”说明。
- 已明确当前 DXF 输出是工程师审核初稿，不是生产批准图。
- 已补充当前 MVP 假设，包括 mm 单位、平板孔坐标左下角原点、简化 bend allowance 公式、示例材料参数、折弯线含义和轻量孔标签限制。
- 已补充生产前必须由工程师确认的内容，包括材料厚度、K 因子、外轮廓尺寸、孔径孔位、折弯方向、工艺预留和目标软件图层识别。

本次修改的文件：

- `README.md`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 本次为文档更新，不涉及计算逻辑或 DXF 生成逻辑修改。
- 已计划继续运行现有测试，确认项目状态稳定。

存在问题：

- AutoCAD、FreeCAD for Windows、激光切割软件交叉验证暂未完成。
- 当前仍未包含完整 CAD 尺寸线、孔表、折弯方向标识或工艺卡。
- 当前所有计算仍是 MVP 简化假设，真实生产前必须由工程师复核。

---

### 2026-05-15 平板开孔件人工检查与孔标注更新

已完成：

- 已由用户人工确认 `output/FLAT_PLATE_001.dxf` 在 FreeCAD 中外轮廓、4 个圆孔和文字轮廓均显示正常。
- 已为平板开孔件增加轻量孔标注：每个孔旁边显示 `H1 DIA ...` 形式的孔标签。
- 已在文字信息区增加孔坐标基准：`HOLE ORIGIN: LOWER LEFT CORNER`。
- 已在文字信息区增加孔径汇总，例如 `HOLES: 4x DIA 10.00 mm`。
- 已更新 DXF 输出测试，验证孔标签、孔坐标基准和孔径汇总写入 `TEXT` 图层。
- 已更新 `README.md`，说明平板开孔件当前包含轻量孔标签，但尚未包含完整 CAD 尺寸线和孔表。

本次修改的文件：

- `src/dxf_generator.py`
- `tests/test_dxf_generator.py`
- `README.md`
- `output/FLAT_PLATE_001.dxf`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `.venv/bin/python -m unittest discover tests`，共 `17` 个测试通过。
- 已运行 `.venv/bin/python src/main.py --input examples/flat_plate_with_holes_sample.json --output-dir output`，成功生成 `output/FLAT_PLATE_001.dxf`。
- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。
- 已使用 `ezdxf.readfile()` 读回 `output/FLAT_PLATE_001.dxf`，确认 `HOLE` 图层包含 `4` 个圆孔，`TEXT` 图层包含 `11` 条普通文字实体和 `253` 条文字轮廓多段线。

存在问题：

- 当前孔标注是 MVP 轻量标注，不包含完整 CAD 尺寸线、箭头、孔距尺寸链或孔表。
- AutoCAD、FreeCAD for Windows、激光切割软件交叉验证暂未完成。
- 当前孔仅支持圆孔，不支持槽孔、沉孔、螺纹孔、倒角或圆角。

---

### 2026-05-15 平板开孔件扩展更新

已完成：

- 已新增第三种基础件：平板开孔件 `flat_plate`。
- 已新增 `CircularHole`、`FlatPlateParams` 和 `FlatPlatePattern`，支持矩形平板和圆孔列表参数。
- 已新增 `calculate_flat_plate_pattern()`，用于生成平板外轮廓和孔位结构。
- 已新增 `generate_flat_plate_dxf()`，输出平板开孔件 DXF。
- 已新增 `HOLE` 图层，用于圆孔轮廓表达。
- 已更新命令行入口 `src/main.py`，支持 `part_type: flat_plate`。
- 已新增示例文件 `examples/flat_plate_with_holes_sample.json`。
- 已生成 `output/FLAT_PLATE_001.dxf`。
- 已补充平板开孔件数学测试、孔位边界校验测试和 DXF 输出测试。
- 已更新 `README.md`，补充平板开孔件运行命令、参数格式、输出文件、`HOLE` 图层和当前限制。

本次修改的文件：

- `src/sheet_metal_math.py`
- `src/dxf_generator.py`
- `src/main.py`
- `examples/flat_plate_with_holes_sample.json`
- `tests/test_sheet_metal_math.py`
- `tests/test_dxf_generator.py`
- `tests/test_main_cli.py`
- `README.md`
- `output/U_BRACKET_001.dxf`
- `output/L_BRACKET_001.dxf`
- `output/FLAT_PLATE_001.dxf`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `.venv/bin/python -m unittest discover tests`，共 `17` 个测试通过。
- 已运行 `.venv/bin/python src/main.py --input examples/u_bracket_sample.json --output-dir output`，成功生成 `output/U_BRACKET_001.dxf`。
- 已运行 `.venv/bin/python src/main.py --input examples/l_bracket_sample.json --output-dir output`，成功生成 `output/L_BRACKET_001.dxf`。
- 已运行 `.venv/bin/python src/main.py --input examples/flat_plate_with_holes_sample.json --output-dir output`，成功生成 `output/FLAT_PLATE_001.dxf`。
- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。
- 已使用 `ezdxf.readfile()` 读回三个 DXF 文件，验证图层和实体类型。
- `output/FLAT_PLATE_001.dxf` 读回结果显示：`CUT` 图层包含 `1` 个外轮廓，`HOLE` 图层包含 `4` 个圆孔，`TEXT` 图层包含 `6` 条普通文字实体和 `141` 条文字轮廓多段线。

存在问题：

- 已由用户用 FreeCAD 人工打开 `output/FLAT_PLATE_001.dxf`，确认外轮廓、4 个圆孔和文字轮廓显示正常。
- AutoCAD、FreeCAD for Windows、激光切割软件交叉验证暂未完成。
- 当前孔仅支持圆孔，不支持槽孔、沉孔、螺纹孔、倒角或圆角。
- 当前平板开孔件已包含轻量孔标签，但暂不包含完整尺寸标注、孔表或加工说明。

---

### 2026-05-15 命令行错误路径测试更新

已完成：

- 已由用户人工确认 `output/L_BRACKET_001.dxf` 在 FreeCAD 中外轮廓、单条分段折弯线和文字轮廓显示正常。
- AutoCAD 或其他 CAD 软件交叉验证目前仍暂不具备条件，继续记录为后续验证项。
- 已新增 `tests/test_main_cli.py`，使用真实子进程调用 `src/main.py` 验证命令行错误路径。
- 已覆盖错误 JSON、未知 `part_type`、非法尺寸三类输入失败场景。
- 已确认上述失败场景会输出清晰 `Input error`，并且不会生成错误 DXF 文件。
- 已更新 `README.md`，补充命令行错误路径测试覆盖范围，并记录 U 型件和 L 型件已通过 FreeCAD 人工显示检查。

本次修改的文件：

- `tests/test_main_cli.py`
- `README.md`
- `output/U_BRACKET_001.dxf`
- `output/L_BRACKET_001.dxf`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `.venv/bin/python -m unittest discover tests`，共 `13` 个测试通过。
- 已运行 `.venv/bin/python src/main.py --input examples/u_bracket_sample.json --output-dir output`，成功生成 `output/U_BRACKET_001.dxf`。
- 已运行 `.venv/bin/python src/main.py --input examples/l_bracket_sample.json --output-dir output`，成功生成 `output/L_BRACKET_001.dxf`。
- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。

存在问题：

- AutoCAD、FreeCAD for Windows、激光切割软件交叉验证暂未完成。
- 当前命令行错误路径测试覆盖基础失败场景，尚未覆盖缺失输入文件或输出目录权限异常。
- 已支持平板开孔件和孔位图层；当前仍未支持尺寸标注或折弯方向标识。

---

### 2026-05-15 L 型件扩展更新

已完成：

- 已开始第二种基础件扩展：新增 L 型钣金件 `l_bracket`。
- 已新增 `LBracketParams` 和 `LBracketFlatPattern`，支持 L 型件参数读取、基础校验和展开尺寸计算。
- 已新增 `calculate_l_bracket_flat_pattern()`，按 MVP 简化公式计算单折弯 L 型件展开图。
- 已新增 `generate_l_bracket_dxf()`，输出 L 型件 `CUT / BEND / TEXT` 图层。
- 已更新命令行入口 `src/main.py`，支持通过 JSON 中的 `part_type` 自动选择 `u_bracket` 或 `l_bracket`。
- 已新增示例文件 `examples/l_bracket_sample.json`。
- 已生成 `output/L_BRACKET_001.dxf`。
- 已补充 L 型件数学测试和 DXF 输出测试。
- 已更新 `README.md`，补充 L 型件运行命令、参数格式、输出文件和当前限制。

本次修改的文件：

- `src/sheet_metal_math.py`
- `src/dxf_generator.py`
- `src/main.py`
- `examples/l_bracket_sample.json`
- `tests/test_sheet_metal_math.py`
- `tests/test_dxf_generator.py`
- `README.md`
- `output/U_BRACKET_001.dxf`
- `output/L_BRACKET_001.dxf`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `.venv/bin/python -m unittest discover tests`，共 `10` 个测试通过。
- 已运行 `.venv/bin/python src/main.py --input examples/u_bracket_sample.json --output-dir output`，成功生成 `output/U_BRACKET_001.dxf`。
- 已运行 `.venv/bin/python src/main.py --input examples/l_bracket_sample.json --output-dir output`，成功生成 `output/L_BRACKET_001.dxf`。
- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。
- 已使用 `ezdxf.readfile()` 读回两个 DXF 文件，验证均包含 `CUT / BEND / TEXT` 图层。
- `output/L_BRACKET_001.dxf` 读回结果显示：`BEND` 图层包含 `12` 条真实线段，`CUT` 图层包含 `1` 个外轮廓，`TEXT` 图层包含 `6` 条普通文字实体和 `159` 条文字轮廓多段线。

存在问题：

- 已由用户用 FreeCAD 人工打开 `output/L_BRACKET_001.dxf`，确认外轮廓、单条分段折弯线和文字轮廓显示正常。
- AutoCAD、FreeCAD for Windows、激光切割软件交叉验证暂未完成。
- L 型件计算仍采用 MVP 简化 bend allowance 公式，不代表真实工厂生产参数。
- 当前 L 型件暂不支持孔、槽、倒角、折弯方向标识或尺寸标注。

---

### 2026-05-15 输入校验与测试补强更新

已完成：

- 已人工确认最新 `output/U_BRACKET_001.dxf` 在 FreeCAD 中可以显示 `TEXT` 文字轮廓和 `BEND` 分段折弯线。
- AutoCAD 或其他 CAD 软件交叉验证目前暂不具备条件，已记录为后续验证项。
- 已为 `src/sheet_metal_math.py` 增加基础单元测试，覆盖 bend allowance、U 型件展开宽度、长度、折弯线位置和外轮廓坐标。
- 已为 U 型件 JSON 参数增加基础校验，包括必填字段、文本非空、数值合法性、正尺寸、K 因子范围和折弯角范围。
- 已优化 `src/main.py` 的错误输出，输入文件读取失败、JSON 格式错误或参数校验失败时会输出清晰的 `Input error`。
- 已更新 `README.md`，补充参数校验规则、测试覆盖范围和当前限制。

本次修改的文件：

- `src/sheet_metal_math.py`
- `src/main.py`
- `tests/test_sheet_metal_math.py`
- `README.md`
- `output/U_BRACKET_001.dxf`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `.venv/bin/python -m unittest discover tests`，共 `7` 个测试通过。
- 已运行 `.venv/bin/python src/main.py --input examples/u_bracket_sample.json --output-dir output`，成功重新生成 `output/U_BRACKET_001.dxf`。
- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码和测试编译检查通过。

存在问题：

- AutoCAD、FreeCAD for Windows、激光切割软件交叉验证暂未完成。
- 当前输入校验仍是 MVP 级基础校验，尚未加入材料库、厚度规格表、设备参数或工厂 K 因子表。
- 当前仍只支持简单 U 型件，尚未支持 L 型件、平板开孔件或多折弯件。
- 当前折弯展开计算仍是简化公式，所有尺寸必须由工程师审核。

---

### 2026-05-15 FreeCAD DXF 显示兼容性更新

已完成：

- 已根据 FreeCAD 人工检查结果确认：原 DXF 中 `CUT / BEND / TEXT` 图层存在，但 FreeCAD 未显示 `TEXT` 文字，且 `BEND` 虚线显示为实线。
- 已更新 `src/dxf_generator.py`：`BEND` 折弯线改为真实短线段，减少 FreeCAD 忽略 DXF 线型的问题。
- 已更新 `src/dxf_generator.py`：`TEXT` 图层保留普通文字实体，并额外生成文字轮廓多段线，增强 FreeCAD 可见性。
- 已重新生成 `output/U_BRACKET_001.dxf`。
- 已新增 `tests/test_dxf_generator.py`，用于验证 DXF 包含标准图层、分段折弯线和文字轮廓几何。
- 已更新 `README.md`，补充 FreeCAD 兼容性处理和测试命令。

本次修改的文件：

- `src/dxf_generator.py`
- `tests/test_dxf_generator.py`
- `README.md`
- `output/U_BRACKET_001.dxf`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `.venv/bin/python src/main.py --input examples/u_bracket_sample.json --output-dir output`，成功重新生成 `output/U_BRACKET_001.dxf`。
- 已运行 `.venv/bin/python -m unittest discover tests`，测试通过。
- 已运行 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src tests`，源码编译检查通过。
- 已使用 `ezdxf.readfile()` 读回 DXF，验证仍包含 `CUT / BEND / TEXT` 图层。
- 读回结果显示：`BEND` 图层包含 `24` 条真实线段，`TEXT` 图层包含 `5` 条普通文字实体和 `141` 条文字轮廓多段线。

存在问题：

- 已由用户重新用 FreeCAD 打开最新 `output/U_BRACKET_001.dxf`，确认文字轮廓和分段折弯线在界面中可见。
- 尚未在 AutoCAD、FreeCAD for Windows 或激光切割软件中交叉验证。
- 文字轮廓多段线会增加 DXF 实体数量和文件体积，但对当前 MVP 检查可接受。
- 当前折弯展开计算仍是 MVP 简化公式，不能直接视为真实生产参数。

---

### 2026-05-15 更新

已完成：

- 已在项目文件夹中创建第一阶段 Python MVP 项目结构。
- 已建立 `.venv` 虚拟环境。
- 已安装 `ezdxf==1.4.2`，并记录到 `requirements.txt`。
- 已创建 `examples/u_bracket_sample.json`，用于描述 U 型钣金件参数。
- 已创建 `src/main.py`，作为命令行入口。
- 已创建 `src/sheet_metal_math.py`，用于 bend allowance 和 U 型件展开尺寸计算。
- 已创建 `src/dxf_generator.py`，用于生成 DXF 文件和 `CUT / BEND / TEXT` 图层。
- 已生成 `output/U_BRACKET_001.dxf`。
- 已编写 `README.md`，说明项目目标、安装方式、运行命令、输入 JSON、输出位置和当前限制。

本次修改的文件：

- `README.md`
- `requirements.txt`
- `examples/u_bracket_sample.json`
- `src/main.py`
- `src/sheet_metal_math.py`
- `src/dxf_generator.py`
- `output/U_BRACKET_001.dxf`
- `AI_Sheet_Metal_Drawing_Project_Plan.md`

测试结果：

- 已运行 `.venv/bin/python src/main.py`，成功生成 `output/U_BRACKET_001.dxf`。
- 生成结果显示展开尺寸为 `188.67 x 200.00 mm`，单个折弯补偿为 `4.335 mm`。
- 已使用 `ezdxf.readfile()` 读回 `output/U_BRACKET_001.dxf`，验证 DXF 版本为 `AC1024`。
- 已验证 DXF 中存在 `BEND / CUT / TEXT` 三个图层。
- 已使用 `PYTHONPYCACHEPREFIX=/private/tmp/sheet_metal_ai_pycache .venv/bin/python -m compileall src` 完成源码编译检查。

存在问题：

- 尚未在 FreeCAD 或 AutoCAD 中进行人工视觉检查。
- 当前折弯展开计算仍是 MVP 简化公式，不能直接视为真实生产参数。
- 当前只支持 U 型钣金件，不支持 L 型件、开孔平板、多折弯件或复杂 PDF 图纸识别。
- 项目当前不是 Git 仓库，后续如果需要版本管理，可以单独初始化。

---

## 下一步行动清单

优先级从高到低：

1. 请用户在 AutoCAD / FreeCAD 中打开 `output/L_BRACKET_HOLES_001.dxf` 和 `output/U_BRACKET_HOLES_001.dxf`，人工检查带孔折弯件的 `CUT / BEND / HOLE / TEXT` 图层、孔位、折弯线和文字说明。
2. 继续增强孔到折弯线校验，区分孔边到折弯线、孔边到折弯影响区、孔边到面边界等不同规则。
3. 在 SVG 检查图和 DXF 文字中继续强化孔所属面、展开坐标和审核提示。
4. 为 Streamlit 手动输入页增加带孔 U/L 型件表单，允许直接编辑底面孔、翻边孔和最小孔到折弯距离。
5. 初始化 Git 仓库或接入现有远程仓库，开始跟踪源码、文档、测试和示例文件变更。
6. 继续扩展非规则外轮廓能力，下一步支持折边避让、折弯释放槽等高频特征。
7. 中期探索 `cut_outline` 多段线输入，让用户或后续 PDF / 三维图解析模块可以提供自由外轮廓点列，不再被固定模板限制。
8. 建立箱体 / 电缆盒产品 JSON 草案，表达底板、侧板、盖板、翻边、孔、焊接边和装配关系。
9. 设计制造约束输入结构，包括板材规格、最大切割尺寸、最大折弯长度、最小孔到折弯线距离、焊接成本和材料利用率权重。
10. 后续实现候选拆分方案生成与评分，先输出可解释推荐方案和备选方案，不追求绝对最优。
11. 请用户打开或刷新 `http://localhost:8506`，确认 Streamlit 页面可访问，并继续人工检查角部圆角、长圆槽孔和诊断预览。
12. 每次修改或确认 Streamlit 本地端口时，同步更新本计划书开头的“当前本地服务地址”区块，并在当前进度中记录。
13. 继续增强 SVG 检查图，加入孔距尺寸链、审核签名区和更清晰的折弯方向交互确认。
14. 后续探索 PDF / 三维工程图文本与视觉辅助提取，生成结构化产品 JSON 草稿，但不要影响当前 JSON 到 DXF 的稳定闭环。

---

## 后续建议

- U 型件、L 型件和平板开孔件的 AutoCAD 初步检查已完成，几何图层和标准文字正常；Mac FreeCAD 需要使用 `*_FREECAD.dxf` 轮廓文字检查版。
- 浏览器 SVG 检查图已加入主流程，用于降低用户对 CAD 软件的依赖；后续应优先增强 SVG/PDF 检查图的尺寸标注和审核版式。
- SVG 检查图的尺寸箭头已改为线内实体箭头，孔编号也已改为基于孔/槽孔外接框避让；后续新增尺寸链、孔距标注或审核签名区时，应继续保持箭头和文字不越界、不遮挡关键几何。
- 平板件已开始支持参数化 `features` 和长圆槽孔，目前可表达角部倒角、角部圆角、边缘矩形缺口、圆孔和水平/竖直长圆槽孔；这些能力已接入 Streamlit 基础表单，长圆槽孔示例已由用户人工审核通过，新加入的角部圆角仍需人工 CAD 检查，下一轮建议继续扩展折边避让。
- 当前 U 型件和 L 型件已初步支持带孔折弯模板，并已完成内部公共面定义逻辑抽象；更通用的公开多折弯件 `part_type` 仍需补齐，为箱体、电缆盒和复杂产品拆图打基础。
- 当前项目目录未初始化为 Git 仓库；建议在继续扩展模板前建立版本控制，便于追踪每次 DXF 生成逻辑、测试和文档变更。
- 电缆盒、箱体类产品应先从参数化模板切入，逐步表达多面结构、折弯关系、焊接边和装配关系，再进入自动拆件和评分。
- 拆图优化应采用“候选方案生成 + 制造约束校验 + 可解释评分”的结构，不应让 AI 单独决定生产方案。
- 非规则轮廓仍建议分两步推进：短期继续用参数化 `features` 修改基础模板，中期再支持自由 `cut_outline` 多段线；这样既能快速覆盖常见图纸，也不会过早进入复杂 PDF/AI 推断。
- 一键交付包已完成，减少用户分别下载 DXF、SVG 和 JSON 的操作成本；下一轮建议继续增强 SVG 审核图或新增更多可编辑 CAD 拆图模板。
- Streamlit 参数输入和 DXF 下载界面已具备简易图形预览、图层开关、JSON 参数模板保存/上传闭环，以及圆孔、长圆槽孔、倒角和缺口的基础表格输入；手动参数区已改为实时输入区，避免 `st.data_editor` 被 form 包裹导致平板/异形件预览不刷新。
- Streamlit 已开始提供更友好的孔坐标校验提示，并已在圆孔/槽孔表格下方显示中心坐标允许范围；当前会明确提示该范围只按基础矩形计算，若孔与倒角、缺口或异形切边相交，会显示中文几何提示和半透明红色诊断孔位。
- Streamlit 本地服务需要有进程持续运行；如果页面打不开，优先检查 `8506` 是否有监听进程，再按计划书开头命令重新启动服务。
- Streamlit 本地端口当前记录为 `8506`；后续如果端口变化，应先更新计划书开头的“当前本地服务地址”，再进行演示、截图或视频捕获。
- 演示视频工作已按用户要求暂停并清理；短期不再投入 HyperFrames 视频制作。
- 后续新增零件类型时，继续保持小步推进：先计算、再生成 DXF、再补测试、最后人工检查。
- 如果 FreeCAD 和 AutoCAD 对文字显示需求冲突，可考虑增加独立且默认关闭的 `TEXT_OUTLINE` 图层，或输出一份 PDF 检查图作为辅助。
- PDF / 三维工程图解析、AI 尺寸识别和多视图结构推断应作为后续探索模块，不应影响当前 `JSON 参数 -> Python 计算 -> DXF 输出` 的核心闭环。
- 如果后续进入真实工厂验证，应优先测试 DXF 在工程师常用 CAD 软件中的打开、编辑、保存和二次修改体验。
- 所有折弯尺寸、孔位、焊接边和工艺预留都应保持工程师审核流程，AI 和脚本输出只作为可修改初稿。
