(fn UseTalent (Slot)
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniSelected))
    (:then
      (Funzionedichiamata|OrderTalent :Slot Slot))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Variabili|Predefinito|OttieniPaused)
        (:then
          (Variabili|Predefinito|ImpostaQueuedSlot (Utility|Operatori|Aggiungi Slot 1))
          (Funzionedichiamata|ShowMsg :Txt "Paused: talent queued"))
        (:else
          (Funzionedichiamata|UseTalentNow :Slot Slot))))))
