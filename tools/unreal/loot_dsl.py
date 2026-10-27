"""python loot_dsl.py: writes dsl/loot/*.dsl, the graphs loot.py builds in: the original's treasure system (daotools
treasure.py, sys_treasure_h) rolled at runtime, the party's inventory and money, potions (by hand and by tactics),
containers, the bags fallen creatures leave, and the loot and inventory windows. Edit this, not the .dsl files."""
from pathlib import Path

from dslkit import (AND, F, NOT, NOW, OR, P, SELF, S, V, add, arr_add, branch, call, div, eq, ge, get, gt, le, length,
                    last, loop, lt, mul, randf, randi, self_, seli, sub, trunc, valid, Writer)

fn = Writer(Path(__file__).resolve().parent / "dsl" / "loot")
BOX_CLASS = "/Game/Cousland/Areas/BP_Container.BP_Container_C"
MONEY_KIND, HEALTH, MANA = 4.0, 1.0, 2.0
COOLDOWN = 5.0  # abi_base cooldown of the poultices and lyrium potions


def IS(item, n):  # ItemStats field n of catalogue item `item`: kind, ability, value, stack, power, base item
    return get(V("ItemStats"), add(mul(item, 6), n))


def box(field, b=V("LootBox")):
    return "(Classe|BPContainer|Ottieni%s %s)" % (field, b)


def ne(a, b):
    return NOT(eq(a, b))


def streq(a, b):
    return "(Utilità|Stringa|EqualExactly(String) %s %s)" % (a, b)


def append(*xs):
    out = xs[0]
    for x in xs[1:]:
        out = "(Utilità|Stringa|Append %s %s)" % (out, x)
    return out


def itos(x):
    return "(Utilità|Stringa|ToString(Integer) %s)" % x


def maxf(a, b):
    return "(Matematica|Float|Max(Float) %s %s)" % (a, b)


def minf(a, b):
    return "(Matematica|Float|Min(Float) %s %s)" % (a, b)


def maxi(a, b):
    return "(Matematica|Intero|Max(Integer) %s %s)" % (a, b)


def mini(a, b):
    return "(Matematica|Intero|Min(Integer) %s %s)" % (a, b)


def clear(a):
    return "(Utilità|Array|Clear %s)" % a


def setel(arr, i, x):
    return "(Utilità|Array|SetArrayElem %s %s %s)" % (arr, i, x)


def remove(arr, i):
    return "(Utilità|Array|RemoveIndex %s %s)" % (arr, i)


# --- the data ---------------------------------------------------------------------------------------------------
DATA = [("ItemTags", "InTags"), ("ItemNames", "InNames"), ("ItemDescs", "InDescs"), ("ItemStats", "InStats"),
        ("TRanges", "InRanges"), ("TRows", "InRows"), ("LBag", "InBag"), ("LRules", "InRules"),
        ("LReactive", "InReactive"), ("PLockpick", "InLockpick"), ("PSpell", "InSpell")]
fn("SetLootData", [p for _, p in DATA] + ["InPlayerItems"], *[S(v, p) for v, p in DATA],
   clear(V("Inv")), clear(V("InvN")), S("Money", 0),
   loop(sub(div(length("InPlayerItems"), 2), 1), call("PlayerItemOne", InPlayerItems="InPlayerItems", K="_index")))
fn("PlayerItemOne", ["InPlayerItems", "K"], call("InvAdd", Item=trunc(get("InPlayerItems", mul("K", 2))),
                                                 N=trunc(get("InPlayerItems", add(mul("K", 2), 1)))))

# --- the inventory: Inv (catalogue items) and InvN (counts); copper is Money ------------------------------------
fn("InvAdd", ["Item", "N"], branch(eq(IS("Item", 0), MONEY_KIND), [S("Money", add(V("Money"), "N"))],
                                   [call("InvFind", Item="Item"), call("InvAddGo", Item="Item", N="N")]))
fn("InvFind", ["Item"], S("InvAt", -1), loop(last(V("Inv")), call("InvFindOne", K="_index", Item="Item")))
fn("InvFindOne", ["K", "Item"], branch(AND(lt(V("InvAt"), 0), eq(get(V("Inv"), "K"), "Item")), [S("InvAt", "K")]))
fn("InvAddGo", ["Item", "N"], branch(ge(V("InvAt"), 0),
                                     [setel(V("InvN"), V("InvAt"), add(get(V("InvN"), V("InvAt")), "N"))],
                                     [arr_add(V("Inv"), "Item"), arr_add(V("InvN"), "N")]))
