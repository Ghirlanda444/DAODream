(fn WatchBite (Npc)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Classe|BPDlgNPC|OttieniAttackTimer Npc) (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniLastAttack) 0.5))
    (:then
      (Animazione|Montaggio|PlaySlotAnimationasDynamicMontage :Asset "/Game/AnimalVarietyPack/Wolf/Animations/ANIM_Wolf_Bite.ANIM_Wolf_Bite" :SlotNodeName "DefaultSlot" :BlendInTime 0.1 :BlendOutTime 0.2 :InPlayRate 1.2))))
