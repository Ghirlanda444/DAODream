(fn SelectRoute (What)
  (Utilità|ControlloDiFlusso|Ramo (Utilità|IsValid (Variabili|Predefinito|OttieniPickNpc))
    (:then
      (Utilità|ControlloDiFlusso|Ramo (Classe|BPDlgNPC|OttieniInParty (Variabili|Predefinito|OttieniPickNpc))
        (:then
          (Funzionedichiamata|SelectNpc :Npc (Variabili|Predefinito|OttieniPickNpc)))))
    (:else
      (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) What (Gioco|GetPlayerPawn 0))
        (:then
          (Funzionedichiamata|SelectMember :K 0))))))