fn("InvTake", ["Slot", "N"], setel(V("InvN"), "Slot", sub(get(V("InvN"), "Slot"), "N")),
   branch(le(get(V("InvN"), "Slot"), 0), [remove(V("Inv"), "Slot"), remove(V("InvN"), "Slot")]))
fn("CountKind", ["Kind"], S("GH", 0), loop(last(V("Inv")), call("CountKindOne", K="_index", Kind="Kind")))
fn("CountKindOne", ["K", "Kind"], branch(eq(IS(get(V("Inv"), "K"), 0), "Kind"),
                                         [S("GH", add(V("GH"), get(V("InvN"), "K")))]))
# 100 bits a silver, 100 silver a gold
GOLD = div("Bits", 10000)
SILVER = sub(div("Bits", 100), mul(GOLD, 100))
BITS = sub("Bits", mul(div("Bits", 100), 100))
fn("MoneyText", ["Bits"], S("MText", append(itos(GOLD), '" gold, "', itos(SILVER), '" silver, "', itos(BITS), '" bits"')))

# --- TreasureGenerate (sys_treasure_h) into GItems, GCounts, GMoney ---------------------------------------------
GL = lambda n: get(V("GLoot"), n)  # treasure.LOOT_FIELDS
PLC = gt(GL(8), 0.5)
MONEY = lambda size: trunc(mul(mul(mul(mul(GL(7), GL(7)), 6.0), size), add(mul(randf(), 0.4), 0.8)))
fn("GenLoot", ["InLoot", "O", "BStart", "BCount", "bHost"],
   clear(V("GItems")), clear(V("GCounts")), clear(V("GEquip")), clear(V("GLoot")), S("GMoney", 0),
   S("GCarry", '"false"'), S("GHost", "bHost"),
   loop(8, call("GCopy", InLoot="InLoot", O="O", J="_index"),
        done=[call("GenBag", BStart="BStart", BCount="BCount"), call("GenReactive"), call("GenFirst"),
              call("GenDraws"), call("GenEquip")]))
fn("GCopy", ["InLoot", "O", "J"], branch(lt(add("O", "J"), length("InLoot")), [arr_add(V("GLoot"), get("InLoot", add("O", "J")))],
                                         [arr_add(V("GLoot"), 0.0)]))
fn("GenBag", ["BStart", "BCount"], loop(sub("BCount", 1), call("GenBagOne", K=add("BStart", "_index"))))
BAG = lambda n: get(V("LBag"), add(mul("K", 3), n))
fn("GenBagOne", ["K"], branch(eq(BAG(2), 2.0), [arr_add(V("GEquip"), trunc(BAG(0)))], [
    call("GAdd", Item=trunc(BAG(0)), N=trunc(BAG(1))),
    S("GCarry", OR(V("GCarry"), eq(IS(trunc(BAG(0)), 0), HEALTH), eq(IS(trunc(BAG(0)), 0), MANA)))]))
fn("GAdd", ["Item", "N"], S("GAt", -1), loop(last(V("GItems")), call("GFindOne", K="_index", Item="Item"),
                                              done=[call("GAddGo", Item="Item", N="N")]))
fn("GFindOne", ["K", "Item"], branch(AND(lt(V("GAt"), 0), eq(get(V("GItems"), "K"), "Item")), [S("GAt", "K")]))
fn("GAddGo", ["Item", "N"], branch(ge(V("GAt"), 0), [setel(V("GCounts"), V("GAt"), add(get(V("GCounts"), V("GAt")), "N"))],
                                   [arr_add(V("GItems"), "Item"), arr_add(V("GCounts"), "N")]))
# the reactive drops: a hostile carrying no potions, when the party holds few
fn("GenReactive", [], branch(AND(NOT(PLC), V("GHost"), NOT(V("GCarry")), gt(GL(5), 0.0)), [
    call("CountKind", Kind=HEALTH), S("GHc", V("GH")), call("CountKind", Kind=MANA), S("GMn", V("GH")),
    call("GenReact2")]))
LIM = get(V("LRules"), 0)
fn("GenReact2", [], branch(OR(lt(F(V("GHc")), LIM), lt(F(V("GMn")), LIM)), [
    S("GLim", maxf(LIM, 1.0)),
    S("GChance", mul(mul(div(add(mul(div(F(mini(V("GHc"), V("GMn"))), V("GLim")), -1.0), 1.0), 4.0), get(V("LRules"), 1)),
                     maxf(GL(2), 1.0))),
    branch(lt(randf(), V("GChance")), [call("GenReact3")])]))
