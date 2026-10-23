(fn GiveNpcLook (Npc K)
  (Utilità|ControlloDiFlusso|Ramo (Utility|Operatori|Minore(<) K (Utilità|Array|Length (Variabili|Predefinito|OttieniNpcCrowd)))
    (:then
      (Classe|BPDlgNPC|ApplyLook Npc (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNpcMorph) K))
      (Classe|BPDlgNPC|ApplyLook Npc (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNpcCrowd) K))
      (Classe|BPDlgNPC|ApplyOutfit Npc (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNpcChest) K))
      (Classe|BPDlgNPC|ApplyHelmet Npc (Utilità|Array|Ottieni(unacopia) (Variabili|Predefinito|OttieniNpcHelmet) K))
      (Classe|BPDlgNPC|ApplyVariety Npc (Variabili|Predefinito|OttieniNpcVariety) (Utility|Operatori|Moltiplica K 11)))))
