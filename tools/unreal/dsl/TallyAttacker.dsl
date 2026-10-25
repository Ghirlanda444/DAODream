(fn TallyAttacker (Npc Hostile)
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ANDBoolean (Matematica|Booleano|ANDBoolean (Classe|BPDlgNPC|OttieniHostile Npc) (Matematica|Booleano|NOTBoolean (Classe|BPDlgNPC|OttieniDead Npc))) (Matematica|Booleano|ANDBoolean (Utilità|IsValid (Classe|BPDlgNPC|OttieniFoe Npc)) (Matematica|Booleano|NOTBoolean (Utility|Operatori|Uguale(==) Npc Hostile))))
    (:then
      (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Uguale(==) (Classe|BPDlgNPC|OttieniFoe Npc) (Gioco|GetPlayerPawn 0))
        (:then
          (Variabili|Predefinito|ImpostaPlayerAttackers (Utility|Operatori|Aggiungi (Variabili|Predefinito|OttieniPlayerAttackers) 1)))
        (:else
          (Funzionedichiamata|AddAttackerTo :Foe (Classe|BPDlgNPC|OttieniFoe Npc)))))))