fn("GenReact3", [],
   S("GTier", add(add(trunc(GL(5)), seli(1, 0, AND(ge(V("PLevel"), 10.0), lt(V("PLevel"), 15.0), lt(randf(), 0.5)))),
                  seli(1, 0, AND(ge(V("PLevel"), 15.0), lt(randf(), 0.75))))),
   S("GBool", gt(randf(), maxf(div(add(mul(div(F(V("GHc")), V("GLim")), -1.0), 1.0), 2.0), get(V("LRules"), 4)))),
   S("GIdx", add(sub(mini(maxi(V("GTier"), 1), 4), 1), seli(4, 0, V("GBool")))),
   branch(OR(AND(V("GBool"), lt(F(V("GMn")), LIM)), AND(NOT(V("GBool")), lt(F(V("GHc")), LIM))),
          [call("GAdd", Item=trunc(get(V("LReactive"), V("GIdx"))), N=1)]))
# a creature's 30% chance of copper when its table starts with it
fn("GenFirst", [], branch(AND(NOT(PLC), gt(GL(6), 0.0), le(randi(1, 100), get(V("LRules"), 2))),
                          [S("GMoney", add(V("GMoney"), MONEY(GL(6))))]))
# TS_GetItemNum: a fraction is a chance of one more; a container holds one at least
fn("GenDraws", [], S("GF", GL(2)), S("GN", 0), S("GNMax", trunc(GL(2))),
   loop(V("GNMax"), call("GenNumOne"), done=[call("GenDraws2")]))
fn("GenNumOne", [], branch(gt(V("GF"), 0.0), [
    S("GR", randf()), S("GN", seli(add(V("GN"), 1), V("GN"), le(V("GR"), V("GF")))),
    S("GF", sub(sub(V("GF"), self_(0, V("GR"), 0.0, le(V("GR"), V("GF")))), 1.0))]))
fn("GenDraws2", [], S("GN", seli(1, V("GN"), AND(PLC, lt(V("GN"), 1)))), loop(sub(V("GN"), 1), call("GenDrawOne")))
fn("GenDrawOne", [], branch(ge(GL(0), 0.0), [S("GTbl", trunc(self_(0, GL(1), GL(0), le(randf(), GL(3))))), call("GenDrawTbl")]))
TR = lambda n: get(V("TRanges"), add(mul(V("GTbl"), 2), n))
fn("GenDrawTbl", [], branch(AND(ge(V("GTbl"), 0), gt(TR(1), 0.0)), [
    S("GRow", add(trunc(TR(0)), randi(0, sub(trunc(TR(1)), 1)))),
    call("GenPut", Item=trunc(get(V("TRows"), mul(V("GRow"), 2))), Size=get(V("TRows"), add(mul(V("GRow"), 2), 1)))]))
# money and other treasure exclude each other on a creature
fn("GenPut", ["Item", "Size"], branch(eq(IS("Item", 0), MONEY_KIND),
                                      [branch(OR(PLC, eq(length(V("GItems")), 0)), [S("GMoney", add(V("GMoney"), MONEY("Size")))])],
                                      [branch(OR(PLC, eq(V("GMoney"), 0)), [call("GenStack", Size="Size"),
                                                                            call("GAdd", Item="Item", N=V("GSn"))])]))
fn("GenStack", ["Size"], S("GSf", add(mul(randf(), 0.2), 0.8)), S("GSn", maxi(1, trunc(mul(V("GSf"), "Size")))),
   S("GSn", seli(add(V("GSn"), 1), V("GSn"), lt(F(V("GSn")), mul("Size", V("GSf"))))),
   S("GSn", seli(1, V("GSn"), le("Size", 1.0))))
# TS_GenerateEquipment: one piece of its equipment, with the rank's chance, unless it dropped money
fn("GenEquip", [], branch(AND(NOT(PLC), eq(V("GMoney"), 0), gt(length(V("GEquip")), 0), le(randf(), GL(4))),
                          [call("GAdd", Item=get(V("GEquip"), randi(0, last(V("GEquip")))), N=1)]))

