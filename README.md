# AI Sheet Metal Drawing Assistant

AI 辅助钣金拆图与加工图自动生成系统的第一阶段 MVP。

当前项目目标是生成可编辑、可审核、可修改的钣金 CAD 拆图初稿，帮助工程师减少从客户工程图到 CAD 拆图的重复绘图工作。

当前项目不以直接生成可上机切割的最终生产文件为目标。后续激光切割、设备参数、排版套料和上机工艺属于用户或工厂既有生产流程，不是本 MVP 的主线。

当前版本先完成最小技术闭环：

```text
JSON 参数 -> Python 折弯展开计算 -> ezdxf 生成 DXF -> FreeCAD / AutoCAD 打开检查
```

## 长期产品目标

本项目长期希望实现的不是简单地把一个参数模板导出为 DXF，而是形成一个面向复杂钣金产品的 AI 辅助拆图系统。

理想最终流程：

```text
用户提供复杂三维工程图 / PDF 工程图 / 三维设计图
↓
AI 识别尺寸、孔位、视图、结构、折弯关系和工艺备注
↓
生成结构化产品 JSON
↓
系统理解产品由哪些钣金面、折弯、孔、槽、焊接边和装配关系组成
↓
结合设备加工范围、板材规格、折弯能力、焊接成本和材料利用率生成候选拆图方案
↓
筛选满足生产条件且成本更优的推荐拆分方案
↓
输出多个可审核、可编辑的 DXF / SVG 检查图 / JSON 参数 / 工艺说明
↓
工程师审核、调整、确认
```

例如用户提交一个电缆盒三维设计图时，系统后期应能判断该产品是否可以一体展开。如果展开尺寸超过板材或设备加工范围，系统应能自动生成多种拆分方案，例如底板单独加工、侧板分件加工、局部折弯后焊接等，并按可制造性、材料利用率、折弯次数、焊接长度和零件数量进行评分。

当前阶段仍以工程师审核初稿为目标，不承诺自动给出绝对最优生产方案。更现实的长期目标是：

```text
生成满足生产约束的推荐拆图方案，并按成本、加工难度和材料利用率排序。
```

## 当前功能

