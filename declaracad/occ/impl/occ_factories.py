"""
Copyright (c) 2016-2018, Jairus Martin.

Distributed under the terms of the GPL v3 License.

The full license is in the file LICENSE, distributed with this software.

Created on Sep 28, 2016

@author: jrm
"""
from enaml.qt.qt_factories import QT_FACTORIES


def occ_arc_factory():
    from .occ_draw import OccArc
    return OccArc


def occ_bezier_factory():
    from .occ_draw import OccBezier
    return OccBezier


def occ_box_factory():
    from .occ_shape import OccBox
    return OccBox


def occ_bspline_factory():
    from .occ_draw import OccBSpline
    return OccBSpline


def occ_chamfer_factory():
    from .occ_algo import OccChamfer
    return OccChamfer


def occ_circle_factory():
    from .occ_draw import OccCircle
    return OccCircle


def occ_common_factory():
    from .occ_algo import OccCommon
    return OccCommon


def occ_cone_factory():
    from .occ_shape import OccCone
    return OccCone


def occ_cut_factory():
    from .occ_algo import OccCut
    return OccCut


def occ_cylinder_factory():
    from .occ_shape import OccCylinder
    return OccCylinder


def occ_ellipse_factory():
    from .occ_draw import OccEllipse
    return OccEllipse


def occ_face_factory():
    from .occ_shape import OccFace
    return OccFace


def occ_fillet_factory():
    from .occ_algo import OccFillet
    return OccFillet


def occ_fuse_factory():
    from .occ_algo import OccFuse
    return OccFuse


def occ_half_space_factory():
    from .occ_shape import OccHalfSpace
    return OccHalfSpace


def occ_hyperbola_factory():
    from .occ_draw import OccHyperbola
    return OccHyperbola


def occ_intersection_factory():
    from .occ_algo import OccIntersection
    return OccIntersection


def occ_line_factory():
    from .occ_draw import OccLine
    return OccLine


def occ_load_shape_factory():
    from .occ_shape import OccLoadShape
    return OccLoadShape


def occ_offset_factory():
    from .occ_algo import OccOffset
    return OccOffset


def occ_offset_shape_factory():
    from .occ_algo import OccOffsetShape
    return OccOffsetShape


def occ_one_axis_factory():
    from .occ_shape import OccOneAxis
    return OccOneAxis


def occ_parabola_factory():
    from .occ_draw import OccParabola
    return OccParabola


def occ_part_factory():
    from .occ_part import OccPart
    return OccPart


def occ_pipe_factory():
    from .occ_algo import OccPipe
    return OccPipe


def occ_plane_factory():
    from .occ_draw import OccPlane
    return OccPlane


def occ_polyline_factory():
    from .occ_draw import OccPolyline
    return OccPolyline


def occ_prism_factory():
    from .occ_shape import OccPrism
    return OccPrism


def occ_raw_shape_factory():
    from .occ_shape import OccRawShape
    return OccRawShape


def occ_rectangle_factory():
    from .occ_draw import OccRectangle
    return OccRectangle


def occ_revol_factory():
    from .occ_shape import OccRevol
    return OccRevol


def occ_revolution_factory():
    from .occ_shape import OccRevolution
    return OccRevolution


def occ_segment_factory():
    from .occ_draw import OccSegment
    return OccSegment


def occ_sphere_factory():
    from .occ_shape import OccSphere
    return OccSphere


def occ_split_factory():
    from .occ_algo import OccSplit
    return OccSplit


def occ_svg_factory():
    from .occ_svg import OccSvg
    return OccSvg


def occ_sweep_factory():
    from .occ_shape import OccSweep
    return OccSweep


def occ_text_factory():
    from .occ_draw import OccText
    return OccText


def occ_thick_solid_factory():
    from .occ_algo import OccThickSolid
    return OccThickSolid


def occ_thru_sections_factory():
    from .occ_algo import OccThruSections
    return OccThruSections


def occ_torus_factory():
    from .occ_shape import OccTorus
    return OccTorus


def occ_transform_factory():
    from .occ_algo import OccTransform
    return OccTransform


def occ_trimmed_curve_factory():
    from .occ_draw import OccTrimmedCurve
    return OccTrimmedCurve


def occ_vertex_factory():
    from .occ_draw import OccVertex
    return OccVertex


def occ_wedge_factory():
    from .occ_shape import OccWedge
    return OccWedge


def occ_wire_factory():
    from .occ_draw import OccWire
    return OccWire


def occ_angle_dimension_factory():
    from .occ_dimension import OccAngleDimension
    return OccAngleDimension


def occ_length_dimension_factory():
    from .occ_dimension import OccLengthDimension
    return OccLengthDimension


def occ_diameter_dimension_factory():
    from .occ_dimension import OccDiameterDimension
    return OccDiameterDimension


def occ_radius_dimension_factory():
    from .occ_dimension import OccRadiusDimension
    return OccRadiusDimension


#: Part
OCC_FACTORIES = {
    'Part': occ_part_factory,
    'Face': occ_face_factory,
    'RawShape': occ_raw_shape_factory,
    'LoadShape': occ_load_shape_factory,

    #: Solids
    'Box': occ_box_factory,
    'Cone': occ_cone_factory,
    'Cylinder': occ_cylinder_factory,
    'Prism': occ_prism_factory,
    'Sphere': occ_sphere_factory,
    #'Sweep': occ_sweep_factory,
    'Torus': occ_torus_factory,
    'Wedge': occ_wedge_factory,

    #: Primatives
    'HalfSpace': occ_half_space_factory,
    #'OneAxis': occ_one_axis_factory,
    'Revol': occ_revol_factory,
    #'Revolution': occ_revolution_factory,

    #: Operations
    'Chamfer': occ_chamfer_factory,
    'Cut': occ_cut_factory,
    'Common': occ_common_factory,
    'Fuse': occ_fuse_factory,
    'Intersection': occ_intersection_factory,
    'Split': occ_split_factory,
    'Fillet': occ_fillet_factory,

    'OffsetShape': occ_offset_shape_factory,
    'ThickSolid': occ_thick_solid_factory,
    'Pipe': occ_pipe_factory,
    'ThruSections': occ_thru_sections_factory,
    'Transform': occ_transform_factory,

    #: Draw
    'Arc': occ_arc_factory,
    'Bezier': occ_bezier_factory,
    'BSpline': occ_bspline_factory,
    'Circle': occ_circle_factory,
    'Ellipse': occ_ellipse_factory,
    'Hyperbola': occ_hyperbola_factory,
    'Line': occ_line_factory,
    'Offset': occ_offset_factory,
    'Parabola': occ_parabola_factory,
    'Plane': occ_plane_factory,
    'Polyline': occ_polyline_factory,
    'Rectangle': occ_rectangle_factory,
    'Segment': occ_segment_factory,
    'Svg': occ_svg_factory,
    'Text': occ_text_factory,
    'TrimmedCurve': occ_trimmed_curve_factory,
    'Vertex': occ_vertex_factory,
    'Wire': occ_wire_factory,


    #: Dimensions
    'AngleDimension': occ_angle_dimension_factory,
    'LengthDimension': occ_length_dimension_factory,
    'DiameterDimension': occ_diameter_dimension_factory,
    'RadiusDimension': occ_radius_dimension_factory,
}

#: Install it
QT_FACTORIES.update(OCC_FACTORIES)

