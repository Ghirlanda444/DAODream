(fn EffOverwhelm (K)
  (Classe|BPPlotManager|CheckBeast (Variabili|Predefinito|OttieniMgr) :Who (Variabili|Predefinito|OttieniFoe))
  (Utilità|ControlloDiFlusso|Ramo (Classe|BPPlotManager|OttieniBeastFoe (Variabili|Predefinito|OttieniMgr))
    (:then
      (Funzionedichiamata|StrikeFoe))
    (:else
      (Funzionedichiamata|OverwhelmHold :K K))))