- 读取 `examples/u_bracket_sample.json` 中的 U 型钣金件参数。
- 读取 `examples/u_bracket_with_holes_sample.json` 中的带孔 U 型钣金件参数。
- 读取 `examples/l_bracket_sample.json` 中的 L 型钣金件参数。
- 读取 `examples/l_bracket_with_holes_sample.json` 中的带孔 L 型钣金件参数。
- 读取 `examples/flat_plate_with_holes_sample.json` 中的平板开孔件参数。
- 读取 `examples/flat_plate_with_features_sample.json` 中的带非规则外轮廓特征平板件参数。
- 提供 Streamlit 参数输入、JSON 上传和 DXF 下载界面。
- Streamlit 界面提供简易 SVG 图形预览，用于在下载 DXF 前快速检查外轮廓、折弯线和孔位大致位置。
- Streamlit 图形预览支持 CUT / BEND / HOLE / TEXT 图层开关，便于单独检查切割轮廓、折弯线、孔位和标注。
- Streamlit 界面支持下载浏览器可打开的 SVG 检查图，包含外形尺寸线、折弯方向待确认提示和孔表，降低用户对 CAD 软件的依赖。
- SVG 检查图的尺寸文字会与尺寸线方向保持一致，尺寸箭头保持在尺寸线内部，孔编号会避开圆孔和长圆槽孔线条，图例使用短线条/孔样式加文字，减少文字与图形线条重叠。
- 当平板/异形件孔位与倒角、缺口或异形切边相交导致无法生成正式预览时，Streamlit 会尽量显示诊断预览，并用半透明红色标出无效孔位；DXF 和交付包仍会严格拦截。
- Streamlit 界面支持一键下载交付包 ZIP，包含标准 DXF、SVG 检查图和 JSON 参数。
- Streamlit 界面支持将当前参数另存为 JSON 参数模板，并可通过 JSON 上传页重新加载。
- Streamlit 平板/异形开孔件表单支持直接编辑圆孔、长圆槽孔、角部倒角、角部圆角和边缘矩形缺口，切换到该零件类型时 `HOLE` 预览图层会默认启用；孔和槽孔中心坐标会按板宽/板长限制，表格下方会显示基于基础矩形的中心坐标允许范围，并在孔与倒角、圆角、缺口或异形切边相交时显示中文提示，减少手写 JSON 的需要。
- 使用 bend allowance 公式计算折弯展开尺寸。
- 生成 `output/U_BRACKET_001.dxf`、`output/U_BRACKET_HOLES_001.dxf`、`output/L_BRACKET_001.dxf`、`output/L_BRACKET_HOLES_001.dxf` 和 `output/FLAT_PLATE_001.dxf`。
- 可额外生成 FreeCAD 检查版 `*_FREECAD.dxf`，使用文字轮廓线显示说明文字。
- 可额外生成浏览器 SVG 检查图 `*_preview.svg`，用于无 CAD 软件时快速查看外轮廓、尺寸、折弯线、孔位和孔表。
- DXF 包含 `CUT`、`BEND`、`HOLE`、`TEXT` 图层。
- `BEND` 折弯线使用真实短线段表示虚线，减少 FreeCAD 忽略 DXF 线型的问题。
- `TEXT` 图层使用标准文字实体，优先保证 AutoCAD 中信息文字清晰、无轮廓重影。
- 平板开孔件会标注孔坐标基准、孔径汇总，并在每个圆孔附近添加 `H1 DIA ...` 轻量孔标签。
- 平板件支持 `features` 参数，当前可生成角部倒角、角部圆角和边缘矩形缺口，并写入可编辑的 `CUT` 外轮廓；圆角在当前 MVP 中使用分段线近似。
- 平板件 `holes` 支持圆孔和长圆槽孔，槽孔会写入 `HOLE` 图层的真实直线和圆弧几何。
- 带孔 U 型件支持底面孔、左翻边孔和右翻边孔，带孔 L 型件支持底面孔和翻边孔；孔位会通过通用面定义逻辑从面内局部坐标换算到展开图坐标，并做最小孔到折弯影响区的 MVP 级距离校验。
- 带孔折弯件校验会同时计算孔边到所属面边界、孔边到实际折弯线和孔边到 MVP 折弯影响区边界的距离，便于输出更清楚的错误提示。
- 带孔 U/L 型件的 JSON 孔参数已复用圆孔和长圆槽孔解析逻辑，为后续通用多折弯带孔模板做准备。
- 对 U 型件、L 型件和平板开孔件 JSON 参数做基础校验，避免缺失字段、非数字、负尺寸或不合理参数继续生成图纸。
- 适合用 FreeCAD、AutoCAD 或其他 CAD 软件打开、检查和继续编辑。

## 开发环境

项目第一阶段在 macOS 上开发，后续会做 Windows 兼容验证。

已验证的基础环境：

```text
macOS
Python3
pip
venv
ezdxf
streamlit
```

## 安装

在项目根目录执行：

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## 运行

生成默认 U 型件 DXF：

```bash
.venv/bin/python src/main.py
```

运行成功后会生成：

```text
output/U_BRACKET_001.dxf
```

也可以指定输入 JSON 和输出目录：

```bash
.venv/bin/python src/main.py examples/u_bracket_sample.json
```

或使用显式参数：

```bash
.venv/bin/python src/main.py --input examples/u_bracket_sample.json --output-dir output
```

同时生成浏览器 SVG 检查图：

```bash
.venv/bin/python src/main.py --input examples/u_bracket_sample.json --output-dir output --preview-svg
```

运行成功后会生成：

```text
output/U_BRACKET_001.dxf
output/U_BRACKET_001_preview.svg
```

生成示例带孔 U 型件 DXF 和 SVG 检查图：

```bash
.venv/bin/python src/main.py --input examples/u_bracket_with_holes_sample.json --output-dir output --preview-svg
```

运行成功后会生成：

```text
output/U_BRACKET_HOLES_001.dxf
output/U_BRACKET_HOLES_001_preview.svg
```

生成示例 L 型件 DXF：

```bash
.venv/bin/python src/main.py --input examples/l_bracket_sample.json --output-dir output
```

运行成功后会生成：

```text
output/L_BRACKET_001.dxf
```

生成示例带孔 L 型件 DXF 和 SVG 检查图：

```bash
.venv/bin/python src/main.py --input examples/l_bracket_with_holes_sample.json --output-dir output --preview-svg
```

运行成功后会生成：

