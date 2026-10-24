(fn StageNpc (Tag Loc Rot)
  (bind _a (Attore|GetAllActorsOfClassWithTag :ActorClass "/Game/Cousland/Dialogue/BP_DlgNPC.BP_DlgNPC_C" :Tag (Utilità|Stringa|StringToName Tag)))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Utilità|Array|Length _a) 0)
    (:then (Trasformazione|SetActorLocationAndRotation (Utilità|Array|Ottieni(unacopia) _a 0) Loc Rot "false" "true"))))
