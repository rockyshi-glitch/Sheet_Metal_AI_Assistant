"""Streamlit interface for parameter input and DXF download."""

from __future__ import annotations

import json
import re
from base64 import b64encode
from pathlib import Path
from typing import Any

import streamlit as st

from generation import calculate_pattern_from_data, generate_delivery_package_from_data, generate_dxf_from_data
from sheet_metal_math import (
    FlatPlateParams,
    FlatPlatePattern,
    _build_flat_plate_cut_outline,
    _flat_plate_feature_from_dict,
    _hole_from_dict,
)
from svg_preview import pattern_to_svg


PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = PROJECT_ROOT / "output"

PART_LABELS = {
    "U 型件": "u_bracket",
    "L 型件": "l_bracket",
    "平板/异形开孔件": "flat_plate",
}


def _editor_records(edited_rows: Any) -> list[dict[str, Any]]:
    if hasattr(edited_rows, "to_dict"):
        return edited_rows.to_dict("records")
    return list(edited_rows)


def _build_circle_holes(rows: list[dict[str, Any]]) -> list[dict[str, float]]:
    return [
        {"x": float(row["x"]), "y": float(row["y"]), "diameter": float(row["diameter"])}
        for row in rows
        if row.get("x") is not None and row.get("y") is not None and row.get("diameter") is not None
    ]


def _build_slot_holes(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "type": "slot",
            "x": float(row["x"]),
            "y": float(row["y"]),
            "length": float(row["length"]),
            "width": float(row["width"]),
            "orientation": str(row.get("orientation") or "horizontal"),
        }
        for row in rows
        if (
            row.get("x") is not None
            and row.get("y") is not None
            and row.get("length") is not None
            and row.get("width") is not None
        )
    ]


def _build_chamfer_features(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "type": "corner_chamfer",
            "corner": str(row["corner"]),
            "distance": float(row["distance"]),
        }
        for row in rows
        if row.get("corner") and row.get("distance") is not None
    ]


def _build_radius_features(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "type": "corner_radius",
            "corner": str(row["corner"]),
            "radius": float(row["radius"]),
        }
        for row in rows
        if row.get("corner") and row.get("radius") is not None
    ]


def _build_notch_features(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "type": "edge_notch",
            "side": str(row["side"]),
            "offset": float(row["offset"]),
            "width": float(row["width"]),
            "depth": float(row["depth"]),
        }
        for row in rows
        if (
            row.get("side")
            and row.get("offset") is not None
            and row.get("width") is not None
            and row.get("depth") is not None
        )
    ]


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _fit_range_text(label: str, min_x: float, max_x: float, min_y: float, max_y: float) -> str:
    return f"{label}: X {min_x:.2f}-{max_x:.2f} mm, Y {min_y:.2f}-{max_y:.2f} mm"


def _circle_hole_range_notes(rows: list[dict[str, Any]], plate_width: float, plate_length: float) -> list[str]:
    notes = []
    for index, row in enumerate(rows, start=1):
        diameter = _optional_float(row.get("diameter"))
        if diameter is None or diameter <= 0:
            continue
        radius = diameter / 2.0
        notes.append(_fit_range_text(f"H{index}", radius, plate_width - radius, radius, plate_length - radius))
    return notes


def _slot_hole_range_notes(rows: list[dict[str, Any]], plate_width: float, plate_length: float) -> list[str]:
    notes = []
    for index, row in enumerate(rows, start=1):
        length = _optional_float(row.get("length"))
        width = _optional_float(row.get("width"))
        if length is None or width is None or length <= 0 or width <= 0:
            continue
        orientation = str(row.get("orientation") or "horizontal").strip().lower()
        if orientation == "vertical":
            half_x = width / 2.0
            half_y = length / 2.0
        else:
            half_x = length / 2.0
            half_y = width / 2.0
        notes.append(_fit_range_text(f"S{index}", half_x, plate_width - half_x, half_y, plate_length - half_y))
    return notes


def _render_range_caption(title: str, notes: list[str]) -> None:
    if notes:
        st.caption(f"{title}: " + "；".join(notes) + "。该范围仅按基础矩形板边计算，仍需避开倒角、缺口和异形切边。")


