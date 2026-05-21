"""Sheet metal unfolding calculations for simple MVP parts."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, isfinite, pi, sin, sqrt
from typing import Union


REQUIRED_U_BRACKET_FIELDS = (
    "part_name",
    "material",
    "thickness",
    "inside_bend_radius",
    "k_factor",
    "part_length",
    "bottom_width",
    "left_flange_height",
    "right_flange_height",
    "bend_angle",
)

REQUIRED_L_BRACKET_FIELDS = (
    "part_name",
    "material",
    "thickness",
    "inside_bend_radius",
    "k_factor",
    "part_length",
    "base_width",
    "flange_height",
    "bend_angle",
)

REQUIRED_FLAT_PLATE_FIELDS = (
    "part_name",
    "material",
    "thickness",
    "plate_width",
    "plate_length",
    "holes",
)

REQUIRED_CIRCULAR_HOLE_FIELDS = (
    "x",
    "y",
    "diameter",
)

REQUIRED_SLOT_HOLE_FIELDS = (
    "x",
    "y",
    "length",
    "width",
)

VALID_CHAMFER_CORNERS = frozenset({"lower_left", "lower_right", "upper_right", "upper_left"})
VALID_NOTCH_SIDES = frozenset({"bottom", "right", "top", "left"})
VALID_SLOT_ORIENTATIONS = frozenset({"horizontal", "vertical"})
VALID_U_BRACKET_HOLE_FACES = frozenset({"left_flange", "bottom", "right_flange"})
VALID_L_BRACKET_HOLE_FACES = frozenset({"flange", "base"})
ROUND_CORNER_SEGMENTS = 8
Point = tuple[float, float]


def _require_text(data: dict, field_name: str) -> str:
    value = data[field_name]
    text = str(value).strip()
    if not text:
        raise ValueError(f"{field_name} must not be empty.")
    return text


def _require_number(data: dict, field_name: str) -> float:
    value = data[field_name]
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field_name} must be a valid number.") from exc
    if not isfinite(number):
        raise ValueError(f"{field_name} must be a finite number.")
    return number


@dataclass(frozen=True)
class UBracketParams:
    part_name: str
    material: str
    thickness: float
    inside_bend_radius: float
    k_factor: float
    part_length: float
    bottom_width: float
    left_flange_height: float
    right_flange_height: float
    bend_angle: float

    @classmethod
    def from_dict(cls, data: dict) -> "UBracketParams":
        """Build and validate U-bracket parameters from JSON-like data."""
        missing_fields = [field_name for field_name in REQUIRED_U_BRACKET_FIELDS if field_name not in data]
        if missing_fields:
            raise ValueError(f"Missing required field(s): {', '.join(missing_fields)}.")

        params = cls(
            part_name=_require_text(data, "part_name"),
            material=_require_text(data, "material"),
            thickness=_require_number(data, "thickness"),
            inside_bend_radius=_require_number(data, "inside_bend_radius"),
            k_factor=_require_number(data, "k_factor"),
            part_length=_require_number(data, "part_length"),
            bottom_width=_require_number(data, "bottom_width"),
            left_flange_height=_require_number(data, "left_flange_height"),
            right_flange_height=_require_number(data, "right_flange_height"),
            bend_angle=_require_number(data, "bend_angle"),
        )
        params.validate()
        return params

    def validate(self) -> None:
        """Validate basic MVP geometry assumptions before DXF generation."""
        positive_fields = {
            "thickness": self.thickness,
            "part_length": self.part_length,
            "bottom_width": self.bottom_width,
            "left_flange_height": self.left_flange_height,
            "right_flange_height": self.right_flange_height,
        }
        for field_name, value in positive_fields.items():
            if value <= 0:
                raise ValueError(f"{field_name} must be greater than 0.")

        if self.inside_bend_radius < 0:
            raise ValueError("inside_bend_radius must be 0 or greater.")
        if not 0.0 <= self.k_factor <= 1.0:
            raise ValueError("k_factor must be between 0 and 1.")
        if not 0.0 < self.bend_angle <= 180.0:
            raise ValueError("bend_angle must be greater than 0 and no more than 180 degrees.")


@dataclass(frozen=True)
class UBracketWithHolesParams(UBracketParams):
    holes: list[UBracketFaceHole]
    min_hole_to_bend_distance: float = 0.0

    @classmethod
    def from_dict(cls, data: dict) -> "UBracketWithHolesParams":
        """Build and validate a U-bracket with face-owned holes from JSON-like data."""
        missing_fields = [field_name for field_name in (*REQUIRED_U_BRACKET_FIELDS, "holes") if field_name not in data]
        if missing_fields:
            raise ValueError(f"Missing required field(s): {', '.join(missing_fields)}.")

        raw_holes = data["holes"]
        if not isinstance(raw_holes, list):
            raise ValueError("holes must be a list.")

        params = cls(
            part_name=_require_text(data, "part_name"),
            material=_require_text(data, "material"),
            thickness=_require_number(data, "thickness"),
            inside_bend_radius=_require_number(data, "inside_bend_radius"),
            k_factor=_require_number(data, "k_factor"),
            part_length=_require_number(data, "part_length"),
            bottom_width=_require_number(data, "bottom_width"),
            left_flange_height=_require_number(data, "left_flange_height"),
            right_flange_height=_require_number(data, "right_flange_height"),
            bend_angle=_require_number(data, "bend_angle"),
            holes=[UBracketFaceHole.from_dict(raw_hole, index) for index, raw_hole in enumerate(raw_holes)],
            min_hole_to_bend_distance=_require_number(data, "min_hole_to_bend_distance")
            if "min_hole_to_bend_distance" in data
            else 0.0,
        )
        params.validate()
        return params

    def validate(self) -> None:
        super().validate()
        _validate_bent_plate_face_holes(
            self.holes,
            _u_bracket_face_definitions(self, bend_allowance=0.0),
            part_length=self.part_length,
            min_hole_to_bend_distance=self.min_hole_to_bend_distance,
        )


@dataclass(frozen=True)
class LBracketParams:
    part_name: str
    material: str
    thickness: float
    inside_bend_radius: float
    k_factor: float
    part_length: float
    base_width: float
    flange_height: float
    bend_angle: float

    @classmethod
    def from_dict(cls, data: dict) -> "LBracketParams":
        """Build and validate L-bracket parameters from JSON-like data."""
        missing_fields = [field_name for field_name in REQUIRED_L_BRACKET_FIELDS if field_name not in data]
        if missing_fields:
            raise ValueError(f"Missing required field(s): {', '.join(missing_fields)}.")

        params = cls(
            part_name=_require_text(data, "part_name"),
            material=_require_text(data, "material"),
            thickness=_require_number(data, "thickness"),
            inside_bend_radius=_require_number(data, "inside_bend_radius"),
            k_factor=_require_number(data, "k_factor"),
            part_length=_require_number(data, "part_length"),
            base_width=_require_number(data, "base_width"),
            flange_height=_require_number(data, "flange_height"),
            bend_angle=_require_number(data, "bend_angle"),
        )
        params.validate()
        return params

    def validate(self) -> None:
        """Validate basic MVP geometry assumptions before DXF generation."""
        positive_fields = {
            "thickness": self.thickness,
            "part_length": self.part_length,
            "base_width": self.base_width,
            "flange_height": self.flange_height,
        }
        for field_name, value in positive_fields.items():
            if value <= 0:
                raise ValueError(f"{field_name} must be greater than 0.")

        if self.inside_bend_radius < 0:
            raise ValueError("inside_bend_radius must be 0 or greater.")
        if not 0.0 <= self.k_factor <= 1.0:
            raise ValueError("k_factor must be between 0 and 1.")
        if not 0.0 < self.bend_angle <= 180.0:
            raise ValueError("bend_angle must be greater than 0 and no more than 180 degrees.")


@dataclass(frozen=True)
class LBracketWithHolesParams(LBracketParams):
    holes: list[LBracketFaceHole]
    min_hole_to_bend_distance: float = 0.0

    @classmethod
    def from_dict(cls, data: dict) -> "LBracketWithHolesParams":
        """Build and validate an L-bracket with face-owned holes from JSON-like data."""
        missing_fields = [field_name for field_name in (*REQUIRED_L_BRACKET_FIELDS, "holes") if field_name not in data]
        if missing_fields:
            raise ValueError(f"Missing required field(s): {', '.join(missing_fields)}.")

        raw_holes = data["holes"]
        if not isinstance(raw_holes, list):
            raise ValueError("holes must be a list.")

        params = cls(
            part_name=_require_text(data, "part_name"),
            material=_require_text(data, "material"),
            thickness=_require_number(data, "thickness"),
            inside_bend_radius=_require_number(data, "inside_bend_radius"),
            k_factor=_require_number(data, "k_factor"),
            part_length=_require_number(data, "part_length"),
            base_width=_require_number(data, "base_width"),
            flange_height=_require_number(data, "flange_height"),
            bend_angle=_require_number(data, "bend_angle"),
            holes=[LBracketFaceHole.from_dict(raw_hole, index) for index, raw_hole in enumerate(raw_holes)],
            min_hole_to_bend_distance=_require_number(data, "min_hole_to_bend_distance")
            if "min_hole_to_bend_distance" in data
            else 0.0,
        )
        params.validate()
        return params

    def validate(self) -> None:
        super().validate()
        _validate_bent_plate_face_holes(
            self.holes,
            _l_bracket_face_definitions(self, bend_allowance=0.0),
            part_length=self.part_length,
            min_hole_to_bend_distance=self.min_hole_to_bend_distance,
        )


@dataclass(frozen=True)
class CircularHole:
    x: float
    y: float
    diameter: float

    @classmethod
    def from_dict(cls, data: dict, index: int) -> "CircularHole":
        missing_fields = [field_name for field_name in REQUIRED_CIRCULAR_HOLE_FIELDS if field_name not in data]
        if missing_fields:
            raise ValueError(f"holes[{index}] missing required field(s): {', '.join(missing_fields)}.")

        hole = cls(
            x=_require_number(data, "x"),
            y=_require_number(data, "y"),
            diameter=_require_number(data, "diameter"),
        )
        if hole.diameter <= 0:
            raise ValueError(f"holes[{index}].diameter must be greater than 0.")
        return hole

    @property
    def radius(self) -> float:
        return self.diameter / 2.0


@dataclass(frozen=True)
class SlotHole:
    x: float
    y: float
    length: float
    width: float
    orientation: str = "horizontal"

    @classmethod
    def from_dict(cls, data: dict, index: int) -> "SlotHole":
        missing_fields = [field_name for field_name in REQUIRED_SLOT_HOLE_FIELDS if field_name not in data]
        if missing_fields:
            raise ValueError(f"holes[{index}] missing required field(s): {', '.join(missing_fields)}.")

        orientation = str(data.get("orientation", "horizontal")).strip().lower()
        if orientation not in VALID_SLOT_ORIENTATIONS:
            raise ValueError(
                f"holes[{index}].orientation must be one of: {', '.join(sorted(VALID_SLOT_ORIENTATIONS))}."
            )
        slot = cls(
            x=_require_number(data, "x"),
            y=_require_number(data, "y"),
            length=_require_number(data, "length"),
            width=_require_number(data, "width"),
            orientation=orientation,
        )
        if slot.width <= 0:
            raise ValueError(f"holes[{index}].width must be greater than 0.")
        if slot.length <= 0:
            raise ValueError(f"holes[{index}].length must be greater than 0.")
        if slot.length <= slot.width:
            raise ValueError(f"holes[{index}].length must be greater than width for a slot hole.")
        return slot

    @property
    def radius(self) -> float:
        return self.width / 2.0

    @property
    def diameter(self) -> float:
        return self.width

    @property
    def straight_length(self) -> float:
        return self.length - self.width

    @property
    def check_centers(self) -> list[Point]:
        half_straight = self.straight_length / 2.0
        if self.orientation == "horizontal":
            return [(self.x - half_straight, self.y), (self.x + half_straight, self.y)]
        return [(self.x, self.y - half_straight), (self.x, self.y + half_straight)]


Hole = Union[CircularHole, SlotHole]


def _hole_from_dict(data: dict, index: int) -> Hole:
    if not isinstance(data, dict):
        raise ValueError(f"holes[{index}] must be an object.")
    hole_type = str(data.get("type", "circle")).strip().lower()
    if hole_type in {"circle", "circular"}:
        return CircularHole.from_dict(data, index)
    if hole_type in {"slot", "slot_hole", "obround"}:
        return SlotHole.from_dict(data, index)
    raise ValueError(f"holes[{index}].type must be 'circle' or 'slot'.")


def _hole_half_extents(hole: Hole) -> tuple[float, float]:
    if isinstance(hole, SlotHole):
        half_x = hole.length / 2.0 if hole.orientation == "horizontal" else hole.width / 2.0
        half_y = hole.width / 2.0 if hole.orientation == "horizontal" else hole.length / 2.0
        return half_x, half_y
    return hole.radius, hole.radius


def _validate_hole_inside_rectangle(
    hole: Hole,
    index: int,
    *,
    width: float,
    length: float,
    field_prefix: str = "holes",
) -> None:
    half_x, half_y = _hole_half_extents(hole)
    if half_x > width / 2.0 or half_y > length / 2.0:
        raise ValueError(f"{field_prefix}[{index}] is too large for the face.")
    if not half_x <= hole.x <= width - half_x:
        raise ValueError(f"{field_prefix}[{index}].x must keep the hole inside the face.")
    if not half_y <= hole.y <= length - half_y:
        raise ValueError(f"{field_prefix}[{index}].y must keep the hole inside the face.")


@dataclass(frozen=True)
class BentPlateFaceDefinition:
    width: float
    offset_x: float
    bend_edge_sides: tuple[str, ...]


def _bend_edge_clearances(hole: Hole, *, face_width: float, bend_edge_sides: tuple[str, ...]) -> list[float]:
    half_x, _ = _hole_half_extents(hole)
    clearances = []
    if "left" in bend_edge_sides:
        clearances.append(hole.x - half_x)
    if "right" in bend_edge_sides:
        clearances.append(face_width - (hole.x + half_x))
    return clearances


def _validate_bent_plate_face_holes(
    face_holes,
    face_definitions: dict[str, BentPlateFaceDefinition],
    *,
    part_length: float,
    min_hole_to_bend_distance: float,
) -> None:
    if min_hole_to_bend_distance < 0:
        raise ValueError("min_hole_to_bend_distance must be 0 or greater.")

    for index, face_hole in enumerate(face_holes):
        face_definition = face_definitions[face_hole.face]
        _validate_hole_inside_rectangle(
            face_hole.hole,
            index,
            width=face_definition.width,
            length=part_length,
        )
        if min_hole_to_bend_distance <= 0:
            continue
        clearances = _bend_edge_clearances(
            face_hole.hole,
            face_width=face_definition.width,
            bend_edge_sides=face_definition.bend_edge_sides,
        )
        if clearances and min(clearances) < min_hole_to_bend_distance:
            raise ValueError(
                f"holes[{index}] must keep at least {min_hole_to_bend_distance:.2f} mm "
                "from bend-adjacent face edges."
            )


def _unfold_bent_plate_face_holes(
    face_holes,
    face_definitions: dict[str, BentPlateFaceDefinition],
) -> tuple[list[Hole], list[str]]:
    holes = [
        _translated_hole(face_hole.hole, face_definitions[face_hole.face].offset_x)
        for face_hole in face_holes
    ]
    hole_faces = [face_hole.face for face_hole in face_holes]
    return holes, hole_faces


def _translated_hole(hole: Hole, offset_x: float) -> Hole:
    if isinstance(hole, SlotHole):
        return SlotHole(
            x=hole.x + offset_x,
            y=hole.y,
            length=hole.length,
            width=hole.width,
            orientation=hole.orientation,
        )
    return CircularHole(x=hole.x + offset_x, y=hole.y, diameter=hole.diameter)


def _normalize_bent_plate_hole_face(
    data: dict,
    index: int,
    *,
    aliases: dict[str, str],
    valid_faces,
) -> str:
    if "face" not in data:
        raise ValueError(f"holes[{index}] missing required field(s): face.")
    face = _require_text(data, "face").lower()
    normalized_face = aliases.get(face)
    if normalized_face is None:
        raise ValueError(f"holes[{index}].face must be one of: {', '.join(sorted(valid_faces))}.")
    return normalized_face


def _normalize_u_bracket_hole_face(data: dict, index: int) -> str:
    face_aliases = {
        "left": "left_flange",
        "left_flange": "left_flange",
        "bottom": "bottom",
        "base": "bottom",
        "right": "right_flange",
        "right_flange": "right_flange",
    }
    return _normalize_bent_plate_hole_face(
        data,
        index,
        aliases=face_aliases,
        valid_faces=VALID_U_BRACKET_HOLE_FACES,
    )


@dataclass(frozen=True)
class UBracketFaceHole:
    face: str
    hole: Hole

    @classmethod
    def from_dict(cls, data: dict, index: int) -> "UBracketFaceHole":
        if not isinstance(data, dict):
            raise ValueError(f"holes[{index}] must be an object.")
        return cls(
            face=_normalize_u_bracket_hole_face(data, index),
            hole=_hole_from_dict(data, index),
        )


def _normalize_l_bracket_hole_face(data: dict, index: int) -> str:
    face_aliases = {
        "flange": "flange",
        "vertical": "flange",
        "base": "base",
        "bottom": "base",
    }
    return _normalize_bent_plate_hole_face(
        data,
        index,
        aliases=face_aliases,
        valid_faces=VALID_L_BRACKET_HOLE_FACES,
    )


@dataclass(frozen=True)
class LBracketFaceHole:
    face: str
    hole: Hole

    @classmethod
    def from_dict(cls, data: dict, index: int) -> "LBracketFaceHole":
        if not isinstance(data, dict):
            raise ValueError(f"holes[{index}] must be an object.")
        return cls(
            face=_normalize_l_bracket_hole_face(data, index),
            hole=_hole_from_dict(data, index),
        )


@dataclass(frozen=True)
class CornerChamfer:
    corner: str
    distance: float

    @classmethod
    def from_dict(cls, data: dict, index: int) -> "CornerChamfer":
        corner = _require_text(data, "corner").lower()
        if corner not in VALID_CHAMFER_CORNERS:
            raise ValueError(f"features[{index}].corner must be one of: {', '.join(sorted(VALID_CHAMFER_CORNERS))}.")
        chamfer = cls(corner=corner, distance=_require_number(data, "distance"))
        if chamfer.distance <= 0:
            raise ValueError(f"features[{index}].distance must be greater than 0.")
        return chamfer


@dataclass(frozen=True)
class EdgeNotch:
    side: str
    offset: float
    width: float
    depth: float

    @classmethod
    def from_dict(cls, data: dict, index: int) -> "EdgeNotch":
        side = _require_text(data, "side").lower()
        if side not in VALID_NOTCH_SIDES:
            raise ValueError(f"features[{index}].side must be one of: {', '.join(sorted(VALID_NOTCH_SIDES))}.")
        notch = cls(
            side=side,
            offset=_require_number(data, "offset"),
            width=_require_number(data, "width"),
            depth=_require_number(data, "depth"),
        )
        if notch.offset < 0:
            raise ValueError(f"features[{index}].offset must be 0 or greater.")
        if notch.width <= 0:
            raise ValueError(f"features[{index}].width must be greater than 0.")
        if notch.depth <= 0:
            raise ValueError(f"features[{index}].depth must be greater than 0.")
        return notch


@dataclass(frozen=True)
class CornerRadius:
    corner: str
    radius: float

    @classmethod
    def from_dict(cls, data: dict, index: int) -> "CornerRadius":
        corner = _require_text(data, "corner").lower()
        if corner not in VALID_CHAMFER_CORNERS:
            raise ValueError(f"features[{index}].corner must be one of: {', '.join(sorted(VALID_CHAMFER_CORNERS))}.")
        rounded = cls(corner=corner, radius=_require_number(data, "radius"))
        if rounded.radius <= 0:
            raise ValueError(f"features[{index}].radius must be greater than 0.")
        return rounded


FlatPlateFeature = Union[CornerChamfer, CornerRadius, EdgeNotch]


def _flat_plate_feature_from_dict(data: dict, index: int) -> FlatPlateFeature:
    if not isinstance(data, dict):
        raise ValueError(f"features[{index}] must be an object.")
    feature_type = _require_text(data, "type").lower()
    if feature_type in {"corner_chamfer", "chamfer"}:
        return CornerChamfer.from_dict(data, index)
    if feature_type in {"corner_radius", "round_corner", "radius"}:
        return CornerRadius.from_dict(data, index)
    if feature_type in {"edge_notch", "notch"}:
        return EdgeNotch.from_dict(data, index)
    raise ValueError(
        "features[{index}].type must be 'corner_chamfer', 'corner_radius', or 'edge_notch'.".format(index=index)
    )


def _remove_duplicate_close(points: list[Point]) -> list[Point]:
    if len(points) > 1 and points[0] == points[-1]:
        return points[:-1]
    return points


def _distance_to_segment(point: Point, segment_start: Point, segment_end: Point) -> float:
    px, py = point
    x1, y1 = segment_start
    x2, y2 = segment_end
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return sqrt((px - x1) ** 2 + (py - y1) ** 2)
    ratio = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    nearest_x = x1 + ratio * dx
    nearest_y = y1 + ratio * dy
    return sqrt((px - nearest_x) ** 2 + (py - nearest_y) ** 2)


def _point_inside_polygon(point: Point, polygon: list[Point]) -> bool:
    x, y = point
    inside = False
    vertices = _remove_duplicate_close(polygon)
    previous_x, previous_y = vertices[-1]
    for current_x, current_y in vertices:
        if (current_y > y) != (previous_y > y):
            intersect_x = (previous_x - current_x) * (y - current_y) / (previous_y - current_y) + current_x
            if x < intersect_x:
                inside = not inside
        previous_x, previous_y = current_x, current_y
    return inside


def _minimum_distance_to_outline(point: Point, outline: list[Point]) -> float:
    vertices = _remove_duplicate_close(outline)
    distances = [
        _distance_to_segment(point, vertices[index], vertices[(index + 1) % len(vertices)])
        for index in range(len(vertices))
    ]
    return min(distances)


def _validate_notch_ranges(
    side: str,
    notches: list[EdgeNotch],
    *,
    minimum_offset: float,
    maximum_offset: float,
) -> None:
    ordered_notches = sorted(notches, key=lambda notch: notch.offset)
    previous_end = minimum_offset
    for notch in ordered_notches:
        notch_end = notch.offset + notch.width
        if notch.offset < minimum_offset or notch_end > maximum_offset:
            raise ValueError(f"{side} edge notch must fit on the straight edge and outside chamfers.")
        if notch.offset < previous_end:
            raise ValueError(f"{side} edge notches must not overlap.")
        previous_end = notch_end


def _flat_plate_feature_maps(
    plate_width: float,
    plate_length: float,
    features: list[FlatPlateFeature],
) -> tuple[dict[str, float], dict[str, float], dict[str, list[EdgeNotch]]]:
    chamfers = {corner: 0.0 for corner in VALID_CHAMFER_CORNERS}
    round_corners = {corner: 0.0 for corner in VALID_CHAMFER_CORNERS}
    notches = {side: [] for side in VALID_NOTCH_SIDES}
    for feature in features:
        if isinstance(feature, CornerChamfer):
            if chamfers[feature.corner]:
                raise ValueError(f"Duplicate chamfer for {feature.corner}.")
            if round_corners[feature.corner]:
                raise ValueError(f"{feature.corner} cannot have both chamfer and corner radius.")
            if feature.distance >= min(plate_width, plate_length):
                raise ValueError(f"{feature.corner} chamfer is too large for the plate.")
            chamfers[feature.corner] = feature.distance
        elif isinstance(feature, CornerRadius):
            if round_corners[feature.corner]:
                raise ValueError(f"Duplicate corner radius for {feature.corner}.")
            if chamfers[feature.corner]:
                raise ValueError(f"{feature.corner} cannot have both chamfer and corner radius.")
            if feature.radius >= min(plate_width, plate_length) / 2.0:
                raise ValueError(f"{feature.corner} corner radius is too large for the plate.")
            round_corners[feature.corner] = feature.radius
        else:
            if feature.side in {"bottom", "top"} and feature.depth >= plate_length:
                raise ValueError(f"{feature.side} edge notch depth is too large for the plate.")
            if feature.side in {"left", "right"} and feature.depth >= plate_width:
                raise ValueError(f"{feature.side} edge notch depth is too large for the plate.")
            notches[feature.side].append(feature)

    clearances = {
        corner: chamfers[corner] or round_corners[corner]
        for corner in VALID_CHAMFER_CORNERS
    }
    _validate_notch_ranges(
        "bottom",
        notches["bottom"],
        minimum_offset=clearances["lower_left"],
        maximum_offset=plate_width - clearances["lower_right"],
    )
    _validate_notch_ranges(
        "right",
        notches["right"],
        minimum_offset=clearances["lower_right"],
        maximum_offset=plate_length - clearances["upper_right"],
    )
    _validate_notch_ranges(
        "top",
        notches["top"],
        minimum_offset=clearances["upper_left"],
        maximum_offset=plate_width - clearances["upper_right"],
    )
    _validate_notch_ranges(
        "left",
        notches["left"],
        minimum_offset=clearances["lower_left"],
        maximum_offset=plate_length - clearances["upper_left"],
    )
    return chamfers, round_corners, notches


def _corner_clearance(chamfers: dict[str, float], round_corners: dict[str, float], corner: str) -> float:
    return chamfers[corner] or round_corners[corner]


def _append_corner_radius(
    points: list[Point],
    *,
    center: Point,
    radius: float,
    start_degrees: float,
    end_degrees: float,
) -> None:
    if radius <= 0:
        return
    for step in range(1, ROUND_CORNER_SEGMENTS + 1):
        angle = (start_degrees + (end_degrees - start_degrees) * step / ROUND_CORNER_SEGMENTS) * pi / 180.0
        points.append((center[0] + cos(angle) * radius, center[1] + sin(angle) * radius))


def _build_flat_plate_cut_outline(plate_width: float, plate_length: float, features: list[FlatPlateFeature]) -> list[Point]:
    chamfers, round_corners, notches = _flat_plate_feature_maps(plate_width, plate_length, features)
    ll = _corner_clearance(chamfers, round_corners, "lower_left")
    lr = _corner_clearance(chamfers, round_corners, "lower_right")
    ur = _corner_clearance(chamfers, round_corners, "upper_right")
    ul = _corner_clearance(chamfers, round_corners, "upper_left")
    points: list[Point] = [(ll, 0.0) if ll else (0.0, 0.0)]

    for notch in sorted(notches["bottom"], key=lambda item: item.offset):
        points.extend(
            [
                (notch.offset, 0.0),
                (notch.offset, notch.depth),
                (notch.offset + notch.width, notch.depth),
                (notch.offset + notch.width, 0.0),
            ]
        )
    points.append((plate_width - lr, 0.0) if lr else (plate_width, 0.0))
    if round_corners["lower_right"]:
        radius = round_corners["lower_right"]
        _append_corner_radius(
            points,
            center=(plate_width - radius, radius),
            radius=radius,
            start_degrees=-90.0,
            end_degrees=0.0,
        )
    elif lr:
        points.append((plate_width, lr))

    for notch in sorted(notches["right"], key=lambda item: item.offset):
        points.extend(
            [
                (plate_width, notch.offset),
                (plate_width - notch.depth, notch.offset),
                (plate_width - notch.depth, notch.offset + notch.width),
                (plate_width, notch.offset + notch.width),
            ]
        )
    points.append((plate_width, plate_length - ur) if ur else (plate_width, plate_length))
    if round_corners["upper_right"]:
        radius = round_corners["upper_right"]
        _append_corner_radius(
            points,
            center=(plate_width - radius, plate_length - radius),
            radius=radius,
            start_degrees=0.0,
            end_degrees=90.0,
        )
    elif ur:
        points.append((plate_width - ur, plate_length))

    for notch in sorted(notches["top"], key=lambda item: item.offset, reverse=True):
        points.extend(
            [
                (notch.offset + notch.width, plate_length),
                (notch.offset + notch.width, plate_length - notch.depth),
                (notch.offset, plate_length - notch.depth),
                (notch.offset, plate_length),
            ]
        )
    points.append((ul, plate_length) if ul else (0.0, plate_length))
    if round_corners["upper_left"]:
        radius = round_corners["upper_left"]
        _append_corner_radius(
            points,
            center=(radius, plate_length - radius),
            radius=radius,
            start_degrees=90.0,
            end_degrees=180.0,
        )
    elif ul:
        points.append((0.0, plate_length - ul))

    for notch in sorted(notches["left"], key=lambda item: item.offset, reverse=True):
        points.extend(
            [
                (0.0, notch.offset + notch.width),
                (notch.depth, notch.offset + notch.width),
                (notch.depth, notch.offset),
                (0.0, notch.offset),
            ]
        )
    points.append((0.0, ll) if ll else (0.0, 0.0))
    if round_corners["lower_left"]:
        radius = round_corners["lower_left"]
        _append_corner_radius(
            points,
            center=(radius, radius),
            radius=radius,
            start_degrees=180.0,
            end_degrees=270.0,
        )
    elif ll:
        points.append(points[0])

    return points


@dataclass(frozen=True)
class FlatPlateParams:
    part_name: str
    material: str
    thickness: float
    plate_width: float
    plate_length: float
    holes: list[Hole]
    features: list[FlatPlateFeature]

    @classmethod
    def from_dict(cls, data: dict) -> "FlatPlateParams":
        """Build and validate flat plate parameters from JSON-like data."""
        missing_fields = [field_name for field_name in REQUIRED_FLAT_PLATE_FIELDS if field_name not in data]
        if missing_fields:
            raise ValueError(f"Missing required field(s): {', '.join(missing_fields)}.")

        raw_holes = data["holes"]
        if not isinstance(raw_holes, list):
            raise ValueError("holes must be a list.")

        raw_features = data.get("features", [])
        if not isinstance(raw_features, list):
            raise ValueError("features must be a list.")

        holes = [_hole_from_dict(raw_hole, index) for index, raw_hole in enumerate(raw_holes)]
        features = [
            _flat_plate_feature_from_dict(raw_feature, index)
            for index, raw_feature in enumerate(raw_features)
        ]
        params = cls(
            part_name=_require_text(data, "part_name"),
            material=_require_text(data, "material"),
            thickness=_require_number(data, "thickness"),
            plate_width=_require_number(data, "plate_width"),
            plate_length=_require_number(data, "plate_length"),
            holes=holes,
            features=features,
        )
        params.validate()
        return params

    def validate(self) -> None:
        """Validate basic flat plate and circular hole assumptions."""
        positive_fields = {
            "thickness": self.thickness,
            "plate_width": self.plate_width,
            "plate_length": self.plate_length,
        }
        for field_name, value in positive_fields.items():
            if value <= 0:
                raise ValueError(f"{field_name} must be greater than 0.")

        cut_outline = _build_flat_plate_cut_outline(self.plate_width, self.plate_length, self.features)
        for index, hole in enumerate(self.holes):
            check_points = [(hole.x, hole.y)]
            if isinstance(hole, SlotHole):
                check_points = hole.check_centers

            if hole.radius > self.plate_width / 2.0 or hole.radius > self.plate_length / 2.0:
                raise ValueError(f"holes[{index}] is too large for the plate.")
            for point_x, point_y in check_points:
                if not hole.radius <= point_x <= self.plate_width - hole.radius:
                    raise ValueError(f"holes[{index}].x must keep the hole inside the plate.")
                if not hole.radius <= point_y <= self.plate_length - hole.radius:
                    raise ValueError(f"holes[{index}].y must keep the hole inside the plate.")
                if not _point_inside_polygon((point_x, point_y), cut_outline):
                    raise ValueError(f"holes[{index}] must keep the hole center inside the cut outline.")
                if _minimum_distance_to_outline((point_x, point_y), cut_outline) < hole.radius:
                    raise ValueError(f"holes[{index}] must keep the full hole inside the cut outline.")


@dataclass(frozen=True)
class UBracketFlatPattern:
    part_name: str
    material: str
    thickness: float
    bend_allowance: float
    flat_width: float
    flat_length: float
    left_bend_x: float
    right_bend_x: float
    cut_outline: list[tuple[float, float]]


@dataclass(frozen=True)
class UBracketWithHolesFlatPattern(UBracketFlatPattern):
    holes: list[Hole]
    hole_faces: list[str]
    min_hole_to_bend_distance: float


@dataclass(frozen=True)
class LBracketFlatPattern:
    part_name: str
    material: str
    thickness: float
    bend_allowance: float
    flat_width: float
    flat_length: float
    bend_x: float
    cut_outline: list[tuple[float, float]]


@dataclass(frozen=True)
class LBracketWithHolesFlatPattern(LBracketFlatPattern):
    holes: list[Hole]
    hole_faces: list[str]
    min_hole_to_bend_distance: float


@dataclass(frozen=True)
class FlatPlatePattern:
    part_name: str
    material: str
    thickness: float
    flat_width: float
    flat_length: float
    holes: list[Hole]
    features: list[FlatPlateFeature]
    cut_outline: list[tuple[float, float]]


def _u_bracket_face_definitions(params, *, bend_allowance: float) -> dict[str, BentPlateFaceDefinition]:
    return {
        "left_flange": BentPlateFaceDefinition(
            width=params.left_flange_height,
            offset_x=0.0,
            bend_edge_sides=("right",),
        ),
        "bottom": BentPlateFaceDefinition(
            width=params.bottom_width,
            offset_x=params.left_flange_height + bend_allowance,
            bend_edge_sides=("left", "right"),
        ),
        "right_flange": BentPlateFaceDefinition(
            width=params.right_flange_height,
            offset_x=params.left_flange_height + bend_allowance + params.bottom_width + bend_allowance,
            bend_edge_sides=("left",),
        ),
    }


def _l_bracket_face_definitions(params, *, bend_allowance: float) -> dict[str, BentPlateFaceDefinition]:
    return {
        "flange": BentPlateFaceDefinition(
            width=params.flange_height,
            offset_x=0.0,
            bend_edge_sides=("right",),
        ),
        "base": BentPlateFaceDefinition(
            width=params.base_width,
            offset_x=params.flange_height + bend_allowance,
            bend_edge_sides=("left",),
        ),
    }


def calculate_bend_allowance(
    bend_angle: float,
    inside_bend_radius: float,
    k_factor: float,
    thickness: float,
) -> float:
    """Calculate bend allowance using BA = angle_rad * (R + K * T)."""
    angle_rad = bend_angle * pi / 180.0
    return angle_rad * (inside_bend_radius + k_factor * thickness)


def calculate_u_bracket_flat_pattern(params: UBracketParams) -> UBracketFlatPattern:
    """Calculate a simplified U-bracket flat pattern.

    The MVP assumes flange and bottom dimensions are straight tangent lengths.
    Each 90-degree bend contributes one bend allowance to the total flat width.
    """
    bend_allowance = calculate_bend_allowance(
        bend_angle=params.bend_angle,
        inside_bend_radius=params.inside_bend_radius,
        k_factor=params.k_factor,
        thickness=params.thickness,
    )
    flat_width = (
        params.left_flange_height
        + bend_allowance
        + params.bottom_width
        + bend_allowance
        + params.right_flange_height
    )
    flat_length = params.part_length

    left_bend_x = params.left_flange_height + bend_allowance / 2.0
    right_bend_x = params.left_flange_height + bend_allowance + params.bottom_width + bend_allowance / 2.0

    cut_outline = [
        (0.0, 0.0),
        (flat_width, 0.0),
        (flat_width, flat_length),
        (0.0, flat_length),
        (0.0, 0.0),
    ]

    return UBracketFlatPattern(
        part_name=params.part_name,
        material=params.material,
        thickness=params.thickness,
        bend_allowance=bend_allowance,
        flat_width=flat_width,
        flat_length=flat_length,
        left_bend_x=left_bend_x,
        right_bend_x=right_bend_x,
        cut_outline=cut_outline,
    )


def calculate_u_bracket_with_holes_flat_pattern(params: UBracketWithHolesParams) -> UBracketWithHolesFlatPattern:
    """Calculate a U-bracket flat pattern and place face-owned holes on the unfolded blank."""
    base_pattern = calculate_u_bracket_flat_pattern(params)
    holes, hole_faces = _unfold_bent_plate_face_holes(
        params.holes,
        _u_bracket_face_definitions(params, bend_allowance=base_pattern.bend_allowance),
    )

    return UBracketWithHolesFlatPattern(
        part_name=base_pattern.part_name,
        material=base_pattern.material,
        thickness=base_pattern.thickness,
        bend_allowance=base_pattern.bend_allowance,
        flat_width=base_pattern.flat_width,
        flat_length=base_pattern.flat_length,
        left_bend_x=base_pattern.left_bend_x,
        right_bend_x=base_pattern.right_bend_x,
        cut_outline=base_pattern.cut_outline,
        holes=holes,
        hole_faces=hole_faces,
        min_hole_to_bend_distance=params.min_hole_to_bend_distance,
    )


def calculate_l_bracket_flat_pattern(params: LBracketParams) -> LBracketFlatPattern:
    """Calculate a simplified L-bracket flat pattern.

    The MVP assumes flange and base dimensions are straight tangent lengths.
    The single bend contributes one bend allowance to the total flat width.
    """
    bend_allowance = calculate_bend_allowance(
        bend_angle=params.bend_angle,
        inside_bend_radius=params.inside_bend_radius,
        k_factor=params.k_factor,
        thickness=params.thickness,
    )
    flat_width = params.flange_height + bend_allowance + params.base_width
    flat_length = params.part_length
    bend_x = params.flange_height + bend_allowance / 2.0

    cut_outline = [
        (0.0, 0.0),
        (flat_width, 0.0),
        (flat_width, flat_length),
        (0.0, flat_length),
        (0.0, 0.0),
    ]

    return LBracketFlatPattern(
        part_name=params.part_name,
        material=params.material,
        thickness=params.thickness,
        bend_allowance=bend_allowance,
        flat_width=flat_width,
        flat_length=flat_length,
        bend_x=bend_x,
        cut_outline=cut_outline,
    )


def calculate_l_bracket_with_holes_flat_pattern(params: LBracketWithHolesParams) -> LBracketWithHolesFlatPattern:
    """Calculate an L-bracket flat pattern and place face-owned holes on the unfolded blank."""
    base_pattern = calculate_l_bracket_flat_pattern(params)
    holes, hole_faces = _unfold_bent_plate_face_holes(
        params.holes,
        _l_bracket_face_definitions(params, bend_allowance=base_pattern.bend_allowance),
    )

    return LBracketWithHolesFlatPattern(
        part_name=base_pattern.part_name,
        material=base_pattern.material,
        thickness=base_pattern.thickness,
        bend_allowance=base_pattern.bend_allowance,
        flat_width=base_pattern.flat_width,
        flat_length=base_pattern.flat_length,
        bend_x=base_pattern.bend_x,
        cut_outline=base_pattern.cut_outline,
        holes=holes,
        hole_faces=hole_faces,
        min_hole_to_bend_distance=params.min_hole_to_bend_distance,
    )


def calculate_flat_plate_pattern(params: FlatPlateParams) -> FlatPlatePattern:
    """Calculate a flat plate pattern with optional edge and corner features."""
    cut_outline = _build_flat_plate_cut_outline(params.plate_width, params.plate_length, params.features)

    return FlatPlatePattern(
        part_name=params.part_name,
        material=params.material,
        thickness=params.thickness,
        flat_width=params.plate_width,
        flat_length=params.plate_length,
        holes=params.holes,
        features=params.features,
        cut_outline=cut_outline,
    )