# --- drops: a fallen creature's loot in a bag where it fell ------------------------------------------------------
NPCF = lambda f, n="Npc": "(Classe|BPDlgNPC|Ottieni%s %s)" % (f, n)
fn("DropFor", ["Npc"], "(Funzionedichiamata|GenLoot :InLoot %s :O 0 :BStart %s :BCount %s :bHost %s)" % (
    NPCF("NLoot"), NPCF("NBagS"), NPCF("NBagN"), NPCF("Hostile")),
   branch(OR(gt(length(V("GItems")), 0), gt(V("GMoney"), 0)), [call("DropBag", Npc="Npc")]))
fn("DropBag", ["Npc"],
   '(bind _b (Gioco|Generaattoredallaclasse :Class "%s" :SpawnTransform (Matematica|Trasforma|MakeTransform '
   '(Trasformazione|GetActorLocation Npc))))' % BOX_CLASS,
   '(Classe|BPContainer|Setup _b :InLook 5 :InName %s :bLocked "false" :InLevel 0.0 :InKey "" :bKeyReq "false" :bUsable "true")'
   % append(NPCF("DisplayName"), '" (remains)"'),
   "(Classe|BPContainer|SetLoot _b :InItems %s :InCounts %s :InMoney %s)" % (V("GItems"), V("GCounts"), V("GMoney")))
# a container's at spawn (TreasureGenerate on spawn)
fn("FillBox", ["Box", "InLoot", "K", "BStart", "BCount"],
   call("GenLoot", InLoot="InLoot", O=mul("K", 9), BStart="BStart", BCount="BCount", bHost='"false"'),
   "(Classe|BPContainer|SetLoot Box :InItems %s :InCounts %s :InMoney %s)" % (V("GItems"), V("GCounts"), V("GMoney")))

# --- opening a container: its key, or a rogue's lockpicking (Placeable_HandleUsed) ------------------------------
fn("OpenBox", ["Box"], branch(box("Usable", "Box"), [branch(box("Locked", "Box"), [call("TryUnlock", Box="Box")],
                                                             [call("ShowLoot", Box="Box")])]))
fn("TryUnlock", ["Box"], S("GBool", '"false"'), loop(last(V("Inv")), call("KeyOne", K="_index", Box="Box"),
                                                    done=[call("TryUnlock2", Box="Box")]))
fn("KeyOne", ["K", "Box"], branch(AND(NOT(streq(box("KeyTag", "Box"), '""')),
                                     streq(get(V("ItemTags"), get(V("Inv"), "K")), box("KeyTag", "Box"))),
                                 [S("GBool", '"true"')]))
fn("TryUnlock2", ["Box"], branch(OR(V("GBool"), AND(NOT(box("KeyReq", "Box")), ge(V("PLockpick"), 0.0),
                                                    ge(V("PLockpick"), box("LockLevel", "Box")))),
                                 ["(Classe|BPContainer|Unlock Box)", call("ShowMsg", Txt='"Unlocked"'), call("ShowLoot", Box="Box")],
                                 [call("ShowMsg", Txt='(Utilità|Stringa|SelectString "Locked: it needs its key" "Locked: you have not the skill to pick it" %s)'
                                       % box("KeyReq", "Box"))]))

# --- the loot window --------------------------------------------------------------------------------------------
fn("LootMake", [], branch(valid(V("WLoot")), els=[
    '(bind _w (InterfacciaUtente|Creawidget "/Game/Cousland/Combat/WBP_Loot.WBP_Loot_C" (Gioco|GetPlayerController 0)))',
    "(bind _t (Utilità|Casting|CastToWBP_Loot _w))", S("WLoot", "_t")]))
fn("ShowLoot", ["Box"], S("LootBox", "Box"), call("LootMake"), call("CloseLootUI"),
   "(Interfacciautente|Viewport|AddtoViewport %s)" % V("WLoot"),
   "(Classe|WBPLoot|Open %s :InMgr %s :InBox Box)" % (V("WLoot"), SELF), S("LootOpen", '"true"'))
fn("CloseLootUI", [], branch(V("LootOpen"), ["(Widget|RemovefromParent %s)" % V("WLoot"), S("LootOpen", '"false"')]))
fn("CloseLoot", [], call("CloseLootUI"), call("BagGone"))
# a bag left empty goes (body bags vanish once emptied)
fn("BagGone", [], branch(valid(V("LootBox")), [branch(AND(eq(box("Look"), 5), eq(length(box("LItems")), 0), eq(box("LMoney"), 0)),
                                                       ["(Attore|DestroyActor %s)" % V("LootBox")])]))