```text
output/L_BRACKET_HOLES_001.dxf
output/L_BRACKET_HOLES_001_preview.svg
```

生成示例平板开孔件 DXF：

```bash
.venv/bin/python src/main.py --input examples/flat_plate_with_holes_sample.json --output-dir output
```

运行成功后会生成：

```text
output/FLAT_PLATE_001.dxf
```

生成示例非规则外轮廓平板件 DXF 和 SVG 检查图：

```bash
.venv/bin/python src/main.py --input examples/flat_plate_with_features_sample.json --output-dir output --preview-svg
```

运行成功后会生成：

```text
output/FLAT_PLATE_FEATURES_001.dxf
output/FLAT_PLATE_FEATURES_001_preview.svg
```

生成 Mac FreeCAD 检查版 DXF：

```bash
.venv/bin/python src/main.py --input examples/u_bracket_sample.json --output-dir output --text-mode outline --file-suffix _FREECAD
.venv/bin/python src/main.py --input examples/l_bracket_sample.json --output-dir output --text-mode outline --file-suffix _FREECAD
.venv/bin/python src/main.py --input examples/flat_plate_with_holes_sample.json --output-dir output --text-mode outline --file-suffix _FREECAD
.venv/bin/python src/main.py --input examples/flat_plate_with_features_sample.json --output-dir output --text-mode outline --file-suffix _FREECAD
```

运行成功后会生成：

```text
output/U_BRACKET_001_FREECAD.dxf
output/L_BRACKET_001_FREECAD.dxf
output/FLAT_PLATE_001_FREECAD.dxf
output/FLAT_PLATE_FEATURES_001_FREECAD.dxf
```

启动 Streamlit 参数输入和 DXF 下载界面：

```bash
.venv/bin/streamlit run src/streamlit_app.py --server.port 8506
```

当前本地地址：

```text
http://localhost:8506
```

如果后续修改 Streamlit 端口，需要同步更新 `AI_Sheet_Metal_Drawing_Project_Plan.md` 开头的“当前本地服务地址”区块。

Web 界面当前支持手动输入 U 型件、L 型件和平板/异形开孔件参数。平板/异形开孔件可以通过表格直接编辑圆孔、长圆槽孔、角部倒角、角部圆角和边缘矩形缺口，并在孔表下方查看基础矩形中心坐标允许范围；如果孔与倒角、圆角、缺口或异形切边相交，界面会显示中文几何提示，并用半透明红色孔位给出诊断预览。界面会根据当前输入实时刷新简易图形预览，通过图层开关单独检查 CUT / BEND / HOLE / TEXT，下载 SVG 检查图，保存 JSON 参数模板，上传 JSON 参数文件，点击按钮生成 DXF，并一键下载 `DXF + SVG + JSON` 交付包。

SVG 检查图当前包含：

- 零件名称、材料、厚度和展开尺寸。
- 外形宽度和长度尺寸线，尺寸文字与尺寸线方向保持一致。
- U 型件和 L 型件的折弯线编号与 `BEND UP VERIFY` 待确认提示。
- 平板开孔件的轻量孔标签和孔表。
- CUT / BEND / HOLE 短线条或孔样式图例，避免用整句文字解释图层。

交付包 ZIP 当前包含：

- 标准 DXF，可在 AutoCAD / FreeCAD 等 CAD 软件中继续编辑。
- SVG 检查图，可直接用浏览器查看。
- JSON 参数文件，便于后续复用、修改或回溯生成来源。

## 示例参数

U 型件示例：

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

L 型件示例：

```json
{
  "part_type": "l_bracket",
  "part_name": "L_BRACKET_001",
  "material": "Aluminium 5052",
  "thickness": 2.0,
  "inside_bend_radius": 2.0,
  "k_factor": 0.38,
  "part_length": 200.0,
  "base_width": 100.0,
  "flange_height": 40.0,
  "bend_angle": 90
}
```

平板开孔件示例：

```json
{
  "part_type": "flat_plate",
  "part_name": "FLAT_PLATE_001",
  "material": "Aluminium 5052",
  "thickness": 2.0,
  "plate_width": 160.0,
  "plate_length": 100.0,
  "holes": [
    {"x": 30.0, "y": 30.0, "diameter": 10.0},
    {"x": 130.0, "y": 30.0, "diameter": 10.0},
    {"x": 30.0, "y": 70.0, "diameter": 10.0},
    {"x": 130.0, "y": 70.0, "diameter": 10.0}
  ]
}
```