def _feature_aware_validation_message(data: dict[str, Any]) -> str | None:
    if str(data.get("part_type", "")).strip().lower() != "flat_plate":
        return None
    try:
        FlatPlateParams.from_dict(data)
    except ValueError as exc:
        return _format_validation_error(str(exc), data)
    return None


def _invalid_hole_indexes_from_message(message: str) -> set[int]:
    matches = re.findall(r"holes\[(\d+)\]", message)
    return {int(match) for match in matches}


def _flat_plate_diagnostic_pattern(data: dict[str, Any]) -> FlatPlatePattern | None:
    if str(data.get("part_type", "")).strip().lower() != "flat_plate":
        return None
    try:
        raw_holes = data.get("holes", [])
        raw_features = data.get("features", [])
        if not isinstance(raw_holes, list) or not isinstance(raw_features, list):
            return None
        holes = [_hole_from_dict(raw_hole, index) for index, raw_hole in enumerate(raw_holes)]
        features = [
            _flat_plate_feature_from_dict(raw_feature, index)
            for index, raw_feature in enumerate(raw_features)
        ]
        plate_width = float(data["plate_width"])
        plate_length = float(data["plate_length"])
        return FlatPlatePattern(
            part_name=str(data.get("part_name", "FLAT_PLATE_DIAGNOSTIC")).strip() or "FLAT_PLATE_DIAGNOSTIC",
            material=str(data.get("material", "")),
            thickness=float(data.get("thickness", 0.0) or 0.0),
            flat_width=plate_width,
            flat_length=plate_length,
            holes=holes,
            features=features,
            cut_outline=_build_flat_plate_cut_outline(plate_width, plate_length, features),
        )
    except (KeyError, TypeError, ValueError):
        return None


def _diagnostic_svg_for_invalid_flat_plate(
    data: dict[str, Any],
    visible_layers: set[str] | None,
    error_message: str,
) -> str | None:
    pattern = _flat_plate_diagnostic_pattern(data)
    if pattern is None:
        return None
    return pattern_to_svg(
        pattern,
        visible_layers=visible_layers,
        invalid_hole_indexes=_invalid_hole_indexes_from_message(error_message),
    )


def _base_fields(default_part_name: str) -> dict[str, Any]:
    col_left, col_right = st.columns(2)
    with col_left:
        part_name = st.text_input("零件名称", value=default_part_name)
        material = st.text_input("材料", value="Aluminium 5052")
    with col_right:
        thickness = st.number_input("厚度 mm", min_value=0.01, value=2.0, step=0.1, format="%.2f")
    return {
        "part_name": part_name,
        "material": material,
        "thickness": thickness,
    }


def _bend_fields() -> dict[str, Any]:
    col_left, col_mid, col_right = st.columns(3)
    with col_left:
        inside_bend_radius = st.number_input("内折弯半径 mm", min_value=0.0, value=2.0, step=0.1, format="%.2f")
    with col_mid:
        k_factor = st.number_input("K 因子", min_value=0.0, max_value=1.0, value=0.38, step=0.01, format="%.2f")
    with col_right:
        bend_angle = st.number_input("折弯角度 deg", min_value=0.01, max_value=180.0, value=90.0, step=1.0)
    return {
        "inside_bend_radius": inside_bend_radius,
        "k_factor": k_factor,
        "bend_angle": bend_angle,
    }


def _u_bracket_form() -> dict[str, Any]:
    data = {
        "part_type": "u_bracket",
        **_base_fields("U_BRACKET_STREAMLIT"),
        **_bend_fields(),
    }
    col_left, col_mid, col_right, col_fourth = st.columns(4)
    with col_left:
        data["part_length"] = st.number_input("长度 mm", min_value=0.01, value=200.0, step=1.0)
    with col_mid:
        data["bottom_width"] = st.number_input("底宽 mm", min_value=0.01, value=100.0, step=1.0)
    with col_right:
        data["left_flange_height"] = st.number_input("左翻边 mm", min_value=0.01, value=40.0, step=1.0)
    with col_fourth:
        data["right_flange_height"] = st.number_input("右翻边 mm", min_value=0.01, value=40.0, step=1.0)
    return data


