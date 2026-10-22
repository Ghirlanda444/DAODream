(fn WatchNpc ()
  (bind _npc (Utilità|Casting|CastToBP_DlgNPC (Attore|GetAttachParentActor (Animazione|GetOwningActor))))
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid _npc)
    (:then
      (Funzionedichiamata|WatchBite :Npc _npc)
      (Funzionedichiamata|WatchHit :Npc _npc)
      (Variabili|Predefinito|ImpostaLastAttack (Classe|BPDlgNPC|OttieniAttackTimer _npc))
      (Variabili|Predefinito|ImpostaLastHealth (Classe|BPDlgNPC|OttieniHealth _npc)))))
