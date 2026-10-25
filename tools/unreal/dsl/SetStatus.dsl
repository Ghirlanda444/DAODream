(fn SetStatus (InStatus K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggiore(>) (Utilità|Array|Length InStatus) (Utility|Operatori|Aggiungi K 2))
    (:then
      (Variabili|Predefinito|ImpostaNLevel (Utilità|Array|Ottieni(unacopia) InStatus K))
      (Variabili|Predefinito|ImpostaDurScale (Utilità|Array|Ottieni(unacopia) InStatus (Utility|Operatori|Aggiungi K 1)))
      (Variabili|Predefinito|ImpostaResist (Utilità|Array|Ottieni(unacopia) InStatus (Utility|Operatori|Aggiungi K 2))))))