def _l_bracket_form() -> dict[str, Any]:
    data = {
        "part_type": "l_bracket",
        **_base_fields("L_BRACKET_STREAMLIT"),
        **_bend_fields(),
    }
    col_left, col_mid, col_right = st.columns(3)
    with col_left:
        data["part_length"] = st.number_input("长度 mm", min_value=0.01, value=200.0, step=1.0)
    with col_mid:
        data["base_width"] = st.number_input("底边宽度 mm", min_value=0.01, value=100.0, step=1.0)
    with col_right:
        data["flange_height"] = st.number_input("翻边高度 mm", min_value=0.01, value=40.0, step=1.0)
    return data


def _flat_plate_form() -> dict[str, Any]:
    data = {
        "part_type": "flat_plate",
        **_base_fields("FLAT_PLATE_FEATURES_STREAMLIT"),
    }
    col_left, col_right = st.columns(2)
    with col_left:
        data["plate_width"] = st.number_input("板宽 mm", min_value=0.01, value=180.0, step=1.0)
    with col_right:
        data["plate_length"] = st.number_input("板长 mm", min_value=0.01, value=110.0, step=1.0)

    st.markdown("**圆孔**")
    default_circle_holes = [
        {"x": 35.0, "y": 35.0, "diameter": 10.0},
    ]
    edited_circle_holes = st.data_editor(
        default_circle_holes,
        num_rows="dynamic",
        width="stretch",
        key="flat_plate_circle_holes",
        column_config={
            "x": st.column_config.NumberColumn("X mm", min_value=0.0, max_value=data["plate_width"], step=1.0, format="%.2f"),
            "y": st.column_config.NumberColumn("Y mm", min_value=0.0, max_value=data["plate_length"], step=1.0, format="%.2f"),
            "diameter": st.column_config.NumberColumn("孔径 mm", min_value=0.01, step=1.0, format="%.2f"),
        },
    )
    _render_range_caption(
        "圆孔中心允许范围",
        _circle_hole_range_notes(_editor_records(edited_circle_holes), data["plate_width"], data["plate_length"]),
    )

    st.markdown("**长圆槽孔**")
    default_slot_holes = [
        {"x": 130.0, "y": 72.0, "length": 34.0, "width": 10.0, "orientation": "horizontal"},
    ]
    edited_slot_holes = st.data_editor(
        default_slot_holes,
        num_rows="dynamic",
        width="stretch",
        key="flat_plate_slot_holes",
        column_config={
            "x": st.column_config.NumberColumn("中心 X mm", min_value=0.0, max_value=data["plate_width"], step=1.0, format="%.2f"),
            "y": st.column_config.NumberColumn("中心 Y mm", min_value=0.0, max_value=data["plate_length"], step=1.0, format="%.2f"),
            "length": st.column_config.NumberColumn("总长 mm", min_value=0.01, step=1.0, format="%.2f"),
            "width": st.column_config.NumberColumn("宽度 mm", min_value=0.01, step=1.0, format="%.2f"),
            "orientation": st.column_config.SelectboxColumn(
                "方向",
                options=["horizontal", "vertical"],
                required=True,
            ),
        },
    )
    _render_range_caption(
        "槽孔中心允许范围",
        _slot_hole_range_notes(_editor_records(edited_slot_holes), data["plate_width"], data["plate_length"]),
    )

    st.markdown("**角部倒角**")
    default_chamfers = [
        {"corner": "lower_left", "distance": 12.0},
        {"corner": "upper_right", "distance": 15.0},
    ]
    edited_chamfers = st.data_editor(
        default_chamfers,
        num_rows="dynamic",
        width="stretch",
        key="flat_plate_chamfers",
        column_config={
            "corner": st.column_config.SelectboxColumn(
                "角",
                options=["lower_left", "lower_right", "upper_right", "upper_left"],
                required=True,
            ),
            "distance": st.column_config.NumberColumn("倒角距离 mm", min_value=0.01, step=1.0, format="%.2f"),
        },
    )

    st.markdown("**角部圆角**")
    default_radii = [
        {"corner": "lower_right", "radius": 10.0},
    ]
    edited_radii = st.data_editor(
        default_radii,
        num_rows="dynamic",
        width="stretch",
        key="flat_plate_corner_radii",
        column_config={
            "corner": st.column_config.SelectboxColumn(
                "角",
                options=["lower_left", "lower_right", "upper_right", "upper_left"],
                required=True,
            ),
            "radius": st.column_config.NumberColumn("圆角半径 mm", min_value=0.01, step=1.0, format="%.2f"),
        },
    )

    st.markdown("**边缘矩形缺口**")
    default_notches = [
        {"side": "bottom", "offset": 70.0, "width": 28.0, "depth": 10.0},
    ]
    edited_notches = st.data_editor(
        default_notches,
        num_rows="dynamic",
        width="stretch",
        key="flat_plate_notches",
        column_config={
            "side": st.column_config.SelectboxColumn(
                "边",
                options=["bottom", "right", "top", "left"],
                required=True,
            ),
            "offset": st.column_config.NumberColumn("偏移 mm", min_value=0.0, step=1.0, format="%.2f"),
            "width": st.column_config.NumberColumn("宽度 mm", min_value=0.01, step=1.0, format="%.2f"),
            "depth": st.column_config.NumberColumn("深度 mm", min_value=0.01, step=1.0, format="%.2f"),
        },
    )

    data["holes"] = [
        *_build_circle_holes(_editor_records(edited_circle_holes)),
        *_build_slot_holes(_editor_records(edited_slot_holes)),
    ]
    features = [
        *_build_chamfer_features(_editor_records(edited_chamfers)),
        *_build_radius_features(_editor_records(edited_radii)),
        *_build_notch_features(_editor_records(edited_notches)),
    ]
    if features:
        data["features"] = features
    validation_message = _feature_aware_validation_message(data)
    if validation_message:
        st.warning(f"当前平板/异形件参数提示: {validation_message}")
    return data


