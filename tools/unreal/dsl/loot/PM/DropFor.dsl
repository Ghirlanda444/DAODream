(fn DropFor (Npc)
  (Funzionedichiamata|GenLoot :InLoot (Classe|BPDlgNPC|OttieniNLoot Npc) :O 0 :BStart (Classe|BPDlgNPC|OttieniNBagS Npc) :BCount (Classe|BPDlgNPC|OttieniNBagN Npc) :bHost (Classe|BPDlgNPC|OttieniHostile Npc))
  (Utilità|ControlloDiFlusso|Ramo (Matematica|Booleano|ORBoolean (Utility|Operatori|Maggiore(>) (Utilità|Array|Length (Variabili|Predefinito|OttieniGItems)) 0) (Utility|Operatori|Maggiore(>) (Variabili|Predefinito|OttieniGMoney) 0))
    (:then
      (Funzionedichiamata|DropBag :Npc Npc))))
