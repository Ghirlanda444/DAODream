(fn MeleeAttack ()
  (Variabili|Predefinito|ImpostaBestDist 230.0)
  (Variabili|Predefinito|ImpostaBestTarget)
  (bind _all (Attore|GetAllActorsOfClass "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC_C"))
  (for _a _all
    (Classe|BPDlgNPC|Bid _a :InMgr (Variabili|Ottieniunriferimentoasestesso) :From (Gioco|GetPlayerPawn 0)))
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniBestTarget))
    (:then
      (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniOneShot)
        (:then
          (Classe|BPDlgNPC|TakeHit (Variabili|Predefinito|OttieniBestTarget) 100000.0))
        (:else
          (Classe|BPDlgNPC|TakeAttack (Variabili|Predefinito|OttieniBestTarget)))))))
