(fn TalentCheck (Slot)
  (Funzionedichiamata|LoadTalent :Slot Slot)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) (Utilità|Testo|GetGameTimeinSeconds) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTReady) Slot))
    (:then
      (Funzionedichiamata|ShowMsg :Txt (Utilità|Stringa|Append (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTalentNames) Slot) " is not ready")))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTUse) 2.0)
        (:then
          (Funzionedichiamata|ToggleSustained))
        (:else
          (Funzionedichiamata|TryActivated))))))
