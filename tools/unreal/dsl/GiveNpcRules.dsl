(fn GiveNpcRules (Npc K)
  (Classe|BPDlgNPC|SetRules Npc :InRules (Variabili|Predefinito|OttieniNpcRules) :K (Utility|Operatori|Moltiplica K 5))
  (Classe|BPDlgNPC|SetStatus Npc :InStatus (Variabili|Predefinito|OttieniNpcStatus) :K (Utility|Operatori|Moltiplica K 11))
  (Classe|BPDlgNPC|SetNpcTalents Npc :InTalents (Variabili|Predefinito|OttieniNpcTalents) :InTactics (Variabili|Predefinito|OttieniNpcTactics) :K K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) K (Utilità|Array|Length (Variabili|Predefinito|OttieniNpcInterval)))
    (:then
      (Classe|BPDlgNPC|SetInterval Npc :InInterval (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNpcInterval) K)))))
