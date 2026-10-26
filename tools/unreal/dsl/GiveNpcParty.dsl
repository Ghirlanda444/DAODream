(fn GiveNpcParty (Npc K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) K (Utilità|Array|Length (Variabili|Predefinito|OttieniNpcTacticSlots)))
    (:then
      (Classe|BPDlgNPC|SetPartyTactics Npc :InTactics (Variabili|Predefinito|OttieniNpcPartyTactics) :K K :Slots (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNpcTacticSlots) K)))))
