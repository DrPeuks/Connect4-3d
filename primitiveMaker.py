from models.primitives.procedural3d import *


def createRect(
                width=2,
                depth=2,
                height=2,
                center=(0, 0., 0.),
                segments = {"width": 2, "depth": 4, "height": 3},
                open_sides = (),
                thickness=.45,
                inverted = False,
                vertex_color=None,
                hav_uvs = True,
                tex_offset= {
                    "left": (.5, .5),
                    "back": (.5, .5),
                    "bottom": (.5, .5)},
                tex_scale = {
                    "left": (.5, .5),
                    "right": (.5, .5),
                    "back": (.5, .5),
                    "front": (.5, .5),
                    "bottom": (.5, .5),
                    "top": (.5, .5)
                }
            ):

    box_maker = BoxMaker(
    center=center,
    width=width,
    depth=depth,
    height=height,
    segments=segments,
    open_sides=open_sides,
    thickness=thickness,
    inverted=inverted,
    vertex_color=vertex_color,
    has_uvs=hav_uvs,
    tex_offset=tex_offset,
    tex_scale=tex_scale
    )

    return box_maker

def createCylinder(
                bottom_center=(0, 0,0),
                top_center=(0, 0,  1),
                radius=2.,
                segments={
                    "circular": 30,
                    "axial": 5,
                    "bottom_cap": 3,
                    "top_cap": 2,
                    "slice_caps_radial": 3,
                    "slice_caps_axial": 2
                },
                smooth=True,

                rotation=60.,
                thickness=.5,
                inverted=False,
                vertex_color=(0, 0, 0, 0),
                has_uvs=True,

                tex_units={
                    "main": (6., 6.),
                    "inner_main": (6., 6.),
                    "bottom_cap": (6., 6.),
                    "top_cap": (6., 6.),
                    "slice_start_cap": (6., 6.),
                    "slice_end_cap": (6., 6.)
                },
                tex_offset={
                    "slice_start_cap": (.2, 0.)
                },
                tex_rotation={
                    "inner_main": 10.,
                    "bottom_cap": 160.,
                    "slice_start_cap": 160.,
                    "slice_end_cap": 60.
                },
                tex_scale={
                    "slice_end_cap": (1.5, 1.5)
                }
            ):



    cylinder_maker = CylinderMaker(
    bottom_center=bottom_center,
    top_center = top_center,
    radius=radius,
    segments=segments,
    smooth=smooth,
    rotation=rotation,
    thickness=thickness,
    inverted=inverted,
    vertex_color=vertex_color,
    has_uvs=has_uvs,
    tex_units=tex_units,
    tex_offset=tex_offset,
    tex_rotation=tex_rotation,
    tex_scale=tex_scale
    )

    return cylinder_maker
