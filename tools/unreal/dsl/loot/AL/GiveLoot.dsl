(fn GiveLoot ()
  (bind _pm (Attore|GetActorOfClass "/Game/Cousland/Plots/BP_PlotManager.BP_PlotManager_C"))
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid _pm)
    (:then
      (Classe|BPPlotManager|SetLootData _pm :InTags (Variabili|Predefinito|OttieniItemTags) :InNames (Variabili|Predefinito|OttieniItemNames) :InDescs (Variabili|Predefinito|OttieniItemDescs) :InStats (Variabili|Predefinito|OttieniItemStats) :InRanges (Variabili|Predefinito|OttieniTreasureRanges) :InRows (Variabili|Predefinito|OttieniTreasureRows) :InBag (Variabili|Predefinito|OttieniBag) :InRules (Variabili|Predefinito|OttieniLootRules) :InReactive (Variabili|Predefinito|OttieniReactivePotions) :InLockpick (Variabili|Predefinito|OttieniPlayerLockpick) :InSpell (Variabili|Predefinito|OttieniPlayerSpellPower) :InPlayerItems (Variabili|Predefinito|OttieniPlayerItems))
  (Utilities|FlowControl|ForLoop :FirstIndex 0 :LastIndex (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniContainerTags)) 1)
    (:LoopBody
      (Funzionedichiamata|BoxOne :K _index :Pm _pm))))))
