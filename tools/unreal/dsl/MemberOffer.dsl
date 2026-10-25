(fn MemberOffer (Npc)
  (Variabili|Predefinito|ImpostaSelectCount (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniSelectCount) 1))
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Variabili|Predefinito|OttieniSelectCount) (Variabili|Predefinito|OttieniSelectWanted))
    (:then
      (Variabili|Predefinito|ImpostaSelected Npc)
      (Classe|BPDlgNPC|MakeOrderLine Npc)
      (Variabili|Predefinito|ImpostaSelName (Classe|BPDlgNPC|OttieniDisplayName Npc))
      (Variabili|Predefinito|ImpostaSelLine (Classe|BPDlgNPC|OttieniOrderLine Npc)))))
