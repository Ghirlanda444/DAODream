(fn GiveTalents ()
  (bind _pm (Attore|GetActorOfClass "/Game/Cousland/Plots/BP_PlotManager.BP_PlotManager_C"))
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid _pm)
    (:then
      (Classe|BPPlotManager|SetPlayerTalents _pm :InTalents (Variabili|Predefinito|OttieniPlayerTalents) :InPassives (Variabili|Predefinito|OttieniPlayerPassives) :InNames (Variabili|Predefinito|OttieniPlayerTalentNames))
      (Classe|BPPlotManager|SetPlayerTactics _pm :InTactics (Variabili|Predefinito|OttieniPlayerTactics)))))
