"""
Correções não-destrutivas de bugs do projeto.py original (nunca alteram o
arquivo original, só o objeto já construído na cena).
"""
import bpy
import bmesh


def fix_pool_boolean():
    """A face de topo de Piscina_Esmeralda_Casca fica exatamente coplanar
    (z=0) com Piso_Area_Piscina. Isso faz o modificador Boolean gerar uma
    face com índice de material inválido, renderizada como preto sólido
    cobrindo toda a piscina. Corrige usando uma cópia elevada como cortador
    e removendo a face de topo da casca original (revela a lâmina d'água)."""
    casca_original = bpy.data.objects.get("Piscina_Esmeralda_Casca")
    if not casca_original:
        return
    chao_piscina_obj = bpy.data.objects["Piso_Area_Piscina"]
    mod_bool = chao_piscina_obj.modifiers["Corte_Piscina"]

    cutter_mesh = casca_original.data.copy()
    cutter_obj = bpy.data.objects.new("Piscina_Cortador_Boolean", cutter_mesh)
    bpy.context.collection.objects.link(cutter_obj)
    cutter_obj.matrix_world = casca_original.matrix_world.copy()
    cutter_obj.location.z += 0.03
    cutter_obj.hide_render = True
    mod_bool.object = cutter_obj

    bpy.context.view_layer.objects.active = casca_original
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(casca_original.data)
    bm.faces.ensure_lookup_table()
    face_topo = max(bm.faces, key=lambda f: f.calc_center_median().z)
    bmesh.ops.delete(bm, geom=[face_topo], context='FACES_ONLY')
    bmesh.update_edit_mesh(casca_original.data)
    bpy.ops.object.mode_set(mode='OBJECT')


def fix_piso_quiosque_seam():
    """Piso_Quiosque_L é formado por 2 blocos sólidos independentes
    (horizontal + vertical) que se sobrepõem sem solda de vértices no
    encontro em L, deixando uma face interna nunca iluminada (aparece como
    um triângulo preto). Soldar vértices coincidentes resolve."""
    piso = bpy.data.objects.get("Piso_Quiosque_L")
    if not piso:
        return
    bpy.context.view_layer.objects.active = piso
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(piso.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.001)
    bmesh.update_edit_mesh(piso.data)
    bpy.ops.object.mode_set(mode='OBJECT')


def apply_all():
    fix_pool_boolean()
    fix_piso_quiosque_seam()
