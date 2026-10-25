(fn PummelStun ()
  (Utilità|ControlloDiFlusso|Ramo (Classe|BPDlgNPC|OttieniDead (Variabili|Predefinito|OttieniBestTarget))
    (:then
      (Funzionedichiamata|AfterTalent :Txt (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTalentNames) (Variabili|Predefinito|OttieniTSlot))))
    (:else
      (Classe|BPDlgNPC|Stun (Variabili|Predefinito|OttieniBestTarget) :Seconds (Variabili|Predefinito|OttieniTSeconds) :PartySize (Variabili|Predefinito|OttieniPartySize))
      (Funzionedichiamata|AfterTalent :Txt (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniTalentNames) (Variabili|Predefinito|OttieniTSlot))))))
