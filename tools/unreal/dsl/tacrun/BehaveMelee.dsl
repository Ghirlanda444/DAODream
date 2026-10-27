(fn BehaveMelee ()
  (Funzionedichiamata|NFlag :Fl 6)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ANDBoolean (Variabili|Predefinito|OttieniBFlag) (Utility|Operatori|Maggiore(>) (Classe|BPPlotManager|OttieniRingN (Variabili|Predefinito|OttieniMgr)) 0)) (Utility|Operatori|Maggiore(>) (Utilità|Array|Length (Classe|BPPlotManager|OttieniEnL (Variabili|Predefinito|OttieniMgr))) 0))
    (:then
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minoreuguale(<=) (Utilità|Array|Ottieni(unacopia) (Classe|BPPlotManager|OttieniEnD (Variabili|Predefinito|OttieniMgr)) 0) 250.0)
    (:then
      (Funzionedichiamata|BackAway :From (Utilità|Array|Ottieni(unacopia) (Classe|BPPlotManager|OttieniEnL (Variabili|Predefinito|OttieniMgr)) 0)))))))
