(fn WatchHit (Npc)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniLastHealth) 0.0) (Utility|Operatori|Minore(<) (Classe|BPDlgNPC|OttieniHealth Npc) (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniLastHealth) 0.01)))
    (:then
      (Animazione|Montaggio|PlaySlotAnimationasDynamicMontage :Asset "/Game/AnimalVarietyPack/Wolf/Animations/ANIM_Wolf_GetHitFront.ANIM_Wolf_GetHitFront" :SlotNodeName "DefaultSlot" :BlendInTime 0.05 :BlendOutTime 0.2 :InPlayRate 1.0))))
