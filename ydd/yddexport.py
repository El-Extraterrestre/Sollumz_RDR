import bpy
from ..cwxml.drawable import DrawableDictionary, RDR2DrawableDictionary
from ..ydr.ydrexport import create_drawable_xml, write_embedded_textures
from ..tools import jenkhash
from ..sollumz_properties import SollumType, SollumzGame, import_export_current_game as current_game, set_import_export_current_game
from ..sollumz_preferences import get_export_settings


def export_ydd(ydd_obj: bpy.types.Object, filepath: str) -> bool:
    export_settings = get_export_settings()

    ydd_xml = create_ydd_xml(ydd_obj, export_settings.exclude_skeleton)

    write_embedded_textures(ydd_obj, filepath)

    ydd_xml.write_xml(filepath)
    return True


def create_ydd_xml(ydd_obj: bpy.types.Object, exclude_skeleton: bool = False):
    set_import_export_current_game(ydd_obj.sollum_game_type)

    if current_game() == SollumzGame.GTA:
        ydd_xml = DrawableDictionary()
    elif current_game() == SollumzGame.RDR:
        ydd_xml = RDR2DrawableDictionary()

    ydd_armature = find_ydd_armature(
        ydd_obj) if ydd_obj.type != "ARMATURE" else ydd_obj

    for child in ydd_obj.children:
        if child.sollum_type != SollumType.DRAWABLE:
            continue

        if child.type != "ARMATURE":
            armature_obj = ydd_armature
        else:
            armature_obj = None

        drawable_xml = create_drawable_xml(child, armature_obj=armature_obj)
        drawable_xml.name = drawable_xml.name + ".#dd"

        if exclude_skeleton or child.type != "ARMATURE":
            drawable_xml.skeleton = None

        if current_game() == SollumzGame.GTA:
            ydd_xml.append(drawable_xml)
        elif current_game() == SollumzGame.RDR:
            ydd_xml.drawables.append(drawable_xml)

    if current_game() == SollumzGame.GTA:
        ydd_xml.sort(key=get_hash)
    elif current_game() == SollumzGame.RDR:
        ydd_xml.drawables.sort(key=rdr_get_hash_literal)

    return ydd_xml


def find_ydd_armature(ydd_obj: bpy.types.Object):
    """Find first drawable with an armature in ``ydd_obj``."""
    for child in ydd_obj.children:
        if child.type == "ARMATURE":
            return child


def get_hash(item):
    return jenkhash.name_to_hash(item.name.split(".")[0])

def rdr_get_hash_literal(item):
    return jenkhash.name_to_hash_literal(item.hash)