def _json_upload_form() -> dict[str, Any] | None:
    uploaded_file = st.file_uploader("JSON 参数文件", type=["json"])
    if uploaded_file is None:
        return None
    try:
        return json.loads(uploaded_file.getvalue().decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        st.error(f"JSON 读取失败: {exc}")
        return None


def _template_json(data: dict[str, Any]) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2)


def _safe_template_filename(data: dict[str, Any]) -> str:
    part_name = str(data.get("part_name", "sheet_metal_template")).strip() or "sheet_metal_template"
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", part_name).strip("._")
    return f"{safe_name or 'sheet_metal_template'}_template.json"


def _safe_preview_filename(data: dict[str, Any]) -> str:
    part_name = str(data.get("part_name", "sheet_metal_preview")).strip() or "sheet_metal_preview"
    safe_name = re.sub(r"[^A-Za-z0-9_.-]+", "_", part_name).strip("._")
    return f"{safe_name or 'sheet_metal_preview'}_preview.svg"


def _hole_fit_range(data: dict[str, Any], hole_index: int, axis: str) -> tuple[float, float] | None:
    holes = data.get("holes")
    if not isinstance(holes, list) or not 0 <= hole_index < len(holes):
        return None
    hole = holes[hole_index]
    if not isinstance(hole, dict):
        return None

    plate_width = float(data.get("plate_width", 0.0) or 0.0)
    plate_length = float(data.get("plate_length", 0.0) or 0.0)
    hole_type = str(hole.get("type", "circle")).strip().lower()
    try:
        if hole_type in {"slot", "slot_hole", "obround"}:
            length = float(hole.get("length", 0.0) or 0.0)
            width = float(hole.get("width", 0.0) or 0.0)
            orientation = str(hole.get("orientation", "horizontal")).strip().lower()
            half_x = length / 2.0 if orientation == "horizontal" else width / 2.0
            half_y = width / 2.0 if orientation == "horizontal" else length / 2.0
        else:
            diameter = float(hole.get("diameter", 0.0) or 0.0)
            half_x = diameter / 2.0
            half_y = diameter / 2.0
    except (TypeError, ValueError):
        return None

    if axis == "x" and plate_width > 0:
        return half_x, plate_width - half_x
    if axis == "y" and plate_length > 0:
        return half_y, plate_length - half_y
    return None


