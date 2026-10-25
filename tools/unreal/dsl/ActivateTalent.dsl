(fn ActivateTalent ()
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTId) 3041.0) (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTId) 3016.0))
    (:then
      (Funzionedichiamata|PayTalent)
      (Funzionedichiamata|AfterTalent :Txt (Utilità|Stringa|Append (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTalentNames) (Variabili|Predefinito|OttieniTSlot)) ": its threat comes with stage 4")))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTAtkBonus) 0.0) (Matematica|Booleano|NOTBoolean (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTId) 603.0)))
        (:then
          (Funzionedichiamata|PayTalent)
          (Utilità|Array|SetArrayElem (Variabili|Predefinito|OttieniTUntil) (Variabili|Predefinito|OttieniTSlot) (Utility|Operatori|Aggiungi (Utilità|Testo|GetGameTimeinSeconds) (Variabili|Predefinito|OttieniTSeconds)))
          (Funzionedichiamata|AfterTalent :Txt (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTalentNames) (Variabili|Predefinito|OttieniTSlot))))
        (:else
          (Funzionedichiamata|TargetTalent))))))
