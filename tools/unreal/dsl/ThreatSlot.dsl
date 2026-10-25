(fn ThreatSlot (Who)
  (Variabili|Predefinito|ImpostaTIdx (Utilità|Array|FindItem (Variabili|Predefinito|OttieniThreatWho) Who))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) (Variabili|Predefinito|OttieniTIdx) 0)
    (:then
      (Utilità|Array|Add (Variabili|Predefinito|OttieniThreatWho) Who)
      (Utilità|Array|Add (Variabili|Predefinito|OttieniThreatVal) 0.0)
      (Variabili|Predefinito|ImpostaTIdx (Utility|Operatori|Sottrai (Utilità|Array|Length (Variabili|Predefinito|OttieniThreatWho)) 1)))))