def _format_validation_error(message: str, data: dict[str, Any] | None = None) -> str:
    hole_match = re.fullmatch(r"holes\[(\d+)\]\.([xy]) must keep the hole inside the plate\.", message)
    if hole_match:
        hole_index = int(hole_match.group(1))
        axis = hole_match.group(2)
        axis_label = "中心 X" if axis == "x" else "中心 Y"
        detail = ""
        if data:
            holes = data.get("holes")
            hole = holes[hole_index] if isinstance(holes, list) and 0 <= hole_index < len(holes) else None
            current_value = hole.get(axis) if isinstance(hole, dict) else None
            fit_range = _hole_fit_range(data, hole_index, axis)
            if current_value is not None and fit_range is not None:
                detail = f" 当前值为 {float(current_value):.2f} mm，建议范围约为 {fit_range[0]:.2f} - {fit_range[1]:.2f} mm。"
        return f"第 {hole_index + 1} 个孔/槽孔的 {axis_label} 超出板件范围，必须保证整个孔都在板内。{detail}"
    outline_match = re.fullmatch(r"holes\[(\d+)\] must keep the full hole inside the cut outline\.", message)
    if outline_match:
        hole_index = int(outline_match.group(1))
        return f"第 {hole_index + 1} 个孔/槽孔与异形外轮廓、倒角或缺口相交，必须把整个孔移到 CUT 外轮廓内部。"
    center_outline_match = re.fullmatch(r"holes\[(\d+)\] must keep the hole center inside the cut outline\.", message)
    if center_outline_match:
        hole_index = int(center_outline_match.group(1))
        return f"第 {hole_index + 1} 个孔/槽孔中心落在异形外轮廓外或被缺口切掉的区域内，请移动孔中心。"
    return message


def _render_template_download(data: dict[str, Any]) -> None:
    st.download_button(
        "保存参数模板 JSON",
        data=_template_json(data),
        file_name=_safe_template_filename(data),
        mime="application/json",
        width="stretch",
    )


def _render_delivery_package_download(data: dict[str, Any], *, key_prefix: str) -> None:
    try:
        package = generate_delivery_package_from_data(data)
    except ValueError as exc:
        st.warning(f"当前参数暂不能生成交付包: {_format_validation_error(str(exc), data)}")
        return

    st.download_button(
        "下载交付包 ZIP",
        data=package.package_bytes,
        file_name=package.package_name,
        mime="application/zip",
        width="stretch",
        key=f"{key_prefix}_download_delivery_package",
    )
    st.caption("交付包包含标准 DXF、SVG 检查图和 JSON 参数。")


def _active_preview_layers(part_type: str, key_prefix: str) -> set[str]:
    layer_options = ["CUT", "BEND", "HOLE", "TEXT"]
    applicable_layers = {"CUT", "TEXT"}
    if part_type in {"u_bracket", "u_bracket_with_holes", "l_bracket", "l_bracket_with_holes"}:
        applicable_layers.add("BEND")
    if part_type in {"u_bracket_with_holes", "l_bracket_with_holes", "flat_plate"}:
        applicable_layers.add("HOLE")

    selected_layers = set()
    columns = st.columns(len(layer_options))
    for column, layer_name in zip(columns, layer_options):
        with column:
            if st.checkbox(
                layer_name,
                value=layer_name in applicable_layers,
                disabled=layer_name not in applicable_layers,
                key=_preview_layer_key(part_type, key_prefix, layer_name),
            ):
                selected_layers.add(layer_name)
    return selected_layers


def _preview_layer_key(part_type: str, key_prefix: str, layer_name: str) -> str:
    return f"{key_prefix}_{part_type}_{layer_name.lower()}"


