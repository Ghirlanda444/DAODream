LOOK = __LOOK__
sub = unreal.get_editor_subsystem(unreal.MetaHumanCharacterEditorSubsystem)
c = unreal.load_asset(LOOK["asset"])
if not sub.is_object_added_for_editing(c):
    raise RuntimeError("open the character in MetaHuman Creator first")
pc = sub.get_preview_collection(c)
inst = pc.default_instance
done = {}
for slot, values in LOOK["params"].items():
    sel = [s for s in inst.get_slot_selection_data() if str(s.selection.slot_name) == slot]
    if not sel:
        done[slot] = "no selection"
        continue
    key = sel[0].selection.selected_item
    ip = unreal.MetaHumanPaletteItemPath(item_key=key)
    for p in inst.get_instance_parameters(item_path=ip):
        n = str(p.name)
        if n in values:
            v = values[n]
            if isinstance(v, (list, tuple)):
                p.set_color(value=unreal.LinearColor(*v))
            else:
                p.set_float(value=float(v))
            done["%s.%s" % (slot, n)] = v
cons = sub.get_body_constraints(c)
for b in cons:
    n = str(b.name)
    if n in LOOK["body"]:
        b.is_active = True
        b.target_measurement = float(LOOK["body"][n])
sub.set_body_constraints(c, cons)
sub.commit_body_state(c)
done["body"] = LOOK["body"]
OUT["done"] = done
