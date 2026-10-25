(fn HitTalent ()
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniTId) 603.0)
    (:then
      (Classe|BPDlgNPC|Stun (Variabili|Predefinito|OttieniBestTarget) :Seconds (Variabili|Predefinito|OttieniTSeconds) :PartySize (Variabili|Predefinito|OttieniPartySize))
      (Funzionedichiamata|AfterTalent :Txt (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTalentNames) (Variabili|Predefinito|OttieniTSlot))))
    (:else
      (Funzionedichiamata|StrikeTalent))))
