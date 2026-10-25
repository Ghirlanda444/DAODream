(fn OrderTalent (Slot)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Minore(<) (Utility|Operatori|Moltiplica Slot 18) (Utilità|Array|Length (Variabili|Predefinito|OttieniNTalents))) (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNTalents) (Utility|Operatori|Moltiplica Slot 18)) 0.0))
    (:then
      (Variabili|Predefinito|ImpostaPendingSlot (Utility|Operatori|Aggiungi Slot 1))
      (Funzionedichiamata|NameOf :K Slot)
      (Variabili|Predefinito|ImpostaOrderMsg (Utilità|Stringa|Append ": " (Variabili|Predefinito|OttieniTName))))
    (:else
      (Variabili|Predefinito|ImpostaOrderMsg ": no such talent"))))
