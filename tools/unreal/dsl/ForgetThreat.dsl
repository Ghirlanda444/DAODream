(fn ForgetThreat (Who)
  (Variabili|Predefinito|ImpostaTIdx (Utilità|Array|FindItem (Variabili|Predefinito|OttieniThreatWho) Who))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Maggioreuguale(>=) (Variabili|Predefinito|OttieniTIdx) 0)
    (:then
      (Utilità|Array|RemoveIndex (Variabili|Predefinito|OttieniThreatWho) (Variabili|Predefinito|OttieniTIdx))
      (Utilità|Array|RemoveIndex (Variabili|Predefinito|OttieniThreatVal) (Variabili|Predefinito|OttieniTIdx))
      (Funzionedichiamata|ForgetFoe :Who Who))))
