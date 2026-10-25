(fn AreaThreat (Amount bTaunt)
  (bind _all (Attore|GetAllActorsOfClass "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC_C"))
  (for _a _all
    (Classe|BPDlgNPC|TauntedBy _a :Who (Gioco|GetPlayerPawn 0) :Amount Amount :bTaunt bTaunt)))
