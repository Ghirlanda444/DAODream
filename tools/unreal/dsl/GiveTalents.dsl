(fn GiveTalents ()
  (bind _pm (Attore|GetActorOfClass "/Game/Cousland/Plots/BP_PlotManager.BP_PlotManager_C"))
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid _pm)
    (:then
      (Classe|BPPlotManager|SetPlayerTalents _pm :InTalents (Variabili|Predefinito|OttieniPlayerTalents) :InPassives (Variabili|Predefinito|OttieniPlayerPassives) :InNames (Variabili|Predefinito|OttieniPlayerTalentNames))
      (Classe|BPPlotManager|SetPlayerTactics _pm :InTactics (Variabili|Predefinito|OttieniPlayerTactics))
      (Classe|BPPlotManager|SetTacticMenu _pm :InTargets (Variabili|Predefinito|OttieniTacticTargets) :InTargetNames (Variabili|Predefinito|OttieniTacticTargetNames) :InBases (Variabili|Predefinito|OttieniTacticBases) :InBaseNames (Variabili|Predefinito|OttieniTacticBaseNames) :InConds (Variabili|Predefinito|OttieniTacticConds) :InCondNames (Variabili|Predefinito|OttieniTacticCondNames) :InCommandNames (Variabili|Predefinito|OttieniTacticCommandNames) :InSlots (Variabili|Predefinito|OttieniPlayerTacticSlots)))))