非规则外轮廓平板件示例：

```json
{
  "part_type": "flat_plate",
  "part_name": "FLAT_PLATE_FEATURES_001",
  "material": "Aluminium 5052",
  "thickness": 2.0,
  "plate_width": 180.0,
  "plate_length": 110.0,
  "holes": [
    {"x": 35.0, "y": 35.0, "diameter": 10.0},
    {"type": "slot", "x": 130.0, "y": 72.0, "length": 34.0, "width": 10.0, "orientation": "horizontal"}
  ],
  "features": [
    {"type": "corner_chamfer", "corner": "lower_left", "distance": 12.0},
    {"type": "corner_radius", "corner": "lower_right", "radius": 10.0},
    {"type": "corner_chamfer", "corner": "upper_right", "distance": 15.0},
    {"type": "edge_notch", "side": "bottom", "offset": 70.0, "width": 28.0, "depth": 10.0}
  ]
}
```

带孔 U 型件示例：

```json
{
  "part_type": "u_bracket_with_holes",
  "part_name": "U_BRACKET_HOLES_001",
  "material": "Aluminium 5052",
  "thickness": 2.0,
  "inside_bend_radius": 2.0,
  "k_factor": 0.38,
  "part_length": 200.0,
  "bottom_width": 100.0,
  "left_flange_height": 40.0,
  "right_flange_height": 40.0,
  "bend_angle": 90,
  "min_hole_to_bend_distance": 8.0,
  "holes": [
    {"face": "bottom", "x": 50.0, "y": 60.0, "diameter": 12.0},
    {"face": "bottom", "x": 50.0, "y": 140.0, "diameter": 12.0},
    {"face": "left_flange", "x": 18.0, "y": 100.0, "diameter": 8.0},
    {"face": "right_flange", "x": 22.0, "y": 100.0, "diameter": 8.0}
  ]
}
```

U 型件必填字段：

```text
part_name, material, thickness, inside_bend_radius, k_factor,
part_length, bottom_width, left_flange_height, right_flange_height, bend_angle
```

带孔 U 型件必填字段：

```text
part_type, part_name, material, thickness, inside_bend_radius, k_factor,
part_length, bottom_width, left_flange_height, right_flange_height, bend_angle, holes
```

带孔 U 型件 `holes` 每一项还需要 `face` 字段，当前支持：

```text
left_flange, bottom, right_flange
```

其中 `x`、`y` 是该孔在所属面内的局部坐标，程序会自动换算成展开图坐标。`min_hole_to_bend_distance` 是可选字段，用于限制孔边到 MVP 折弯影响区边界的最小距离，当前不是完整生产级折弯变形校验。孔参数当前复用平板件的圆孔和长圆槽孔结构。

L 型件必填字段：

```text
part_type, part_name, material, thickness, inside_bend_radius, k_factor,
part_length, base_width, flange_height, bend_angle
```

带孔 L 型件示例：

```json
{
  "part_type": "l_bracket_with_holes",
  "part_name": "L_BRACKET_HOLES_001",
  "material": "Aluminium 5052",
  "thickness": 2.0,
  "inside_bend_radius": 2.0,
  "k_factor": 0.38,
  "part_length": 200.0,
  "base_width": 100.0,
  "flange_height": 40.0,
  "bend_angle": 90,
  "min_hole_to_bend_distance": 8.0,
  "holes": [
    {"face": "base", "x": 50.0, "y": 60.0, "diameter": 12.0},
    {"face": "base", "x": 50.0, "y": 140.0, "diameter": 12.0},
    {"face": "flange", "x": 18.0, "y": 100.0, "diameter": 8.0}
  ]
}
```

带孔 L 型件必填字段：

```text
part_type, part_name, material, thickness, inside_bend_radius, k_factor,
part_length, base_width, flange_height, bend_angle, holes
```

带孔 L 型件 `holes` 每一项还需要 `face` 字段，当前支持：

```text
flange, base
```

其中 `x`、`y` 是该孔在所属面内的局部坐标，孔参数当前复用平板件的圆孔和长圆槽孔结构。

平板开孔件必填字段：

```text
part_type, part_name, material, thickness, plate_width, plate_length, holes
```

平板件可选字段：

```text
features
```

`holes` 当前支持：

