(fn EffBelt (K)
  (Funzionedichiamata|HitFoe :Bonus (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 16) 6)) :Mul 1.0 :bOff "false" :bSure "false")
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Classe|BPPlotManager|OttieniLastDamage (Variabili|Predefinito|OttieniMgr)) 0.0)
    (:then
      (Funzionedichiamata|LockFoe :Seconds (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 16) 7))))))
