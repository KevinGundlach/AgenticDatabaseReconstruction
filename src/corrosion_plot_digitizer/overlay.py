"""Render a visual QA overlay for raw digitized observations."""

from __future__ import annotations

from math import log, log10
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


SERIES_COLORS = ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00"]


def _axis_transform(value: float, scale: str) -> float:
    if scale == "linear":
        return value
    if value <= 0:
        raise ValueError(f"{scale} axes require positive values")
    if scale == "log10":
        return log10(value)
    if scale == "ln":
        return log(value)
    raise ValueError(f"Unsupported axis scale: {scale}")


def _axis_pixel(
    value: float, calibration: list[dict[str, float]], scale: str
) -> float:
    if len(calibration) != 2:
        raise ValueError("Linear calibration requires exactly two points")
    first, second = calibration
    transformed_value = _axis_transform(value, scale)
    transformed_first = _axis_transform(float(first["value"]), scale)
    transformed_second = _axis_transform(float(second["value"]), scale)
    value_span = transformed_second - transformed_first
    if value_span == 0:
        raise ValueError("Calibration values must differ")
    fraction = (transformed_value - transformed_first) / value_span
    return float(first["pixel"]) + fraction * (
        float(second["pixel"]) - float(first["pixel"])
    )


def render_overlay(spec: dict[str, Any], output_path: Path) -> list[str]:
    warnings: list[str] = []
    source_path = Path(spec["source_image"])
    image = Image.open(source_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    calibration = spec.get("calibration", {})

    plot_box = calibration.get("plot_box")
    if plot_box and len(plot_box) == 4:
        draw.rectangle(tuple(plot_box), outline="#00bcd4", width=2)

    x_calibration = calibration.get("x", [])
    y_calibration = calibration.get("y", [])
    legend_y = 8

    for series_index, series in enumerate(spec.get("series", [])):
        color = SERIES_COLORS[series_index % len(SERIES_COLORS)]
        label = f'{series.get("label", series.get("series_id", "series"))} [{series.get("metric", "unknown")}]'
        draw.rectangle((8, legend_y + 3, 18, legend_y + 13), fill=color)
        draw.text((23, legend_y), label, fill=color, font=ImageFont.load_default())
        legend_y += 16

        for point in series.get("points", []):
            pixel_x = point.get("pixel_x")
            pixel_y = point.get("pixel_y")
            if pixel_x is None and len(x_calibration) == 2:
                pixel_x = _axis_pixel(
                    float(point["x"]), x_calibration, spec["x_axis"]["scale"]
                )
            if pixel_y is None and len(y_calibration) == 2:
                pixel_y = _axis_pixel(
                    float(point["y"]), y_calibration, spec["y_axis"]["scale"]
                )
            if pixel_x is None or pixel_y is None:
                warnings.append(
                    f'No overlay position for {series.get("series_id")} point ({point.get("x")}, {point.get("y")})'
                )
                continue
            radius = 5
            draw.ellipse(
                (pixel_x - radius, pixel_y - radius, pixel_x + radius, pixel_y + radius),
                outline=color,
                width=2,
            )
            draw.line((pixel_x - 7, pixel_y, pixel_x + 7, pixel_y), fill=color, width=1)
            draw.line((pixel_x, pixel_y - 7, pixel_x, pixel_y + 7), fill=color, width=1)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    image.save(output_path)
    return warnings
