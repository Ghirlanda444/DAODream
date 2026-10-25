(fn TalentCheck (Slot)
  (Funzionedichiamata|LoadTalent :Slot Slot)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Minore(<) (Utilità|Testo|GetGameTimeinSeconds) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTReady) Slot)) (Matematica|Booleano|NOTBoolean (Utility|Operatori|Maggiore(>) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTUntil) Slot) 0.0)))
    (:then
      (Funzionedichiamata|ShowMsg :Txt (Utilità|Stringa|Append (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTalentNames) Slot) " is not ready")))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Variabili|Predefinito|OttieniFeign) (Matematica|Booleano|NOTBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTId) 3023.0)))
        (:then
          (Funzionedichiamata|ShowMsg :Txt "Feigning death"))
        (:else
          (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTUse) 2.0)
            (:then
              (Funzionedichiamata|ToggleSustained))
            (:else
              (Funzionedichiamata|TryActivated))))))))