def _render_preview(data: dict[str, Any], visible_layers: set[str] | None = None, *, key_prefix: str) -> None:
    st.subheader("图形预览")
    try:
        result = calculate_pattern_from_data(data)
    except ValueError as exc:
        error_message = str(exc)
        st.warning(f"当前参数暂不能生成正式预览: {_format_validation_error(error_message, data)}")
        diagnostic_svg = _diagnostic_svg_for_invalid_flat_plate(data, visible_layers, error_message)
        if diagnostic_svg:
            encoded_svg = b64encode(diagnostic_svg.encode("utf-8")).decode("ascii")
            st.markdown(
                f'<img src="data:image/svg+xml;base64,{encoded_svg}" alt="invalid flat pattern diagnostic preview" style="width:100%;max-width:920px;">',
                unsafe_allow_html=True,
            )
            st.caption("红色半透明孔位表示当前参数下无法完整落在 CUT 外轮廓内部；该诊断预览不会用于 DXF 或交付包输出。")
        return

    svg = pattern_to_svg(result.pattern, visible_layers=visible_layers)
    encoded_svg = b64encode(svg.encode("utf-8")).decode("ascii")
    st.markdown(
        f'<img src="data:image/svg+xml;base64,{encoded_svg}" alt="flat pattern preview" style="width:100%;max-width:920px;">',
        unsafe_allow_html=True,
    )
    st.download_button(
        "下载 SVG 检查图",
        data=svg,
        file_name=_safe_preview_filename(data),
        mime="image/svg+xml",
        width="stretch",
        key=f"{key_prefix}_download_svg",
    )
    st.caption("预览仅用于快速检查外轮廓、折弯线和孔位大致位置，不等同于正式生产图。")


def _render_result(data: dict[str, Any]) -> None:
    try:
        result = generate_dxf_from_data(data, OUTPUT_DIR)
    except ValueError as exc:
        st.error(f"输入错误: {_format_validation_error(str(exc), data)}")
        return

    dxf_bytes = result.output_path.read_bytes()
    col_left, col_mid, col_right = st.columns(3)
    col_left.metric("展开宽度 mm", f"{result.pattern.flat_width:.2f}")
    col_mid.metric("展开长度 mm", f"{result.pattern.flat_length:.2f}")
    if hasattr(result.pattern, "bend_allowance"):
        col_right.metric("折弯补偿 mm", f"{result.pattern.bend_allowance:.3f}")
    else:
        col_right.metric("孔数量", str(len(result.pattern.holes)))

    st.download_button(
        "下载 DXF",
        data=dxf_bytes,
        file_name=result.output_path.name,
        mime="application/dxf",
        width="stretch",
    )
    st.caption("当前 DXF 是 MVP 工程师审核初稿，折弯展开仍使用简化公式。")


def main() -> None:
    st.set_page_config(page_title="Sheet Metal DXF MVP", layout="wide")
    st.title("钣金 DXF 参数生成")

    tab_manual, tab_json = st.tabs(["参数输入", "JSON 上传"])
    with tab_manual:
        selected_label = st.selectbox("零件类型", list(PART_LABELS.keys()))
        part_type = PART_LABELS[selected_label]
        if part_type == "u_bracket":
            data = _u_bracket_form()
        elif part_type == "l_bracket":
            data = _l_bracket_form()
        else:
            data = _flat_plate_form()
        submitted = st.button("生成 DXF", width="stretch", key="manual_generate_dxf")
        st.subheader("预览图层")
        visible_layers = _active_preview_layers(part_type, "manual_preview_layer")
        col_preview, col_template = st.columns([3, 1])
        with col_preview:
            _render_preview(data, visible_layers, key_prefix="manual_preview")
        with col_template:
            st.subheader("参数模板")
            _render_template_download(data)
            st.subheader("交付包")
            _render_delivery_package_download(data, key_prefix="manual_package")
        if submitted:
            _render_result(data)

    with tab_json:
        uploaded_data = _json_upload_form()
        if uploaded_data is not None:
            st.json(uploaded_data)
            uploaded_part_type = str(uploaded_data.get("part_type", "u_bracket")).strip().lower()
            st.subheader("预览图层")
            visible_layers = _active_preview_layers(uploaded_part_type, "json_preview_layer")
            col_preview, col_template = st.columns([3, 1])
            with col_preview:
                _render_preview(uploaded_data, visible_layers, key_prefix="json_preview")
            with col_template:
                st.subheader("参数模板")
                _render_template_download(uploaded_data)
                st.subheader("交付包")
                _render_delivery_package_download(uploaded_data, key_prefix="json_package")
            if st.button("从 JSON 生成 DXF", width="stretch"):
                _render_result(uploaded_data)


if __name__ == "__main__":
    main()