fn("LootTake", ["K"], branch(lt("K", length(box("LItems"))), [
    call("InvAdd", Item=get(box("LItems"), "K"), N=get(box("LCounts"), "K")),
    call("ShowMsg", Txt=append('"Took "', get(V("ItemNames"), get(box("LItems"), "K")))),
    "(Classe|BPContainer|TakeOut %s :K K)" % V("LootBox")]))
fn("LootMoney", [], branch(gt(box("LMoney"), 0), [S("Money", add(V("Money"), box("LMoney"))),
                                                   "(Classe|BPContainer|TakeMoney %s)" % V("LootBox")]))
fn("LootAll", [], call("LootMoney"), S("GN", length(box("LItems"))),
   loop(sub(V("GN"), 1), call("LootTake", K=0), done=[call("CloseLoot")]))

# --- the inventory window and using an item -----------------------------------------------------------------------
fn("InvMake", [], branch(valid(V("WInv")), els=[
    '(bind _w (InterfacciaUtente|Creawidget "/Game/Cousland/Combat/WBP_Inventory.WBP_Inventory_C" (Gioco|GetPlayerController 0)))',
    "(bind _t (Utilità|Casting|CastToWBP_Inventory _w))", S("WInv", "_t")]))
fn("ToggleInventory", [], branch(V("InvOpen"), [call("CloseInv")], [call("OpenInv")]))
fn("OpenInv", [], branch(V("Talking"), els=[call("InvMake"), "(Interfacciautente|Viewport|AddtoViewport %s)" % V("WInv"),
                                            "(Classe|WBPInventory|Open %s :InMgr %s)" % (V("WInv"), SELF), S("InvOpen", '"true"')]))
fn("CloseInv", [], branch(V("InvOpen"), ["(Widget|RemovefromParent %s)" % V("WInv"), S("InvOpen", '"false"')]))
fn("UseFromInv", ["Slot"], call("TrCtrl"), call("UseItem", Who=V("TCtrl"), Slot="Slot"))
ITEM = get(V("Inv"), "Slot")
fn("UseItem", ["Who", "Slot"], branch(OR(eq(IS(ITEM, 0), HEALTH), eq(IS(ITEM, 0), MANA)), [
    call("CdCheck", Who="Who", Ab=IS(ITEM, 1)),
    branch(V("GBool"), [call("UseGo", Who="Who", Slot="Slot")], [call("ShowMsg", Txt='"Not ready yet"')])],
    [call("ShowMsg", Txt='"It cannot be used"')]))
fn("CdCheck", ["Who", "Ab"], S("GBool", '"true"'), loop(last(V("CdWho")), call("CdOne", K="_index", Who="Who", Ab="Ab")))
fn("CdOne", ["K", "Who", "Ab"], branch(AND(eq(get(V("CdWho"), "K"), "Who"), eq(get(V("CdAb"), "K"), "Ab"),
                                           gt(get(V("CdUntil"), "K"), NOW)), [S("GBool", '"false"')]))
fn("UseGo", ["Who", "Slot"], S("ItemK", ITEM), call("UseSP", Who="Who"),
   arr_add(V("CdWho"), "Who"), arr_add(V("CdAb"), IS(V("ItemK"), 1)), arr_add(V("CdUntil"), add(NOW, COOLDOWN)),
   call("InvTake", Slot="Slot", N=1), call("ShowMsg", Txt=get(V("ItemNames"), V("ItemK"))),
   branch(eq(IS(V("ItemK"), 0), HEALTH), [S("UseAmt", mul(add(V("UseSPv"), 50.0), IS(V("ItemK"), 4))), call("HealAny", Who="Who")],
          [call("ManaAny", Who="Who")]))
fn("UseSP", ["Who"], S("UseSPv", V("PSpell")), branch(eq("Who", P), els=[call("UseSPCast", A="Who")]))
fn("UseSPCast", ["A"], "(bind _n (Utilità|Casting|CastToBP_DlgNPC A))", S("UseSPv", "(Classe|BPDlgNPC|OttieniSpellPower _n)"))
fn("HealAny", ["Who"], branch(eq("Who", P), [call("HealPlayer", Amount=V("UseAmt"))], [call("HealAnyCast", A="Who")]))
fn("HealAnyCast", ["A"], "(bind _n (Utilità|Casting|CastToBP_DlgNPC A))", "(Classe|BPDlgNPC|GainHealth _n :Amount %s)" % V("UseAmt"))
# lyrium: mana to a magic user (class 2) only (item_singletarget)
fn("ManaAny", ["Who"], call("TrPeek", A="Who"), branch(eq(V("PkClass"), 2), [
    S("UseAmt", add(IS(V("ItemK"), 4), mul(V("UseSPv"), 0.5))),
    branch(eq("Who", P), [S("PStamina", minf(add(V("PStamina"), V("UseAmt")), V("PPool")))], [call("ManaCast", A="Who")])]))
