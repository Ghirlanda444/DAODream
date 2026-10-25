(fn EffPin (K)
  (Funzionedichiamata|HitFoe :Bonus 0.0 :Mul 1.0 :bOff "false" :bSure "false")
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Classe|BPPlotManager|OttieniLastDamage (Variabili|Predefinito|OttieniMgr)) 0.0)
    (:then
      (Funzionedichiamata|RootFoe :Seconds (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 18) 7))))))