| 类型 | 必填字段 | 说明 |
| --- | --- | --- |
| `circle` 或省略 `type` | `x`, `y`, `diameter` | 圆孔，兼容早期 JSON |
| `slot` | `x`, `y`, `length`, `width` | 长圆槽孔，`orientation` 可选 `horizontal` 或 `vertical`，默认 `horizontal` |

`features` 当前支持：

| 类型 | 必填字段 | 说明 |
| --- | --- | --- |
| `corner_chamfer` | `corner`, `distance` | 角部倒角，`corner` 可为 `lower_left`、`lower_right`、`upper_right`、`upper_left` |
| `corner_radius` | `corner`, `radius` | 角部圆角，`corner` 可为 `lower_left`、`lower_right`、`upper_right`、`upper_left`；当前以分段线近似圆弧 |
| `edge_notch` | `side`, `offset`, `width`, `depth` | 边缘矩形缺口，`side` 可为 `bottom`、`right`、`top`、`left`；`offset` 沿该边从左下基准方向计量 |
 

`part_type` 当前支持：

```text
u_bracket
u_bracket_with_holes
l_bracket
l_bracket_with_holes
flat_plate
```

如果 JSON 中不写 `part_type`，程序会按 `u_bracket` 处理，以兼容第一版 U 型件示例。

当前基础校验规则：

- `part_name` 和 `material` 不能为空。
- `thickness`、`part_length` 和零件宽度/翻边类尺寸必须大于 0。
- 平板开孔件的 `plate_width`、`plate_length` 必须大于 0，`holes` 必须是列表。
- 圆孔需要 `x`、`y`、`diameter`，孔直径必须大于 0，孔必须完整落在板材外轮廓内。
- 长圆槽孔需要 `x`、`y`、`length`、`width`，`length` 必须大于 `width`，槽孔必须完整落在板材外轮廓内。
- 带孔 U 型件和带孔 L 型件的孔需要 `face` 字段，孔必须完整落在所属面内；如果设置 `min_hole_to_bend_distance`，圆孔或长圆槽孔的孔边必须避开 MVP 折弯影响区边界。程序会在错误信息中区分孔边到折弯线和到所属面边界的距离。
- 平板件 `features` 如果存在，必须是列表；倒角、圆角和边缘缺口必须落在板材范围内；同一角不能同时设置倒角和圆角，缺口不能互相重叠，也不能压到相邻倒角或圆角。
- 带 `features` 的平板件会按最终 `CUT` 外轮廓校验孔位，避免孔落在已切除的缺口区域。
- `inside_bend_radius` 必须大于等于 0。
- `k_factor` 必须在 0 到 1 之间。
- `bend_angle` 必须大于 0 且不超过 180 度。

## 折弯展开公式

```text
BA = angle_rad x (inside_bend_radius + k_factor x thickness)
angle_rad = bend_angle x pi / 180
```

当前 MVP 假设左右翻边高度和底部宽度均为直线切点之间的尺寸，每个 90 度折弯向展开宽度贡献一个 bend allowance。

## 输出图层

| 图层 | 用途 |
| --- | --- |
| CUT | 外轮廓切割线 |
| BEND | 折弯线，当前以分段线模拟虚线，增强 CAD 查看兼容性 |
| HOLE | 圆孔轮廓 |
| TEXT | 零件信息、材料、厚度、展开尺寸、孔径摘要和轻量孔标签；当前使用标准文字实体，避免 AutoCAD 中普通文字和轮廓文字叠加 |

## 文字输出模式

不同 CAD 软件对 DXF 文字支持不一致，当前提供两种文字模式：

| 模式 | 命令参数 | 适用场景 | 说明 |
| --- | --- | --- | --- |
| standard | `--text-mode standard` | Windows AutoCAD / 常规 CAD 检查 | 使用标准 `TEXT` 实体，文字清晰且不会产生轮廓重影 |
| outline | `--text-mode outline` | Mac FreeCAD 检查 | 使用文字轮廓 `LWPOLYLINE`，避免 FreeCAD 不显示标准 `TEXT` |

建议：

- 发给 AutoCAD 或工厂软件时，优先使用默认标准版，例如 `output/U_BRACKET_001.dxf`。
- 用 Mac FreeCAD 查看说明文字时，打开 FreeCAD 检查版，例如 `output/U_BRACKET_001_FREECAD.dxf`。

