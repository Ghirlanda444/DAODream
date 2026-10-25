(fn TalentAfterHit ()
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniLastDamage) 0.0) (Matematica|Booleano|NOTBoolean (Classe|BPDlgNPC|OttieniDead (Variabili|Predefinito|OttieniBestTarget))))
    (:then
      (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTId) 617.0)
        (:then
          (Classe|BPDlgNPC|Knock (Variabili|Predefinito|OttieniBestTarget) :Seconds (Variabili|Predefinito|OttieniTSeconds))
          (Funzionedichiamata|AfterTalent :Txt (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTalentNames) (Variabili|Predefinito|OttieniTSlot))))
        (:else
          (Classe|BPDlgNPC|Slow (Variabili|Predefinito|OttieniBestTarget) :Seconds (Variabili|Predefinito|OttieniTSeconds) :PartySize (Variabili|Predefinito|OttieniPartySize))
          (Funzionedichiamata|AfterTalent :Txt (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTalentNames) (Variabili|Predefinito|OttieniTSlot))))))
    (:else
      (Funzionedichiamata|AfterTalent :Txt (Utilità|Stringa|Append (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTalentNames) (Variabili|Predefinito|OttieniTSlot)) ": no hit")))))
