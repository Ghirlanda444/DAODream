(fn GiveNpcAlly (Npc K)
  (Funzionedichiamata|GiveNpcRules :Npc Npc :K K)
  (Funzionedichiamata|GiveNpcImmortal :Npc Npc :K K)
  (Funzionedichiamata|GiveNpcParty :Npc Npc :K K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) K (Utilità|Array|Length (Variabili|Predefinito|OttieniNpcAlly)))
    (:then
      (Classe|BPDlgNPC|SetAlly Npc (Utility|Operatori|Uguale(==) (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNpcAlly) K) 1)))))