## 工程假设与审核责任

当前 DXF 输出是工程师审核和继续编辑的 CAD 初稿，不能直接视为生产批准图或上机切割文件。

当前 MVP 假设：

- 坐标单位为 mm。
- 平板开孔件孔坐标以左下角为原点。
- 平板件 `edge_notch.offset` 以对应边的左下基准方向计量：底边/顶边按 X 方向，左边/右边按 Y 方向。
- 平板件 `corner_radius` 当前在 DXF/SVG 中按固定分段线近似圆弧，适合作为可审核初稿；生产前仍需工程师确认圆角半径和 CAD 表达方式。
- 长圆槽孔 `x`、`y` 表示槽孔中心点；`length` 表示槽孔总长，`width` 表示两端圆弧直径。
- U 型件和 L 型件的折弯展开使用简化 bend allowance 公式。
- 示例材料、厚度、内 R 和 K 因子仅用于测试工程闭环。
- 折弯线仅表示展开图上的折弯位置，不包含完整折弯方向、刀具、模具、回弹或工艺补偿信息。
- 孔标注为轻量标签，不等同于完整孔表或正式尺寸链。

生产前必须由工程师确认：

- 材料牌号、厚度、内折弯半径和 K 因子是否符合工厂设备。
- 外轮廓尺寸、展开尺寸、孔径、孔位和孔坐标基准是否正确。
- 折弯方向、折弯顺序、焊接边、打磨、喷涂和其他工艺预留是否完整。
- `CUT`、`BEND`、`HOLE`、`TEXT` 图层是否能被目标 CAD 软件正确识别和编辑。
- 工程师是否已在自己的 CAD 流程中完成修改、确认和后续生产准备。

## 项目结构

```text
Sheet_Metal_AI_Assistant/
├── README.md
├── requirements.txt
├── AI_Sheet_Metal_Drawing_Project_Plan.md
├── examples/
│   ├── u_bracket_sample.json
│   ├── u_bracket_with_holes_sample.json
│   ├── l_bracket_sample.json
│   ├── l_bracket_with_holes_sample.json
│   ├── flat_plate_with_holes_sample.json
│   └── flat_plate_with_features_sample.json
├── output/
│   ├── U_BRACKET_001.dxf
│   ├── U_BRACKET_HOLES_001.dxf
│   ├── L_BRACKET_001.dxf
│   ├── L_BRACKET_HOLES_001.dxf
│   ├── FLAT_PLATE_001.dxf
│   ├── FLAT_PLATE_FEATURES_001.dxf
│   ├── U_BRACKET_001_FREECAD.dxf
│   ├── L_BRACKET_001_FREECAD.dxf
│   ├── FLAT_PLATE_001_FREECAD.dxf
│   ├── FLAT_PLATE_FEATURES_001_FREECAD.dxf
│   ├── U_BRACKET_001_preview.svg
│   ├── U_BRACKET_HOLES_001_preview.svg
│   ├── L_BRACKET_001_preview.svg
│   ├── L_BRACKET_HOLES_001_preview.svg
│   ├── FLAT_PLATE_001_preview.svg
│   └── FLAT_PLATE_FEATURES_001_preview.svg
├── src/
│   ├── main.py
│   ├── generation.py
│   ├── streamlit_app.py
│   ├── svg_preview.py
│   ├── sheet_metal_math.py
│   └── dxf_generator.py
└── tests/
    ├── test_generation.py
    ├── test_streamlit_app.py
    ├── test_svg_preview.py
    ├── test_dxf_generator.py
    ├── test_main_cli.py
    └── test_sheet_metal_math.py
```

## 测试

```bash
.venv/bin/python -m unittest discover tests
```

当前测试覆盖：

