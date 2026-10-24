(fn SetPlayerRules (InStats)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Utilità|Array|Length InStats) 10)
    (:then
      (Variabili|Predefinito|ImpostaPArmour (Utilità|Array|Ottieni(unacopia) InStats 6))
      (Variabili|Predefinito|ImpostaPPen (Utilità|Array|Ottieni(unacopia) InStats 7))
      (Variabili|Predefinito|ImpostaPCrit (Utilità|Array|Ottieni(unacopia) InStats 8))
      (Variabili|Predefinito|ImpostaPFlank (Utilità|Array|Ottieni(unacopia) InStats 9))
      (Variabili|Predefinito|ImpostaPBonus (Utilità|Array|Ottieni(unacopia) InStats 10)))))
