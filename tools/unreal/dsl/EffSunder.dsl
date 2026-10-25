(fn EffSunder (K)
  (Funzionedichiamata|HitFoe :Bonus 0.0 :Mul (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 18) 15)) :bOff "false" :bSure "false")
  (Funzionedichiamata|HitFoe :Bonus 0.0 :Mul (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 18) 15)) :bOff "false" :bSure "false")
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Maggiore(>) (Classe|BPPlotManager|OttieniLastDamage (Variabili|Predefinito|OttieniMgr)) 0.0) (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 18) 0)) 3025.0))
    (:then
      (Funzionedichiamata|DisarmFoe :Seconds (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Aggiungi (Utility|Operatori|Moltiplica K 18) 7))))))