fn("ManaCast", ["A"], "(bind _n (Utilità|Casting|CastToBP_DlgNPC A))", "(Classe|BPDlgNPC|GainStamina _n :Amount %s)" % V("UseAmt"))

# --- tactics: the potions (_AI_GetPotionByFilter) and Use item, in combat only -------------------------------------
fn("TacItem", ["Me", "Cmd", "Sub"], S("BF", '"false"'), branch(gt(length(V("EnAll")), 0), [call("TacItem2", Me="Me", Cmd="Cmd", Sub="Sub")]))
fn("TacItem2", ["Me", "Cmd", "Sub"], call("TrPeek", A="Me"), S("TIt", -1), S("GBest", 0.0),
   branch(AND(OR(eq("Cmd", 15.0), eq("Cmd", 16.0)), ge(V("PkHp"), V("PkMax"))), els=[
       loop(last(V("Inv")), call("TacItemOne", K="_index", Cmd="Cmd", Sub="Sub"), done=[call("TacItemUse", Me="Me")])]))
V_ = IS(get(V("Inv"), "K"), 2)
MOST = OR(eq("Cmd", 15.0), eq("Cmd", 17.0))
fn("TacItemOne", ["K", "Cmd", "Sub"], branch(eq("Cmd", 7.0), [
    branch(AND(lt(V("TIt"), 0), eq(IS(get(V("Inv"), "K"), 1), "Sub")), [S("TIt", "K")])], [
    branch(AND(eq(IS(get(V("Inv"), "K"), 0), self_(0, HEALTH, MANA, le("Cmd", 16.0))), gt(get(V("InvN"), "K"), 0),
               OR(AND(MOST, gt(V_, V("GBest"))), AND(NOT(MOST), OR(le(V_, V("GBest")), eq(V("GBest"), 0.0))))),
           [S("GBest", V_), S("TIt", "K")])]))
fn("TacItemUse", ["Me"], branch(ge(V("TIt"), 0), [call("CdCheck", Who="Me", Ab=IS(get(V("Inv"), V("TIt")), 1)),
                                                   branch(V("GBool"), [call("UseGo", Who="Me", Slot=V("TIt")), S("BF", '"true"')])]))

# --- BP_DlgNPC ----------------------------------------------------------------------------------------------------
fn("SetLootInfo", ["InLoot", "InBag", "K"], clear(V("NLoot")),
   branch(ge(length("InLoot"), mul(add("K", 1), 9)), [loop(8, call("LootOne", InLoot="InLoot", K="K", J="_index"))]),
   bp="NPC")
fn("LootOne", ["InLoot", "K", "J"], arr_add(V("NLoot"), get("InLoot", add(mul("K", 9), "J"))), bp="NPC")
fn("SetBagInfo", ["InBag", "K"], branch(ge(length("InBag"), mul(add("K", 1), 2)), [
    S("NBagS", trunc(get("InBag", mul("K", 2)))), S("NBagN", trunc(get("InBag", add(mul("K", 2), 1))))]), bp="NPC")
fn("DropLoot", [], branch(AND(NOT(V("InParty")), NOT(V("Dropped")), ge(length(V("NLoot")), 9)), [
    S("Dropped", '"true"'), "(Classe|BPPlotManager|DropFor %s :Npc %s)" % (V("Mgr"), SELF)]), bp="NPC")
fn("GainStamina", ["Amount"], S("NStamina", minf(add(V("NStamina"), "Amount"), V("NPool"))), bp="NPC")
fn("TacItemRow", ["Cmd", "Sub"], "(Classe|BPPlotManager|TacItem %s :Me %s :Cmd Cmd :Sub Sub)" % (V("Mgr"), SELF),
   branch("(Classe|BPPlotManager|OttieniBF %s)" % V("Mgr"), [S("TacDone", '"true"'), S("TacSlot", -2)]), bp="NPC")

