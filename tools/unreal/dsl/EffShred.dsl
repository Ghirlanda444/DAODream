(fn EffShred (K)
  (Variabili|Predefinito|ImpostaNOwnCrit (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniNOwnCrit) 1000.0))
  (Funzionedichiamata|HitFoe :Bonus (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 18) 6)) :Mul 1.0 :bOff "false" :bSure "false")
  (Variabili|Predefinito|ImpostaNOwnCrit (Utility|Operatori|Sottrai (Variabili|Predefinito|OttieniNOwnCrit) 1000.0))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Classe|BPPlotManager|OttieniLastDamage (Variabili|Predefinito|OttieniMgr)) 0.0)
    (:then
      (Funzionedichiamata|BleedFoe :Amount (Classe|BPPlotManager|OttieniLastDamage (Variabili|Predefinito|OttieniMgr)) :Seconds (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 18) 7))))))