- bend allowance 简化公式。
- 共享生成工作流。
- Streamlit 图形预览所用的 SVG 渲染辅助逻辑。
- Streamlit 平板/异形开孔件表单的圆孔、长圆槽孔和 `features` 参数转换逻辑。
- SVG 预览图层显示/隐藏逻辑。
- CLI 和 Streamlit 使用的 SVG 检查图导出逻辑。
- Streamlit 一键交付包 ZIP 生成逻辑。
- SVG 检查图中的外形尺寸线、折弯方向待确认提示和孔表。
- U 型件、带孔 U 型件、L 型件、带孔 L 型件和平板开孔件的展开尺寸、折弯线或孔位。
- 带孔 U 型件和带孔 L 型件的面归属、展开孔位坐标、圆孔/长圆槽孔到折弯线和 MVP 折弯影响区的距离校验、DXF HOLE 图层和 SVG 预览。
- 平板件角部倒角、角部圆角、边缘缺口和最终外轮廓孔位校验。
- 平板件长圆槽孔参数校验、DXF 直线/圆弧输出和 SVG 预览。
- JSON 参数缺失和非法值校验。
- 命令行边界路径，包括错误 JSON、未知 `part_type`、非法尺寸、缺失输入文件、缺少必要字段、位置参数输入和成功生成输出摘要。
- U 型件、L 型件和平板开孔件 DXF 图层、分段折弯线、圆孔、AutoCAD 友好的标准文字实体和 FreeCAD 友好的文字轮廓模式。

## 当前限制

- 折弯展开公式仍是第一阶段 MVP 简化公式，不能直接视为生产参数。
- 孔到折弯校验已能区分折弯线、折弯影响区和所属面边界，但折弯影响区仍按 MVP 简化模型处理，尚未接入材料、模具、下模开口、回弹和工厂经验表。
- AutoCAD 已人工确认 U 型件、L 型件和平板开孔件的外轮廓、折弯虚线、孔图层和标准文字显示正常。
- 用户已人工确认带角部倒角、边缘缺口和长圆槽孔的平板件示例审核通过；新加入的角部圆角仍需人工 CAD 检查。
- Mac FreeCAD 对标准 `TEXT` 显示不稳定；需要使用 `*_FREECAD.dxf` 检查版查看文字轮廓。
- 当前支持简单 U 型件、L 型件、平板开孔件，以及带角部倒角、角部圆角、边缘矩形缺口和长圆槽孔的平板件；尚不支持多折弯件或复杂 PDF 图纸识别。
- 当前已新增带孔 U 型件和带孔 L 型件，并已将面内孔校验、孔到折弯线/折弯影响区的距离校验和展开坐标换算抽象为内部通用逻辑；公开的通用多折弯 `part_type`、箱体类面归属和复杂多面结构仍未实现。
- 当前尚未支持电缆盒、箱体类产品的多面展开、零件拆分、焊接边定义、装配关系和拆图方案评分。
- 当前尚未引入设备加工范围、板材标准规格、最大折弯长度、最小孔到折弯线距离、焊接成本、材料利用率等生产约束。
- 当前非规则外轮廓先采用“基础矩形 + 可编辑特征”的方式推进；后续仍需要支持折边避让和自由 `cut_outline` 多段线。
- Streamlit 界面是第二阶段 Web MVP 初版，已包含简易图形预览、SVG 检查图下载、预览图层开关和 JSON 参数模板保存/加载，但尚未包含登录权限、工程审核流、签核记录或模板库管理。
- 平板开孔件当前在 SVG 检查图中包含孔表，但 DXF 内仍只有轻量孔标签，不包含完整 CAD 尺寸线、箭头或孔距尺寸链。
- 生成的 DXF 是工程师审核和编辑初稿，不是可直接投产或上机切割文件。

## 下一步

- 为 Streamlit 手动输入页增加带孔 U/L 型件表单，允许直接编辑底面孔、翻边孔和最小孔到折弯距离。
- 继续强化带孔折弯件的审核表达，在 SVG 检查图和 DXF 文字中显示孔所属面、展开坐标和孔到折弯风险提示。
- 继续扩展非规则外轮廓的参数化特征，下一步优先考虑折边避让和折弯释放槽。
- 中期在 JSON 和几何计算中引入自由 `cut_outline` 概念，让输出不再局限于“基础矩形 + 特征”。
- 中期建立箱体 / 电缆盒参数模板，表达底板、侧板、翻边、孔、焊接边和装配关系。
- 长期建立拆图方案生成与评分模块，根据设备尺寸、板材规格、折弯能力、焊接成本和材料利用率推荐可制造方案。
- 继续增强 SVG 检查图，加入孔距尺寸链、审核签名区和更清晰的折弯方向交互确认。
- 为参数模板增加模板库管理，例如保存到 `templates/`、重命名、加载和删除模板。
- 后续探索 PDF / 三维工程图文本与视觉辅助提取，生成结构化产品 JSON 草稿。