# --- BP_Container -------------------------------------------------------------------------------------------------
fn("Setup", ["InLook", "InName", "bLocked", "InLevel", "InKey", "bKeyReq", "bUsable"],
   S("Look", "InLook"), S("CName", "InName"), S("Locked", "bLocked"), S("LockLevel", "InLevel"), S("KeyTag", "InKey"),
   S("KeyReq", "bKeyReq"), S("Usable", "bUsable"),
   "(bind _m (Attore|GetComponentbyClass %s \"/Script/Engine.StaticMeshComponent\"))" % SELF,
   "(bind _sm (Utilità|Casting|CastToStaticMeshComponent _m))",
   "(Componenti|StaticMesh|SetStaticMesh _sm %s)" % get(V("Meshes"), "InLook"),
   "(Trasformazione|SetRelativeScale3D _sm %s)" % get(V("Scales"), "InLook"), bp="BOX")
fn("SetLoot", ["InItems", "InCounts", "InMoney"], S("LItems", "InItems"), S("LCounts", "InCounts"), S("LMoney", "InMoney"), bp="BOX")
fn("TakeOut", ["K"], remove(V("LItems"), "K"), remove(V("LCounts"), "K"), bp="BOX")
fn("TakeMoney", [], S("LMoney", 0), bp="BOX")
fn("Unlock", [], S("Locked", '"false"'), bp="BOX")

# --- BP_AreaLoader: the data, the creatures' share, the containers ------------------------------------------------
AL_DATA = [("InTags", "ItemTags"), ("InNames", "ItemNames"), ("InDescs", "ItemDescs"), ("InStats", "ItemStats"),
           ("InRanges", "TreasureRanges"), ("InRows", "TreasureRows"), ("InBag", "Bag"), ("InRules", "LootRules"),
           ("InReactive", "ReactivePotions"), ("InLockpick", "PlayerLockpick"), ("InSpell", "PlayerSpellPower"),
           ("InPlayerItems", "PlayerItems")]
fn("GiveLoot", [], '(bind _pm (Attore|GetActorOfClass "/Game/Cousland/Plots/BP_PlotManager.BP_PlotManager_C"))',
   branch(valid("_pm"), ["(Classe|BPPlotManager|SetLootData _pm%s)" % "".join(" :%s %s" % (p, V(v)) for p, v in AL_DATA),
                         loop(last(V("ContainerTags")), call("BoxOne", K="_index", Pm="_pm"))]), bp="AL")
CP = lambda n: get(V("ContainerPose"), add(mul("K", 4), n))
CI = lambda n: get(V("ContainerInfo"), add(mul("K", 6), n))
fn("BoxOne", ["K", "Pm"], branch(gt(CI(5), 0.5), [
    '(bind _b (Gioco|Generaattoredallaclasse :Class "%s" :SpawnTransform (Matematica|Trasforma|MakeTransform '
    '(Matematica|Vettore|MakeVector %s %s %s) (Matematica|Rotatore|MakeRotator 0.0 0.0 %s))))' % (BOX_CLASS, CP(0), CP(1), CP(2), CP(3)),
    '(Classe|BPContainer|Setup _b :InLook %s :InName %s :bLocked %s :InLevel %s :InKey %s :bKeyReq %s :bUsable %s)' % (
        trunc(CI(0)), get(V("ContainerNames"), "K"), gt(CI(1), 0.5), CI(2), get(V("ContainerKeys"), "K"), gt(CI(3), 0.5),
        gt(CI(4), 0.5)),
    "(Classe|BPPlotManager|FillBox Pm :Box _b :InLoot %s :K K :BStart %s :BCount %s)" % (
        V("ContainerLoot"), trunc(get(V("ContainerBag"), mul("K", 2))), trunc(get(V("ContainerBag"), add(mul("K", 2), 1))))]),
   bp="AL")

# --- WBP_Loot: what a container or a bag holds; take one, the money, or all ----------------------------------------
LOOT_ROWS, INV_ROWS = 12, 20


def W(n):  # a widget of the tree
    return "(Variabili|%s|Ottieni%s)" % ("%s", n)


def text(widget, s):
    return "(Widget|SetText(Text) %s (Utilità|Testo|ToText(String) %s))" % (widget, s)


def vis(widget, on):
    return '(Widget|SetVisibility %s "%s")' % (widget, "Visible" if on else "Collapsed")


WL = lambda n: "(Variabili|WBP_Loot|Ottieni%s)" % n
WI = lambda n: "(Variabili|WBP_Inventory|Ottieni%s)" % n
MG = V("Mgr")
PMG = lambda f: "(Classe|BPPlotManager|Ottieni%s %s)" % (f, MG)
BX = lambda f: "(Classe|BPContainer|Ottieni%s %s)" % (f, V("Box"))
fn("Collect", [], *["(Utilità|Array|Add %s %s)" % (V(a), WL("%s%d" % (w, k))) for k in range(LOOT_ROWS)
                    for a, w in (("ItTs", "ItT"), ("ItBs", "It"))], bp="WLOOT")
