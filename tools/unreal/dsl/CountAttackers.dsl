(fn CountAttackers (Hostile)
  (Variabili|Predefinito|ImpostaPlayerAttackers 0)
  (bind _all (Attore|GetAllActorsOfClass "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC_C"))
  (for _a _all
    (Classe|BPDlgNPC|ClearAttackers _a))
  (for _b _all
    (Funzionedichiamata|TallyAttacker :Npc _b :Hostile Hostile)))
