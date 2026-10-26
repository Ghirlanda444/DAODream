(fn ListMembers ()
  (Utilità|Array|Clear (Variabili|Predefinito|OttieniMembers))
  (bind _all (Attore|GetAllActorsOfClass "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC_C"))
  (for _a _all
    (Funzionedichiamata|MemberOffer :A _a)))