fn("Open", ["InMgr", "InBox"], S("Mgr", "InMgr"), S("Box", "InBox"), call("CollectOnce"), call("Redraw"), bp="WLOOT")
fn("CollectOnce", [], branch(eq(length(V("ItTs")), 0), [call("Collect")]), bp="WLOOT")
fn("Redraw", [], text(WL("Title"), BX("CName")),
   "(Classe|BPPlotManager|MoneyText %s :Bits %s)" % (MG, BX("LMoney")),
   text(WL("MoneyT"), '(Utilità|Stringa|SelectString (Utilità|Stringa|Append "Money: " %s) "No money" %s)' % (PMG("MText"), gt(BX("LMoney"), 0))),
   loop(LOOT_ROWS - 1, call("DrawIt", K="_index")), bp="WLOOT")
fn("DrawIt", ["K"], branch(lt("K", length(BX("LItems"))), [
    vis(get(V("ItBs"), "K"), True),
    text(get(V("ItTs"), "K"), '(Utilità|Stringa|Append (Utilità|Stringa|Append %s " x") (Utilità|Stringa|ToString(Integer) %s))' % (
        get(PMG("ItemNames"), get(BX("LItems"), "K")), get(BX("LCounts"), "K")))], [vis(get(V("ItBs"), "K"), False)]), bp="WLOOT")
fn("ClickIt", ["K"], "(Classe|BPPlotManager|LootTake %s :K K)" % MG, call("Redraw"), bp="WLOOT")
fn("ClickMoney", [], "(Classe|BPPlotManager|LootMoney %s)" % MG, call("Redraw"), bp="WLOOT")
fn("ClickAll", [], "(Classe|BPPlotManager|LootAll %s)" % MG, bp="WLOOT")
fn("ClickClose", [], "(Classe|BPPlotManager|CloseLoot %s)" % MG, bp="WLOOT")

# --- WBP_Inventory: the party's items and money; a potion used on the one in control -----------------------------
INVI = lambda k: get(PMG("Inv"), k)
ISW = lambda item, n: get(PMG("ItemStats"), add(mul(item, 6), n))
fn("Collect", [], *["(Utilità|Array|Add %s %s)" % (V(a), WI("%s%d" % (w, k))) for k in range(INV_ROWS)
                    for a, w in (("RowTs", "RowT"), ("RowBs", "Row"))], bp="WINV")
fn("Open", ["InMgr"], S("Mgr", "InMgr"), call("CollectOnce"), call("Redraw"), bp="WINV")
fn("CollectOnce", [], branch(eq(length(V("RowTs")), 0), [call("Collect")]), bp="WINV")
fn("Redraw", [], "(Classe|BPPlotManager|MoneyText %s :Bits %s)" % (MG, PMG("Money")),
   text(WI("MoneyT"), PMG("MText")), loop(INV_ROWS - 1, call("DrawRow", K="_index")), bp="WINV")
USABLE = lambda item: OR(eq(ISW(item, 0), 1.0), eq(ISW(item, 0), 2.0))
fn("DrawRow", ["K"], branch(lt("K", length(PMG("Inv"))), [
    vis(get(V("RowBs"), "K"), True),
    text(get(V("RowTs"), "K"), '(Utilità|Stringa|Append (Utilità|Stringa|Append (Utilità|Stringa|Append %s " x") (Utilità|Stringa|ToString(Integer) %s)) (Utilità|Stringa|SelectString "   (click to use)" "" %s))' % (
        get(PMG("ItemNames"), INVI("K")), get(PMG("InvN"), "K"), USABLE(INVI("K"))))], [vis(get(V("RowBs"), "K"), False)]),
   bp="WINV")
fn("ClickRow", ["K"], branch(lt("K", length(PMG("Inv"))), [
    text(WI("Desc"), get(PMG("ItemDescs"), INVI("K"))),
    branch(USABLE(INVI("K")), ["(Classe|BPPlotManager|UseFromInv %s :Slot K)" % MG, call("Redraw")])]), bp="WINV")
fn("ClickClose", [], "(Classe|BPPlotManager|CloseInv %s)" % MG, bp="WINV")

if __name__ == "__main__":
    print(len(fn.wrote), "graphs")
