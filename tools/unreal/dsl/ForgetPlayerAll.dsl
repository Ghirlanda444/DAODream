(fn ForgetPlayerAll ()
  (bind _all (Attore|GetAllActorsOfClass "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC_C"))
  (for _a _all
    (Classe|BPDlgNPC|ForgetThreat _a :Who (Gioco|GetPlayerPawn 0))))
