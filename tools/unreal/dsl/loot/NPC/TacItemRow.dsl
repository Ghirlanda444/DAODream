(fn TacItemRow (Cmd Sub)
  (Classe|BPPlotManager|TacItem (Variabili|Predefinito|OttieniMgr) :Me (Variabili|Ottieniunriferimentoasestesso) :Cmd Cmd :Sub Sub)
  (Utilità|ControlloDiFlusso|Ramo (Classe|BPPlotManager|OttieniBF (Variabili|Predefinito|OttieniMgr))
    (:then
      (Variabili|Predefinito|ImpostaTacDone "true")
      (Variabili|Predefinito|ImpostaTacSlot -2))))
