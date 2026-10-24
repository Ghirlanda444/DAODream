(fn SetRules (InRules K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Utilità|Array|Length InRules) (Utility|Operatori|Aggiungi K 4))
    (:then
      (Variabili|Predefinito|ImpostaArmour (Utilità|Array|Ottieni(unacopia) InRules K))
      (Variabili|Predefinito|ImpostaPen (Utilità|Array|Ottieni(unacopia) InRules (Utility|Operatori|Aggiungi K 1)))
      (Variabili|Predefinito|ImpostaCrit (Utilità|Array|Ottieni(unacopia) InRules (Utility|Operatori|Aggiungi K 2)))
      (Variabili|Predefinito|ImpostaFlank (Utilità|Array|Ottieni(unacopia) InRules (Utility|Operatori|Aggiungi K 3)))
      (Variabili|Predefinito|ImpostaDmgBonus (Utilità|Array|Ottieni(unacopia) InRules (Utility|Operatori|Aggiungi K 4))))))
