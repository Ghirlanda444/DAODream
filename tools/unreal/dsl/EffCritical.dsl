(fn EffCritical (K)
  (Funzionedichiamata|ReadFoe)
  (Funzionedichiamata|HitFoe :Bonus 0.0 :Mul 1.0 :bOff "false" :bSure "false")
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Maggiore(>) (Classe|BPPlotManager|OttieniLastDamage (Variabili|Predefinito|OttieniMgr)) 0.0) (Utility|Operatori|Minoreuguale(<=) (Variabili|Predefinito|OttieniFoeHp) 25.0))
    (:then
      (Funzionedichiamata|KillFoe))))
