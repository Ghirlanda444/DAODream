(fn TacAim ()
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Variabili|Predefinito|OttieniTacDone) (Utilità|IsValid (Variabili|Predefinito|OttieniTacWho)))
    (:then
      (Variabili|Predefinito|ImpostaTacOn (Variabili|Predefinito|OttieniTacWho))
      (Classe|BPPlotManager|TrFoeTest (Variabili|Predefinito|OttieniMgr) :A (Variabili|Predefinito|OttieniTacWho))
  (Utilità|ControlloDiFlusso|Ramo (Classe|BPPlotManager|OttieniBFoe (Variabili|Predefinito|OttieniMgr))
    (:then
      (Funzionedichiamata|TacRetarget))))))
